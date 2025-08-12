# vyomcloudbridge/queue_writer_json.py
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
from typing import Dict, Any
import json
from typing import Dict, Any, List, Tuple, Union
from pathlib import Path
from vyomcloudbridge.services.chunk_merger import ChunkMerger
from vyomcloudbridge.services.mission_stats import MissionStats
from vyomcloudbridge.services.rabbit_queue.queue_main import RabbitMQ
from vyomcloudbridge.utils.logger_setup import setup_logger
from vyomcloudbridge.utils.configs import Configs
from vyomcloudbridge.constants.constants import MAX_FILE_SIZE, LIVE_FILE_SIZE
from vyomcloudbridge.utils.common import generate_unique_id, DATA_TYPE_MAPPING
from vyomcloudbridge.utils.common import get_mission_upload_dir, get_mission_dir_for_s3
from vyomcloudbridge.constants.constants import (
    default_project_id,
    default_mission_id,
    data_buffer_key,
)


# logger = setup_logger(name=__name__, show_terminal=False)


class QueueWriterJson:
    """Main class for handling message queue writing operations."""

    def __init__(self):
        self.rabbit_mq = RabbitMQ()
        self.machine_config = Configs.get_machine_config()
        self.machine_id = self.machine_config.get("machine_id", "-") or "-"
        self.organization_id = self.machine_config.get("organization_id", "-") or "-"
        self.logger = setup_logger(
            name=self.__class__.__module__ + "." + self.__class__.__name__,
            show_terminal=False,
        )
        self.chunk_merger = ChunkMerger()
        self.mission_stats = MissionStats()
        self.live_publish = True
        self.live_priority = 2
        self.live_destinations = ["s3", "gcs_mqtt"]
        self.expiration = "2000"  # milisecond
        self._setup_signal_handlers()

    # def _mission_upload_dir(self, message: Dict[str, Any]) -> str:
    #     """
    #     Returns:
    #         str: Upload dir for mission related data
    #     """
    #     now = datetime.now(timezone.utc)
    #     default_date = now.strftime("%Y-%m-%d")

    #     date = message.get("date", default_date)
    #     project_id = message.get("project_id", default_project_id)

    #     return (
    #         f"{self.machine_config['organization_id']}/{project_id}/{date}/"
    #         f"{message['data_source']}/{self.machine_config['machine_id']}/{message['mission_id']}"
    #     )

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

    def _read_data(self, message_data, message_type):
        """Helper to read data and compute MD5 hash"""
        if message_type == "binary":
            data = (
                message_data
                if isinstance(message_data, bytes)
                else message_data.encode("utf-8")
            )
        else:
            data = json.dumps(message_data).encode("utf-8")

        md5_hash = hashlib.md5(data).hexdigest()
        return data, md5_hash

    def _read_data_in_chunks(self, message_data, message_type):
        """Helper to split data into chunks and compute MD5 hash"""
        if message_type == "binary":
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
        for i in range(0, len(data), MAX_FILE_SIZE):
            chunks.append(data[i : i + MAX_FILE_SIZE])

        return chunks, md5_hash

    def _get_live_first_chunks(self, message_data, message_type):
        """Helper to split data into chunks and compute MD5 hash"""
        if message_type == "binary":
            data = (
                message_data
                if isinstance(message_data, bytes)
                else message_data.encode("utf-8")
            )
        else:
            data = json.dumps(message_data).encode("utf-8")

        return data[0:LIVE_FILE_SIZE]

    def write_message(
        self,
        message_data,
        data_type: str,  # json, image, binary
        data_source: str,  # DRONE_STATE, camera1, camera2, machine_state, BATTERY_TOPIC
        destination_ids,  # array of destination_ids
        source_id: Union[str, int] = None,
        filename: str = None,
        mission_id: Union[str, int] = default_mission_id,
        project_id: Union[str, int] = default_project_id,
        priority: int = 1,
        merge_chunks: bool = False,
        send_live: bool = False,
        expiry_time: Union[int, str] = None,
    ) -> tuple[bool, str]:
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
            expiry_time: Optional, message expiry time in milliseconds, default is None, after that message will be deleted from queue
        Returns:
            tuple[bool, str]: A tuple containing:
                - success: Boolean indicating whether the operation was successful
                - error: Error message if unsuccessful, empty string otherwise
        """
        try:
            if expiry_time is not None:
                try:
                    expiry_time = str(expiry_time)
                except Exception as e:
                    self.logger.error(
                        f"Error in converting expiry_time to string: {str(e)}"
                    )
                    return False, f"Error in converting expiry_time to string: {str(e)}"

            if source_id is None:
                source_id = self.machine_id
            self.logger.info(
                f"Data arrived to data_source={data_source}, data_type={data_type}, filename={filename}, message_data_type={type(message_data)}, isinstance={isinstance(message_data, bytes)}"
            )
            # if data_source!="camera-color-image_raw":
            #     return False, ""
            message_type = "json" if data_type == "json" else "binary"
            # message_type = "binary" if isinstance(message_data, bytes) else "json"
            if not filename or filename is None:
                epoch_ms = int(time.time() * 1000)
                if data_type == "json":
                    filename = f"{epoch_ms}.json"
                    self.logger.warning(
                        f"No filename provided, using generated name epoch_ms: {filename}"
                    )
                else:
                    self.logger.error(
                        f"No filename provided, invalid filename for non string message_data, message skipped..."
                    )
                    return False, "No filename provided"

            # self.logger.info(f"Data arrived TESSSSSST 1")
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

            # self.logger.info(f"Data arrived TESSSSSST 2")
            # Determine file paths
            # file_mqtt_dir = self._mission_upload_dir(properties) # TODO
            file_mqtt_dir: str = get_mission_upload_dir(
                organization_id=self.organization_id,
                machine_id=source_id,
                mission_id=mission_id,
                data_source=data_source,
                date=now.strftime("%Y-%m-%d"),
                project_id=project_id,
            )
            file_s3_dir: str = get_mission_dir_for_s3(
                organization_id=self.organization_id,
                machine_id=source_id,
                mission_id=mission_id,
                data_source=data_source,
                date=now.strftime("%Y-%m-%d"),
                project_id=project_id,
            )

            chunk_dir = f"{file_mqtt_dir}/chunks"
            live_dir = f"{file_mqtt_dir}/live"
            buffer_key = mission_id if isinstance(mission_id, str) else str(mission_id)

            # self.logger.info(f"Data arrived TESSSSSST 3")
            # Determine data size and if chunking is needed
            if message_type == "binary":
                data_size: int = (
                    len(message_data)
                    if isinstance(message_data, bytes)
                    else len(message_data.encode("utf-8"))
                )
            else:  # JSON
                data_size: int = len(json.dumps(message_data).encode("utf-8"))

            should_chunk = data_size > MAX_FILE_SIZE
            should_chunk_live = data_size > LIVE_FILE_SIZE

            # Process data according to size
            if should_chunk:
                data_chunks, data_md5 = self._read_data_in_chunks(
                    message_data, message_type
                )
            else:
                data, data_md5 = self._read_data(message_data, message_type)
                data_chunks = []
            # LIVE
            if should_chunk_live:
                data_live = self._get_live_first_chunks(message_data, message_type)
            else:
                data_live = message_data

            # self.logger.info(f"Data arrived TESSSSSST 4")
            if self.live_publish and send_live:
                try:
                    # self.logger.info(f"Data arrived TESSSSSST 5")
                    data_type_live = "json" if data_type == "image" else data_type
                    message_type_live = "json" if data_type_live == "json" else "binary"
                    filename_live = (
                        f"{base_filename}.json"
                        if message_type_live == "json"
                        else filename
                    )
                    # self.logger.info(f"Data arrived TESSSSSST 6, {len(data_live)}")
                    # self.logger.info(f"Data arrived TESSSSSST 7, {type(data_live)}, data_type={data_type}")
                    if (
                        data_type == "image"
                    ):  # for any binary, converting it to json TODO
                        # self.logger.info(f"Data arrived TESSSSSST 7.1, updated")
                        data_live = {
                            "image_base64": base64.b64encode(data_live).decode("utf-8"),
                            "type": "jpeg",
                        }
                    live_topic = f"{live_dir}/{filename_live}"
                    message_body = (
                        data_live
                        if message_type_live == "binary"
                        else json.dumps(data_live)
                    )
                    headers = {
                        "message_type": message_type_live,
                        "topic": live_topic,
                        "destination_ids": self.live_destinations,  # LIVE
                        "data_source": data_source,
                        # meta data
                        "buffer_key": buffer_key,
                        "buffer_size": 0,
                        "data_type": data_type_live,
                    }
                    self.rabbit_mq.enqueue_message(
                        message=message_body,
                        headers=headers,
                        priority=priority,
                        expiration=self.expiration,
                    )
                    self.logger.info(
                        f"Data enqueued to {live_topic}, with expiry time {self.expiration}"
                    )
                except Exception as e:
                    self.logger.error(f"Error in publishing live data-{str(e)}")
                    pass
                # TODO
                # return True, ""

            if expiry_time is not None:
                try:
                    data_type_live = "json" if data_type == "image" else data_type
                    message_type_live = "json" if data_type_live == "json" else "binary"
                    filename_live = (
                        f"{base_filename}.json"
                        if message_type_live == "json"
                        else filename
                    )
                    if data_type == "image":
                        data_live = {
                            "image_base64": base64.b64encode(data_live).decode("utf-8"),
                            "type": "jpeg",
                        }
                    live_topic = f"{live_dir}/{filename_live}"
                    message_body = (
                        data_live
                        if message_type_live == "binary"
                        else json.dumps(data_live)
                    )
                    headers = {
                        "message_type": message_type_live,
                        "topic": live_topic,
                        "destination_ids": self.live_destinations,
                        "data_source": data_source,
                        # meta data
                        "buffer_key": buffer_key,
                        "buffer_size": 0,
                        "data_type": data_type_live,
                    }
                    self.rabbit_mq.enqueue_message(
                        message=message_body,
                        headers=headers,
                        priority=priority,
                        expiration=expiry_time,
                    )
                    self.logger.info(
                        f"Data enqueued to {live_topic}, with expiry time {expiry_time}"
                    )
                    return True, ""
                except Exception as e:
                    self.logger.error(f"Error in publishing live data-{str(e)}")
                    return False, f"Error in publishing live data-{str(e)}"

            # Prepare file info metadata
            file_info_data = {
                "filename": filename,
                "data_type": data_type,
                "file_md5": data_md5,
                "total_size": data_size,
                "file_dir": file_s3_dir,
                "properties": properties,
            }

            if should_chunk:
                file_info_data.update(
                    {
                        "is_chunked": True,
                        "total_chunks": len(data_chunks),
                        "chunk_dir": chunk_dir,
                        "merge_chunks": merge_chunks,
                        "chunk_name": base_filename,
                    }
                )
            else:
                file_info_data.update(
                    {
                        "is_chunked": False,
                    }
                )

            if should_chunk:
                chunk_info_topic = (
                    f"{file_mqtt_dir}/file_properties/{base_filename}.json"
                )
                message_body = json.dumps(file_info_data)
                headers = {
                    "topic": chunk_info_topic,
                    "message_type": "json",
                    "destination_ids": destination_ids,
                    "data_source": data_source,
                    # meta data
                    "buffer_key": buffer_key,
                    "buffer_size": len(json.dumps(file_info_data).encode("utf-8")),
                    "data_type": data_type,
                }
                self.rabbit_mq.enqueue_message(
                    message=message_body, headers=headers, priority=priority
                )

                self.logger.info(f"Data enqueued to {chunk_info_topic}")

            self.mission_stats.(
                mission_id=mission_id,
                size=data_size,
                file_count=1,
                data_type=data_type,
                data_source=data_source,
                s3_dir=file_mqtt_dir,
            )

            # Send content based on chunking decision
            if should_chunk:
                total_chunks = len(data_chunks)
                padding_length = len(str(total_chunks))
                for i, chunk in enumerate(data_chunks):
                    try:
                        formatted_index = str(i + 1).zfill(padding_length)
                        message_body = chunk
                        headers = {
                            "message_type": "binary",  # Always binary for chunks
                            "topic": f"{chunk_dir}/{base_filename}_{formatted_index}.bin",
                            "destination_ids": destination_ids,
                            "data_source": data_source,
                            # meta data
                            "buffer_key": buffer_key,
                            "buffer_size": len(chunk),
                            "data_type": data_type,
                        }
                        self.rabbit_mq.enqueue_message(
                            message=message_body, headers=headers, priority=priority
                        )

                    except Exception as e:
                        self.logger.error(f"Error in publishing chunk {i}: {str(e)}")
                self.logger.info(
                    f"Data enqueued to all {chunk_dir}/{base_filename}_*.bin"
                )
                if merge_chunks:
                    # send event for merging file
                    s3_prop_key = (
                        f"{file_mqtt_dir}/file_properties/{base_filename}.json"
                    )
                    self.chunk_merger.on_chunk_file_arrive(s3_prop_key)
            else:
                try:
                    file_name_topic = file_mqtt_dir + "/" + filename

                    message_body = (
                        message_data
                        if message_type == "binary"
                        else json.dumps(message_data)
                    )
                    headers = {
                        "message_type": message_type,
                        "topic": file_name_topic,
                        "destination_ids": destination_ids,
                        "data_source": data_source,
                        # meta data
                        "buffer_key": buffer_key,
                        "buffer_size": data_size,
                        "data_type": data_type,
                    }
                    self.rabbit_mq.enqueue_message(
                        message=message_body, headers=headers, priority=priority
                    )
                    self.logger.info(f"Data enqueued to all {file_name_topic}")
                except Exception as e:
                    self.logger.error(f"Error in publishing data: {str(e)}")
            return True, None
        except Exception as e:
            error = f"Error in write_message: {traceback.format_exc()}"
            error_message = f"Error in write_message: {str(e)}"
            self.logger.error(error)
            return False, error_message

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

        if self.mission_stats:
            try:
                self.mission_stats.stop()
                self.logger.info("mission_stats cleaned up successfully")
            except Exception as e:
                self.logger.error(
                    f"Error cleaning mission_stats: {str(e)}", exc_info=True
                )

        try:
            self.rabbit_mq.close()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def is_healthy(self):
        """
        Override health check to add additional service-specific checks.
        """
        return self.rabbit_mq.is_healthy() and self.mission_stats.is_healthy()

    def __del__(self):
        """Destructor called by garbage collector to ensure resources are cleaned up, when object is about to be destroyed"""
        try:
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
            destination_ids=["s3"],  # ["s3"]
        )
    except Exception as e:
        print(f"Error writing test messages: {e}")
    finally:
        writer.cleanup()

    # # Example 2, send data, live
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
            destination_ids=["s3"],  # ["s3"]
            send_live=True,
        )
    except Exception as e:
        print(f"Error writing test messages: {e}")
    finally:
        writer.cleanup()

    # # Example 3
    from vyomcloudbridge.services.queue_writer_json import QueueWriterJson

    writer = QueueWriterJson()
    try:
        loop_len = 10
        padding_length = len(str(loop_len))

        for i in range(loop_len):
            epoch_ms = int(time.time() * 1000)
            message_data = {
                "data": f"Test message No {i}",
                "data_id": epoch_ms,
                "lat": 75.66666,
                "long": 73.0589455,
                "alt": 930,
            }

            data_source = "MACHINE_POSE"  # event, warning, camera1, camera2,
            data_type = "json"  # image, binary, json
            mission_id = "111333"
            formatted_index = str(i + 1).zfill(padding_length)
            filename = f"{epoch_ms}_{formatted_index}.json"

            writer.write_message(
                message_data=message_data,
                filename=filename,
                data_source=data_source,
                data_type=data_type,
                mission_id=mission_id,
                priority=1,
                destination_ids=["s3"],
            )
    except Exception as e:
        print(f"Error writing test messages: {e}")
    finally:
        writer.cleanup()

    # # Example 4
    from vyomcloudbridge.services.queue_writer_json import QueueWriterJson

    writer = QueueWriterJson()
    try:
        import requests
        from urllib.parse import urlparse

        loop_len = 10
        padding_length = len(str(loop_len))

        # URLs for the images
        image_urls = [
            "https://sample-videos.com/img/Sample-jpg-image-50kb.jpg",
            # "https://sample-videos.com/img/Sample-png-image-100kb.png",
            # "https://sample-videos.com/img/Sample-jpg-image-100kb.jpg",
            "https://sample-videos.com/img/Sample-jpg-image-200kb.jpg",
            "https://sample-videos.com/img/Sample-jpg-image-500kb.jpg",
        ]

        for i in range(loop_len):
            epoch_ms = int(time.time() * 1000)
            data_source = "AIRSIM_CAMERA_FRONT"  # event, warning, camera1, camera2
            data_type = "image"  # image, json, binary
            mission_id = default_mission_id  # "34556"
            formatted_index = str(i + 1).zfill(padding_length)

            # Alternate between the two URLs
            current_url = image_urls[i % len(image_urls)]

            # Get the file extension from the URL
            parsed_url = urlparse(current_url)
            file_extension = parsed_url.path.split(".")[-1]

            # Download the image binary data
            response = requests.get(current_url)
            if response.status_code == 200:
                file_data = response.content  # This is binary data (bytes)

                # Create filename with proper extension
                filename = f"{epoch_ms}_{formatted_index}.{file_extension}"

                writer.write_message(
                    message_data=file_data,
                    filename=filename,
                    data_source=data_source,
                    data_type=data_type,
                    mission_id=mission_id,
                    priority=1,
                    destination_ids=["s3"],
                )
            else:
                print(
                    f"Failed to download image from {current_url}. Status code: {response.status_code}"
                )

    except Exception as e:
        print(f"Error writing test messages: {e}")
    finally:
        writer.cleanup()

    # Example 5 - send mission detail
    from vyomcloudbridge.services.queue_writer_json import QueueWriterJson

    writer = QueueWriterJson()
    try:
        mission_id = "301394"
        machine_id = 60
        epoch_ms = int(time.time() * 1000)
        filename = f"{epoch_ms}.json"

        mission_stats = {
            "mission": {
                "id": mission_id,
                "name": f"Test Mission {mission_id}",
                "creator_id": 1,
                "owner_id": 1,
                "mission_status": 1,
                "machine_id": machine_id,
                "mission_date": "2025-03-21",  # datetime.now(timezone.utc).strftime("%Y-%m-%d")
                "start_time": "2025-03-21T10:00:00Z",  # datetime.now(timezone.utc).isoformat()
                "end_time": None,  # datetime.now(timezone.utc).strftime("%Y-%m-%d")
                # less important field
                "description": "Testing mission navigation features",
                "campaign_id": 1,
                "mission_type": "",
                "json_data": {},
            }
        }
        writer.write_message(
            message_data=mission_stats,  # json or binary data
            filename=filename,  # 293749834.json, 93484934.jpg
            data_source="mission_stats",  # machine_pose camera1, machine_state
            data_type="json",  # image, binary, json
            mission_id=mission_id,  # mission_id
            priority=1,  # important send with priority 1
            destination_ids=["s3"],  # ["s3"]
        )
    except Exception as e:
        print(f"Error writing test messages: {e}")
    finally:
        writer.cleanup()

    # Example 6 - send mission topics list
    from vyomcloudbridge.services.queue_writer_json import QueueWriterJson

    writer = QueueWriterJson()
    try:
        mission_id = "301394"
        epoch_ms = int(time.time() * 1000)
        filename = f"{epoch_ms}.json"

        mission_stats = {
            "mission_topics": {} or []  # here you have to add, mission topics object
        }
        writer.write_message(
            message_data=mission_stats,  # json or binary data
            filename=filename,  # 293749834.json, 93484934.jpg
            data_source="mission_stats",  # machine_pose camera1, machine_state
            data_type="json",  # image, binary, json
            mission_id=mission_id,  # mission_id
            priority=1,  # important send with priority 1
            destination_ids=["s3"],  # ["s3"]
        )
    except Exception as e:
        print(f"Error writing test messages: {e}")
    finally:
        writer.cleanup()


if __name__ == "__main__":
    main()
