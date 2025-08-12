import pika
import json
import logging
from datetime import datetime, timezone
import threading
import time
from typing import Dict, Any, Optional
from vyomcloudbridge.services.rabbit_queue.queue_main import RabbitMQ
from vyomcloudbridge.services.root_store import RootStore
from vyomcloudbridge.utils.common import ServiceAbstract, get_mission_upload_dir
from vyomcloudbridge.constants.constants import (
    DEFAULT_RABBITMQ_URL,
    default_project_id,
    default_mission_id,
    data_buffer_key,
)
from vyomcloudbridge.utils.configs import Configs


class MachineStats(ServiceAbstract):
    """
    A service that maintains machine buffer statistics using RabbitMQ as a persistent store.
    Stores the current buffer state in a dedicated queue and publishes stats to HQ.
    """

    def __init__(self):
        """
        Initialize the machine stats service with RabbitMQ connection.
        """
        super().__init__()
        self.host: str = "localhost"
        self.rabbitmq_url = DEFAULT_RABBITMQ_URL
        self.priority = 2  # live priority
        self.stats_publish_interval = 1  # Seconds between stats publication
        self.publish_error_delay = 20  # Delay after publish error

        self.rmq_conn = None
        self.rmq_channel = None
        self.rabbit_mq = RabbitMQ()
        self.machine_config = Configs.get_machine_config()
        self.machine_id = self.machine_config.get("machine_id", "-") or "-"
        self.organization_id = self.machine_config.get("organization_id", "-") or "-"
        self.data_source = "machine_stats"
        self.expiration = "2000"  # milisecond
        self.root_store = RootStore()

        # Thread attributes
        self.stats_thread = None
        self.is_running = False

    def _setup_connection(self):
        """Set up RabbitMQ connection and declare the queue for machine buffer."""
        try:
            # Establish connection
            self.rmq_conn = pika.BlockingConnection(
                pika.URLParameters(self.rabbitmq_url)
            )
            self.rmq_channel = self.rmq_conn.channel()

            # Declare queue for machine buffer
            self.rmq_channel.queue_declare(queue="machine_buffer", durable=True)

            self.logger.info("RabbitMQ connection established successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize RabbitMQ: {str(e)}")
            raise

    def _ensure_connection(self) -> bool:
        """Ensure connection and channel are active and working"""
        try:
            if not self.rmq_conn or self.rmq_conn.is_closed:
                self._setup_connection()
                return True

            if not self.rmq_channel or self.rmq_channel.is_closed:
                self.logger.info("Closed channel found, re-establishing...")
                self.rmq_channel = self.rmq_conn.channel()
                self.rmq_channel.queue_declare(queue="machine_buffer", durable=True)
                self.logger.info("Channel re-established successfully")

            return True
        except Exception as e:
            self.logger.error(f"Failed to ensure connection: {e}")
            self.rmq_conn = None
            self.rmq_channel = None
            return False

    def get_current_buffer(self):
        """
        Get the current data size and uploaded size from RabbitMQ.

        Returns:
            Tuple of (data_size, data_size_uploaded) or (0, 0) if not found.
        """
        try:
            if not self._ensure_connection() or not self.rmq_channel:
                raise Exception("Could not establish connection")

            method_frame, _, body = self.rmq_channel.basic_get(
                queue="machine_buffer", auto_ack=False
            )

            if method_frame:
                data = json.loads(body.decode("utf-8"))
                self.rmq_channel.basic_nack(
                    delivery_tag=method_frame.delivery_tag, requeue=True
                )
                data_size = data.get("data_size", 0)
                data_size_uploaded = data.get("data_size_uploaded", 0)
                return data_size, data_size_uploaded
        except pika.exceptions.DuplicateGetOkCallback as e:
            self.logger.error(
                f"DuplicateGetOkCallback error in get_current_buffer: {e}"
            )
        except Exception as e:
            self.logger.error(f"Warning getting current buffer: {str(e)}")

        return 0, 0

    def _set_current_buffer(self, data_size: int, data_size_uploaded: int):
        try:
            if not self._ensure_connection() or not self.rmq_channel:
                raise Exception("Could not establish connection")

            while True:
                method_frame, _, _ = self.rmq_channel.basic_get(
                    queue="machine_buffer", auto_ack=True
                )
                if not method_frame:
                    break

            body = json.dumps(
                {"data_size": data_size, "data_size_uploaded": data_size_uploaded}
            )

            self.rmq_channel.basic_publish(
                exchange="",
                routing_key="machine_buffer",
                body=body,
                properties=pika.BasicProperties(delivery_mode=2),
            )

            self.logger.info(
                f"Set buffer: data_size={data_size}, data_size_uploaded={data_size_uploaded}"
            )
        except pika.exceptions.DuplicateGetOkCallback as e:
            self.logger.error(
                f"DuplicateGetOkCallback error in _set_current_buffer: {e}"
            )
        except Exception as e:
            self.logger.error(f"Error setting buffer state: {str(e)}")

    def on_data_arrive(self, size: int):
        try:
            data_size, data_size_uploaded = self.get_current_buffer()
            new_data_size = data_size + int(size)
            self._set_current_buffer(new_data_size, data_size_uploaded)
            self.logger.info(
                f"Data arrived: +{size} bytes, new data_size={new_data_size}"
            )
        except Exception as e:
            self.logger.error(f"Error handling data arrival: {str(e)}")

    def on_data_publish(self, size: int):
        try:
            data_size, data_size_uploaded = self.get_current_buffer()
            new_uploaded = min(data_size_uploaded + int(size), data_size)
            self._set_current_buffer(data_size, new_uploaded)
            self.logger.info(
                f"Data published: +{size} bytes, total uploaded={new_uploaded}"
            )
        except Exception as e:
            self.logger.error(f"Error handling data publish: {str(e)}")

    def _publish_stats_to_hq(self) -> bool:
        """
        Send buffer size to API endpoint with retry logic.

        Returns:
            True if report was successful, False otherwise
        """
        try:
            # Get current buffer
            data_size, data_size_uploaded = self.get_current_buffer()
            buffer_size_bytes = data_size - data_size_uploaded
            try:
                location_data = self.root_store.get_data("location")
            except Exception as e:
                location_data = None

            try:
                health_data = self.root_store.get_data("health")
            except Exception as e:
                health_data = None

            # Prepare payload
            payload = {
                "machine_id": self.machine_id,
                "buffer": buffer_size_bytes,
                "data_size": data_size,
                "data_size_uploaded": data_size_uploaded,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "location": location_data,
                "health": health_data,
            }

            # Log current state
            self.logger.debug(
                f"Current buffer state: Total: {buffer_size_bytes:.2f} bytes"
            )

            now = datetime.now(timezone.utc)
            date = now.strftime("%Y-%m-%d")
            filename = int(time.time() * 1000)
            # mission_upload_dir = f"{self.machine_config['organization_id']}/{default_project_id}/{date}/machine_stats/{self.machine_id}" # TODO
            mission_upload_dir: str = get_mission_upload_dir(
                organization_id=self.organization_id,
                machine_id=self.machine_id,
                mission_id=default_mission_id,
                data_source=self.data_source,
                date=date,
                project_id=default_project_id,
            )

            message_body = json.dumps(payload)
            headers = {
                "topic": f"{mission_upload_dir}/{filename}.json",
                "message_type": "json",
                "destination_ids": ["s3"],
                "data_source": self.data_source,
                # meta data
                "buffer_key": data_buffer_key,
                "buffer_size": 0,
                "data_type": "json",
            }
            self.rabbit_mq.enqueue_message(
                message=message_body,
                headers=headers,
                priority=self.priority,
                expiration=self.expiration,
            )

            self.logger.debug("Machine stats publish SUCCESSFUL")
            return True

        except Exception as e:
            self.logger.error(f"Machine stats publish: Unexpected error: {e}")
            return False

    def start(self):
        """
        Start the machine stats service, including the background publisher thread.
        """
        try:
            self.logger.info("Starting MachineStats service...")
            self.is_running = True

            # Define the stats publisher loop
            def stats_publisher_loop():
                while self.is_running:
                    try:
                        self._publish_stats_to_hq()
                        time.sleep(self.stats_publish_interval)
                    except Exception as e:
                        self.logger.error(f"Error in stats publisher loop: {str(e)}")
                        time.sleep(self.publish_error_delay)

            # Create and start the thread
            self.stats_thread = threading.Thread(
                target=stats_publisher_loop, daemon=True
            )
            self.stats_thread.start()

            self.logger.info("MachineStats service started!")

        except Exception as e:
            self.logger.error(f"Error starting MachineStats service: {str(e)}")
            self.stop()
            raise

    def stop(self):
        """
        Stop the machine stats service and clean up resources.
        """
        self.is_running = False

        # Wait for thread to finish
        if (
            hasattr(self, "stats_thread")
            and self.stats_thread
            and self.stats_thread.is_alive()
        ):
            self.stats_thread.join(timeout=5)

        # Clean up connection
        self.cleanup()

        self.logger.info("MachineStats service stopped")

    def cleanup(self):
        """
        Clean up resources, closing connections and channels.
        """
        try:
            if hasattr(self, "rmq_conn") and self.rmq_conn and self.rmq_conn.is_open:
                self.rmq_conn.close()
        except Exception as e:
            self.logger.error(f"Error closing RabbitMQ connection: {str(e)}")

        try:
            self.rabbit_mq.close()
        except Exception as e:
            self.logger.error(f"Error closing RabbitMQ connection: {str(e)}")

        try:
            self.root_store.cleanup()
        except Exception as e:
            self.logger.error(f"Error closing Root store connection: {str(e)}")

    def is_healthy(self):
        """
        Check if the service is healthy.
        """
        return (
            self.is_running
            and hasattr(self, "rmq_conn")
            and self.rmq_conn
            and self.rmq_conn.is_open
            and self.rabbit_mq.is_healthy()
        )

    def __del__(self):
        """Destructor called by garbage collector to ensure resources are cleaned up, when object is about to be destroyed"""
        try:
            self.logger.error(
                "Destructor called by garbage collector to cleanup MachineStats"
            )
            self.stop()
        except Exception as e:
            pass


def main():
    """Example of how to use the MachineStats service"""
    print("Starting machine stats service example")

    machine_stats = MachineStats()

    machine_stats.on_data_arrive(1024)  # 1 MB
    machine_stats.on_data_publish(500)

    machine_stats.cleanup()

    # Create the service
    machine_stats = MachineStats()

    try:
        # Simulate data arriving
        machine_stats.on_data_arrive(1024)  # 1 MB
        print(
            f"Current buffer after data arrival: {machine_stats.get_current_buffer()} bytes"
        )

        # Simulate publishing some data
        machine_stats.on_data_publish(500)  # 512 KB
        print(
            f"Current buffer after publishing: {machine_stats.get_current_buffer()} bytes"
        )

        # Start the service for continuous monitoring
        machine_stats.start()

        # Let it run for a short while
        time.sleep(20)

    finally:
        # Clean up
        machine_stats.stop()

    print("Completed machine stats service example")


if __name__ == "__main__":
    main()
