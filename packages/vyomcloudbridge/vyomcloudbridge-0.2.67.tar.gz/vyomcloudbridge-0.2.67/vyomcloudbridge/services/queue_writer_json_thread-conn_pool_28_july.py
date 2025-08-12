# vyomcloudbridge/queue_writer_json.py
from concurrent.futures import ThreadPoolExecutor
import time
import random
from datetime import datetime, timezone
import configparser
import traceback
import os
import signal
import sys
import hashlib
import base64
from typing import Dict, Any, Optional
import json
from typing import Dict, Any, List, Tuple, Union
from pathlib import Path
import threading
from vyomcloudbridge.services.chunk_merger import ChunkMerger

# from vyomcloudbridge.services.mission_stats import MissionStats # TODO: remove later
from vyomcloudbridge.services.rabbit_queue.queue_main import RabbitMQ
from vyomcloudbridge.utils.logger_setup import setup_logger
from vyomcloudbridge.utils.configs import Configs
from vyomcloudbridge.constants.constants import MAX_FILE_SIZE, LIVE_FILE_SIZE
from vyomcloudbridge.utils.common import generate_unique_id, DATA_TYPE_MAPPING
from vyomcloudbridge.utils.common import get_mission_upload_dir
from vyomcloudbridge.constants.constants import (
    default_project_id,
    default_mission_id,
    data_buffer_key,
)


class ThreadSafeRabbitMQPool:
    """Thread-safe RabbitMQ connection pool for background threads"""

    def __init__(self, max_connections=4):
        self._connections = []
        self._lock = threading.Lock()
        self._max_connections = max_connections
        self.logger = setup_logger(
            name=self.__class__.__module__ + "." + self.__class__.__name__,
            show_terminal=False,
        )

    def get_connection(self) -> RabbitMQ:
        """Get a RabbitMQ connection from the pool"""
        with self._lock:
            # Try to find an available connection
            for conn in self._connections:
                try:
                    if not conn.is_consuming and conn.is_healthy():
                        self.logger.debug(
                            f"Reusing existing RabbitMQ connection for thread {threading.current_thread().name}"
                        )
                        return conn
                except Exception as e:
                    self.logger.warning(f"Connection health check failed: {e}")
                    # Remove unhealthy connection from pool
                    try:
                        self._connections.remove(conn)
                        conn.close()
                    except:
                        pass
            
            # Create new connection if pool is not full
            if len(self._connections) < self._max_connections:
                self.logger.debug(
                    f"Creating new RabbitMQ connection for thread {threading.current_thread().name}"
                )
                try:
                    new_conn = RabbitMQ()
                    self._connections.append(new_conn)
                    return new_conn
                except Exception as e:
                    self.logger.error(f"Failed to create new connection: {e}")
                    # Fall back to creating a temporary connection
                    return RabbitMQ()
            
            # If pool is full, create a temporary connection
            self.logger.debug(
                f"Pool full, creating temporary connection for thread {threading.current_thread().name}"
            )
            return RabbitMQ()

    def cleanup_thread_connection(self):
        """Clean up the current thread's connection - not needed with pool approach"""
        # Connections are reused, so we don't clean up individual thread connections
        pass

    def cleanup(self):
        """Clean up all connections in the pool"""
        with self._lock:
            for conn in self._connections:
                try:
                    conn.close()
                    self.logger.debug(
                        f"Cleaned up RabbitMQ connection from pool"
                    )
                except Exception as e:
                    self.logger.error(f"Error cleaning up pool connection: {e}")
            self._connections.clear()
            self.logger.info("ThreadSafeRabbitMQPool cleanup completed")


class QueueWriterJson:
    """Main class for handling message queue writing operations."""

    def __init__(self):
        self.rabbit_mq = RabbitMQ()  # Main thread connection
        self.rabbit_mq_pool = (
            ThreadSafeRabbitMQPool()
        )  # Thread pool for background threads
        self.machine_config = Configs.get_machine_config()
        self.machine_id = self.machine_config.get("machine_id", "-") or "-"
        self.organization_id = self.machine_config.get("organization_id", "-") or "-"
        self.logger = setup_logger(
            name=self.__class__.__module__ + "." + self.__class__.__name__,
            show_terminal=False,
        )
        self.chunk_merger = ChunkMerger()
        # self.mission_stats = MissionStats() # TODO: remove later
        self.live_publish = True
        self.live_priority = 2
        self.live_destinations = ["s3", "gcs_mqtt"]
        self.live_expiry_time = "2000"  # millisecond
        self.live_executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="live"
        )
        self.data_executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="data"
        )
        self._setup_signal_handlers()

    def _get_file_info(self, filename: str) -> Tuple[str, str, str]:
        """
        Extract file information from filepath.
        Returns: (filename without extension, extension, detected data type)
        """
        extension = filename.lower().lstrip(".")
        data_type = DATA_TYPE_MAPPING.get(extension, "file")
        return filename, extension, data_type

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            self.logger.info("Shutting down...")
            self.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def _get_data_chunks_md5(self, message_data, is_json_data, should_chunk):
        """Helper to split data into chunks and compute MD5 hash"""
        if not is_json_data:
            data = (
                message_data
                if isinstance(message_data, bytes)
                else message_data.encode("utf-8")
            )
        else:
            data = json.dumps(message_data).encode("utf-8")
        md5_hash = hashlib.md5(data).hexdigest()

        # Split data into chunks
        chunks = []
        if should_chunk:
            for i in range(0, len(data), MAX_FILE_SIZE):
                chunks.append(data[i : i + MAX_FILE_SIZE])

        return chunks, md5_hash

    def _get_live_first_chunks(self, message_data, is_json_data):
        """Helper to split data into chunks and compute MD5 hash"""
        if not is_json_data:
            data = (
                message_data
                if isinstance(message_data, bytes)
                else message_data.encode("utf-8")
            )
        else:
            data = json.dumps(message_data).encode("utf-8")

        return data[0:LIVE_FILE_SIZE]

    def _enqueue_live_data_sync(
        self,
        message_data,
        data_type,
        data_size,
        live_dir,
        filename,
        base_filename,
        buffer_key,
        data_source,
    ):
        """Synchronous version for main thread"""
        return self._enqueue_live_data_impl(
            self.rabbit_mq,  # Use main thread connection
            message_data,
            data_type,
            data_size,
            live_dir,
            filename,
            base_filename,
            buffer_key,
            data_source,
        )

    def _enqueue_live_data_async(
        self,
        message_data,
        data_type,
        data_size,
        live_dir,
        filename,
        base_filename,
        buffer_key,
        data_source,
    ):
        """Asynchronous version for background threads"""
        try:
            thread_rabbit_mq = self.rabbit_mq_pool.get_connection()
            return self._enqueue_live_data_impl(
                thread_rabbit_mq,  # Use thread-specific connection
                message_data,
                data_type,
                data_size,
                live_dir,
                filename,
                base_filename,
                buffer_key,
                data_source,
            )
        except Exception as e:
            self.logger.error(f"Error in async live data enqueue: {str(e)}")
        # No need to cleanup thread connection with pool approach

    def _enqueue_live_data_impl(
        self,
        rabbit_mq_conn,  # RabbitMQ connection to use
        message_data,
        data_type,
        data_size,
        live_dir,
        filename,
        base_filename,
        buffer_key,
        data_source,
    ):
        """Implementation that works with any RabbitMQ connection"""
        # Ensure connection is healthy before use
        if not rabbit_mq_conn or not rabbit_mq_conn.is_healthy():
            self.logger.error("RabbitMQ connection is not healthy")
            return
        
        try:
            if data_size is None:
                data_size = (
                    len(json.dumps(message_data).encode("utf-8"))
                    if data_type == "json"
                    else (
                        len(message_data)
                        if isinstance(message_data, bytes)
                        else len(message_data.encode("utf-8"))
                    )
                )
            # LIVE DATA
            data_live = (
                self._get_live_first_chunks(
                    message_data, is_json_data=data_type == "json"
                )
                if data_size > LIVE_FILE_SIZE
                else message_data
            )
            data_type_live = "json" if data_type == "image" else data_type
            message_type_live = "json" if data_type_live == "json" else "binary"
            filename_live = (
                f"{base_filename}.json" if message_type_live == "json" else filename
            )
            if data_type == "image":  # for any binary, converting it to json TODO
                data_live = {
                    "image_base64": base64.b64encode(data_live).decode("utf-8"),
                    "type": "jpeg",
                }
            live_topic = f"{live_dir}/{filename_live}"
        
            # Ensure message_body is properly formatted
            if message_type_live == "binary":
                if isinstance(data_live, bytes):
                    message_body = data_live
                else:
                    message_body = data_live.encode("utf-8") if isinstance(data_live, str) else str(data_live).encode("utf-8")
            else:
                message_body = json.dumps(data_live)
            headers = {
                "message_type": message_type_live,
                "topic": live_topic,
                "destination_ids": self.live_destinations,  # LIVE
                "data_source": data_source,
                # meta info
                "buffer_key": buffer_key,
                "buffer_size": 0,
                "data_type": data_type_live,
            }
            
            # Ensure all header values are strings or simple types
            for key, value in headers.items():
                if isinstance(value, (list, dict)):
                    headers[key] = json.dumps(value)
                elif not isinstance(value, (str, int, float, bool)) and value is not None:
                    headers[key] = str(value)
            rabbit_mq_conn.enqueue_message(
                message=message_body,
                headers=headers,
                priority=self.live_priority,
                expiration=self.live_expiry_time,
            )
            self.logger.info(
                f"Data enqueued to {live_topic}, with expiry time {self.live_expiry_time}"
            )
        except Exception as e:
            self.logger.error(f"Error in publishing live -{str(e)}")
            pass

    def _enqueue_all_data_sync(
        self,
        mission_id,
        message_data,
        data_type,
        data_size,
        chunk_dir,
        filename,
        mission_upload_dir,
        properties,
        merge_chunks,
        base_filename,
        buffer_key,
        data_source,
        destination_ids,
        priority,
        expiry_time_ms,
        background,
    ):
        """Synchronous version for main thread"""
        return self._enqueue_all_data_impl(
            self.rabbit_mq,  # Use main thread connection
            mission_id,
            message_data,
            data_type,
            data_size,
            chunk_dir,
            filename,
            mission_upload_dir,
            properties,
            merge_chunks,
            base_filename,
            buffer_key,
            data_source,
            destination_ids,
            priority,
            expiry_time_ms,
            background,
        )

    def _enqueue_all_data_async(
        self,
        mission_id,
        message_data,
        data_type,
        data_size,
        chunk_dir,
        filename,
        mission_upload_dir,
        properties,
        merge_chunks,
        base_filename,
        buffer_key,
        data_source,
        destination_ids,
        priority,
        expiry_time_ms,
        background,
    ):
        """Asynchronous version for background threads"""
        try:
            thread_rabbit_mq = self.rabbit_mq_pool.get_connection()
            return self._enqueue_all_data_impl(
                thread_rabbit_mq,  # Use thread-specific connection
                mission_id,
                message_data,
                data_type,
                data_size,
                chunk_dir,
                filename,
                mission_upload_dir,
                properties,
                merge_chunks,
                base_filename,
                buffer_key,
                data_source,
                destination_ids,
                priority,
                expiry_time_ms,
                background,
            )
        except Exception as e:
            self.logger.error(f"Error in async all data enqueue: {str(e)}")
            return False, f"Error in async all data enqueue: {str(e)}"
        # No need to cleanup thread connection with pool approach

    def _enqueue_all_data_impl(
        self,
        rabbit_mq_conn,  # RabbitMQ connection to use
        mission_id,
        message_data,
        data_type,
        data_size,
        chunk_dir,
        filename,
        mission_upload_dir,
        properties,
        merge_chunks,
        base_filename,
        buffer_key,
        data_source,
        destination_ids,
        priority,
        expiry_time_ms,
        background,
    ):
        """Implementation that works with any RabbitMQ connection"""
        # Ensure connection is healthy before use
        if not rabbit_mq_conn or not rabbit_mq_conn.is_healthy():
            self.logger.error("RabbitMQ connection is not healthy")
            return False, "RabbitMQ connection is not healthy"
        
        try:
            if data_size is None:
                data_size = (
                    len(json.dumps(message_data).encode("utf-8"))
                    if data_type == "json"
                    else (
                        len(message_data)
                        if isinstance(message_data, bytes)
                        else len(message_data.encode("utf-8"))
                    )
                )
            should_chunk = data_size > MAX_FILE_SIZE
            file_property_size = 0
            # chunks_size = 0
            if should_chunk:
                # 1.1 getting chunks and md5
                data_chunks, data_md5 = self._get_data_chunks_md5(
                    message_data,
                    is_json_data=data_type == "json",
                    should_chunk=should_chunk,
                )
                # 1.2 properties for chunks, doing it inside chunking logic to optimize
                file_info_data = {
                    "filename": filename,
                    "data_type": data_type,
                    "file_md5": data_md5,
                    "total_size": data_size,
                    "file_dir": mission_upload_dir,
                    "properties": properties,
                    "is_chunked": should_chunk,
                    **(
                        {
                            "total_chunks": len(data_chunks),
                            "chunk_dir": chunk_dir,
                            "merge_chunks": merge_chunks,
                            "chunk_name": base_filename,
                        }
                        if should_chunk
                        else {}
                    ),
                }
                # 1.3 send file_properties for chunks
                chunk_info_topic = (
                    f"{mission_upload_dir}/file_properties/{base_filename}.json"
                )
                file_property_size = len(json.dumps(file_info_data).encode("utf-8"))
                message_body = json.dumps(file_info_data)
                headers = {
                    "topic": chunk_info_topic,
                    "message_type": "json",
                    "destination_ids": destination_ids,
                    "data_source": data_source,
                    # meta info
                    "buffer_key": buffer_key,
                    "buffer_size": file_property_size,
                    "data_type": data_type,
                }
                
                # Ensure all header values are strings or simple types
                for key, value in headers.items():
                    if isinstance(value, (list, dict)):
                        headers[key] = json.dumps(value)
                    elif not isinstance(value, (str, int, float, bool)) and value is not None:
                        headers[key] = str(value)
                rabbit_mq_conn.enqueue_message(
                    message=message_body,
                    headers=headers,
                    priority=priority,
                    expiration=expiry_time_ms,
                )
                self.logger.info(f"Data enqueued to {chunk_info_topic}")
                # 1.4 send all chunks
                total_chunks = len(data_chunks)
                padding_length = len(str(total_chunks))
                for i, chunk in enumerate(data_chunks):
                    try:
                        formatted_index = str(i + 1).zfill(padding_length)
                        message_body = chunk
                        # chunks_size += len(chunk)
                        headers = {
                            "message_type": "binary",  # Always binary for chunks
                            "topic": f"{chunk_dir}/{base_filename}_{formatted_index}.bin",
                            "destination_ids": destination_ids,
                            "data_source": data_source,
                            # meta info
                            "buffer_key": buffer_key,
                            "buffer_size": len(chunk),
                            "data_type": data_type,
                        }
                        
                        # Ensure all header values are strings or simple types
                        for key, value in headers.items():
                            if isinstance(value, (list, dict)):
                                headers[key] = json.dumps(value)
                            elif not isinstance(value, (str, int, float, bool)) and value is not None:
                                headers[key] = str(value)
                        rabbit_mq_conn.enqueue_message(
                            message=message_body,
                            headers=headers,
                            priority=priority,
                            expiration=expiry_time_ms,
                        )
                    except Exception as e:
                        self.logger.error(f"Error in publishing chunk {i}: {str(e)}")
                self.logger.info(
                    f"Data enqueued to all {chunk_dir}/{base_filename}_*.bin"
                )
                # 1.5 send event for merging file
                if merge_chunks:
                    s3_prop_key = (
                        f"{mission_upload_dir}/file_properties/{base_filename}.json"
                    )
                    self.chunk_merger.on_chunk_file_arrive(s3_prop_key)
            else:
                try:
                    # 2.1 send file to s3, without chunking
                    file_name_topic = mission_upload_dir + "/" + filename
                    
                    # Ensure message_body is properly formatted
                    if data_type == "json":
                        message_body = json.dumps(message_data)
                    else:
                        if isinstance(message_data, bytes):
                            message_body = message_data
                        else:
                            message_body = message_data.encode("utf-8") if isinstance(message_data, str) else str(message_data).encode("utf-8")
                    headers = {
                        "message_type": "json" if data_type == "json" else "binary",
                        "topic": file_name_topic,
                        "destination_ids": destination_ids,
                        "data_source": data_source,
                        # meta data
                        "buffer_key": buffer_key,
                        "buffer_size": data_size,
                        "data_type": data_type,
                    }
                    rabbit_mq_conn.enqueue_message(
                        message=message_body,
                        headers=headers,
                        priority=priority,
                        expiration=expiry_time_ms,
                    )
                    self.logger.info(f"Data enqueued to {file_name_topic}")
                except Exception as e:
                    self.logger.error(f"Error in publishing : {str(e)}")
            # metadata for machine buffer (in case of all success)
            if expiry_time_ms is None:
                self.logger.debug(
                    f"Enqueuing file info metadata to RabbitMQ, mission_id: {mission_id}, data_source: {data_source}, size: {data_size}"
                )
                rabbit_mq_conn.enqueue_message_size(
                    size=data_size + file_property_size,
                )
                # TODO: remove later
                # self.mission_stats.on_mission_data_arrive(
                #     mission_id=mission_id,
                #     size=data_size+file_property_size,
                #     file_count=1,
                #     data_type=data_type,
                #     data_source=data_source,
                #     s3_dir=mission_upload_dir,
                # )
                self.logger.debug(
                    f"Enqueued file info metadata to RabbitMQ, mission_id: {mission_id}, data_source: {data_source}, size: {data_size}"
                )
            return True, None
        except Exception as e:
            if background:
                self.logger.fatal(
                    f"Error in enqueueing all data, data lost for {mission_upload_dir}/file_properties/{base_filename}.json: {str(e)}"
                )
                return False, f"Error in enqueueing all data: {str(e)}"
            else:
                self.logger.error(f"Error in enqueueing all data: {str(e)}")
                return False, f"Error in enqueueing all data: {str(e)}"

    def write_message(
        self,
        message_data: Any,
        data_type: str,  # json, image, binary
        data_source: str,  # DRONE_STATE, camera1, camera2, machine_state, BATTERY_TOPIC
        destination_ids: List[Union[str, int]],  # array of destination_ids
        source_id: Optional[Union[str, int]] = None,
        filename: Optional[str] = None,
        mission_id: Optional[Union[str, int]] = default_mission_id,
        project_id: Optional[Union[str, int]] = default_project_id,
        priority: Optional[int] = 1,
        merge_chunks: Optional[bool] = False,
        send_live: Optional[bool] = False,
        expiry_time_ms: Optional[Union[int, str]] = None,
        expiry_time: Optional[
            Union[int, str]
        ] = None,  # THIS IS DEPRECATED, USE expiry_time_ms INSTEAD
        background: bool = False,
    ) -> tuple[bool, Union[str, None]]:
        """
        Writes a message to the specified destinations.

        Args:
            message_data: The data to be sent
            data_type: Type of data (json, image, binary)
            data_source: Source of the data (telemetry, drone_state, mission_summary, camera1, camera2, machine_state)
            destination_ids: List of destination IDs to send the message to, for publishing it to server use ["s3"]
            filename: Optional filename for JSON data which be taken from timestamp, for rest give proper name i.e. 17460876104123343.jpeg
            mission_id: Optional mission ID for data generated by current device
            project_id: Optional project ID for data generated by current device
            priority: Optional, message priority to be published in priority order (1 for all, 3 for critical) 2 is reserved
            merge_chunks: Optional, Whether to merge message chunks after publishing it to server, default is False
            send_live: Optional, Whether to send live data or not, default is False
            expiry_time_ms: Optional, message expiry time in milliseconds, default is None, after that message will be deleted from queue
            background: Whether to execute in background thread (True) or synchronously (False)
        Returns:
            tuple[bool, str]: A tuple containing:
                - success: Boolean indicating whether the operation was successful
                - error: Error message if unsuccessful, empty string otherwise
        """
        try:
            expiry_time_ms = expiry_time_ms or expiry_time
            if expiry_time_ms is not None:
                try:
                    expiry_time_ms = str(expiry_time_ms)
                except Exception as e:
                    self.logger.error(
                        f"Error in converting expiry_time_ms to string: {str(e)}"
                    )
                    return (
                        False,
                        f"Error in converting expiry_time_ms to string: {str(e)}",
                    )

            if source_id is None:
                source_id = self.machine_id

            if destination_ids and (
                isinstance(destination_ids, str) or isinstance(destination_ids, int)
            ):
                destination_ids = [destination_ids]

            if data_source is None or data_source == "":
                data_source = "UNKNOWN_SOURCE"
                self.logger.warning(
                    "data_source is None or empty, using 'UNKNOWN_SOURCE' as default"
                )
            if not isinstance(data_source, str):
                return False, "data_source must be a of type string"

            if "/" in data_source:
                self.logger.error(
                    f"data_source '{data_source}' contains '/', which is not allowed"
                )
                return False, "data_source cannot contain '/'"

            if priority is None:
                error_msg = (
                    "'priority' cannot be None; must be an integer (1-4) if provided."
                )
                self.logger.error(error_msg)
                return False, f"[QueueWriterJson.write_message] {error_msg}"

            destination_ids_str = ",".join(str(id) for id in destination_ids)
            mrg_chunks_str = "T" if merge_chunks else "F"
            snd_live_str = "T" if send_live else "F"
            self.logger.info(
                f"Data enqueueing... src={source_id}, dst's=[{destination_ids_str}], dta_src={data_source}, dtatyp={data_type}, fil_nm={filename}, prio={priority}, msid={mission_id}, pid={project_id}, mrg_c={mrg_chunks_str}, live={snd_live_str}, exp={expiry_time or expiry_time_ms}, sz={len(message_data) if hasattr(message_data, '__len__') else 'N/A'}, msgdtatyp={type(message_data).__name__}, bg={background}"
            )
            # isinstance(message_data, bytes) is True when {type(message_data).__name__=="bytes"

            if not filename or filename is None:
                epoch_ms = int(time.time() * 1000)
                if data_type == "json":
                    filename = f"{epoch_ms}.json"
                    self.logger.debug(
                        f"No filename provided, using generated name epoch_ms: {filename}"
                    )
                else:
                    self.logger.error(
                        f"No filename provided, invalid filename for non string message_data, message skipped..."
                    )
                    return False, "No filename provided"

            # Extract filename and extension
            base_filename, file_extension = os.path.splitext(filename)
            file_extension = file_extension[1:]
            if not file_extension:
                file_extension = "json" if data_type == "json" else "bin"
                filename = f"{base_filename}.{file_extension}"

            # Get current time for metadata
            now = datetime.now(timezone.utc)
            properties = {
                "organization_id": self.organization_id,
                "data_source": data_source,
                "date": now.strftime("%Y-%m-%d"),
                "hour": str((now.hour + 1) % 24 or 24),
                "machine_id": source_id,
                "mission_id": mission_id,
                "project_id": project_id,
                "file_name": filename,
            }

            # Determine file paths
            mission_upload_dir: str = get_mission_upload_dir(
                organization_id=self.organization_id,
                machine_id=source_id,
                mission_id=mission_id,
                data_source=data_source,
                date=now.strftime("%Y-%m-%d"),
                project_id=project_id,
            )

            chunk_dir = f"{mission_upload_dir}/chunks"
            live_dir = f"{mission_upload_dir}/live"
            buffer_key = mission_id if isinstance(mission_id, str) else str(mission_id)

            if background:
                data_size = None  # will be calculated in _enqueue_all_data_impl
                if self.live_publish and send_live:
                    self.live_executor.submit(
                        self._enqueue_live_data_async,
                        message_data,
                        data_type,
                        data_size,
                        live_dir,
                        filename,
                        base_filename,
                        buffer_key,
                        data_source,
                    )
                self.data_executor.submit(
                    self._enqueue_all_data_async,
                    mission_id,
                    message_data,
                    data_type,
                    data_size,
                    chunk_dir,
                    filename,
                    mission_upload_dir,
                    properties,
                    merge_chunks,
                    base_filename,
                    buffer_key,
                    data_source,
                    destination_ids,
                    priority,
                    expiry_time_ms,
                    background,
                )
                return True, None
            else:
                # Synchronous execution - use main thread connection
                data_size = (
                    len(json.dumps(message_data).encode("utf-8"))
                    if data_type == "json"
                    else (
                        len(message_data)
                        if isinstance(message_data, bytes)
                        else len(message_data.encode("utf-8"))
                    )
                )
                if self.live_publish and send_live:
                    self._enqueue_live_data_sync(
                        message_data,
                        data_type,
                        data_size,
                        live_dir,
                        filename,
                        base_filename,
                        buffer_key,
                        data_source,
                    )
                success, error = self._enqueue_all_data_sync(
                    mission_id,
                    message_data,
                    data_type,
                    data_size,
                    chunk_dir,
                    filename,
                    mission_upload_dir,
                    properties,
                    merge_chunks,
                    base_filename,
                    buffer_key,
                    data_source,
                    destination_ids,
                    priority,
                    expiry_time_ms,
                    background,
                )
                return success, error

        except Exception as e:
            self.logger.error(f"Error in write_message: {traceback.format_exc()}")
            return False, f"Error in write_message: {str(e)}"

    def cleanup(self):
        """Clean up resources."""
        if self.chunk_merger:
            try:
                self.chunk_merger.stop()
                self.logger.info("chunk_merger cleaned up successfully")
            except Exception as e:
                self.logger.error(
                    f"Error cleaning chunk_merger: {str(e)}", exc_info=True
                )

        # TODO: remove later
        # if self.mission_stats:
        #     try:
        #         self.mission_stats.stop()
        #         self.logger.info("mission_stats cleaned up successfully")
        #     except Exception as e:
        #         self.logger.error(
        #             f"Error cleaning mission_stats: {str(e)}", exc_info=True
        #         )

        try:
            self.rabbit_mq.close()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

            # Clean up thread pool
        if hasattr(self, "live_executor"):
            try:
                self.live_executor.shutdown(wait=True, timeout=5)
                self.logger.info("Live executor cleaned up successfully")
            except Exception as e:
                self.logger.error(f"Error cleaning live executor: {str(e)}")

        if hasattr(self, "data_executor"):
            try:
                self.data_executor.shutdown(wait=True, timeout=5)
                self.logger.info("Data executor cleaned up successfully")
            except Exception as e:
                self.logger.error(f"Error cleaning data executor: {str(e)}")

        # Clean up RabbitMQ pool
        if hasattr(self, "rabbit_mq_pool"):
            try:
                self.rabbit_mq_pool.cleanup()
                self.logger.info("RabbitMQ pool cleaned up successfully")
            except Exception as e:
                self.logger.error(f"Error cleaning RabbitMQ pool: {str(e)}")

    def is_healthy(self):
        """
        Override health check to add additional service-specific checks.
        """
        # TODO: remove later
        # return self.rabbit_mq.is_healthy() and self.mission_stats.is_healthy()
        return self.rabbit_mq.is_healthy()

    def __del__(self):
        """Destructor called by garbage collector to ensure resources are cleaned up, when object is about to be destroyed"""
        try:
            if self.is_healthy():
                self.logger.error(
                    "Destructor called by garbage collector to cleanup QueueWriterJson"
                )
                self.cleanup()
        except Exception as e:
            pass


logger = setup_logger(name=__name__, show_terminal=False)


def main():
    # # Example 1, send data, without live
    from vyomcloudbridge.services.queue_writer_json import QueueWriterJson

    try:
        writer = QueueWriterJson()
        message_data = {"lat": 75.66666, "long": 73.0589455, "alt": 930}
        data_source = "MACHINE_POSE"  # event, warning, camera1, camera2,
        data_type = "json"  # image, binary, json
        mission_id = "111333"

        epoch_ms = int(time.time() * 1000)
        uuid_padding = generate_unique_id(4)
        filename = f"{epoch_ms}_{uuid_padding}.json"

        writer.write_message(
            message_data=message_data,  # json or binary data
            filename=filename,  # 293749834.json, 93484934.jpg
            data_source=data_source,  # machine_pose camera1, machine_state
            data_type=data_type,  # json, binary, ros
            mission_id=mission_id,  # mission_id
            priority=1,  # 1, 2
            destination_ids=["gcs_mav"],  # ["s3"]
        )
    except Exception as e:
        print(f"Error writing test messages: {e}")
    finally:
        writer.cleanup()

if __name__ == "__main__":
    main()
