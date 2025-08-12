# === Standard Library ===
import importlib
import json
import math
import os
import sys
import threading
import time
from collections import defaultdict
from typing import Callable

# === Third-party / ROS 2 Libraries ===
import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, HistoryPolicy, QoSDurabilityPolicy
from rosidl_runtime_py import set_message_fields
import sensor_msgs.msg
from std_msgs.msg import String

# === Local Application Imports ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.generate_summary import Summariser
from vyomcloudbridge.constants.constants import default_mission_id
from vyomcloudbridge.services.mission_stats import MissionStats
from vyomcloudbridge.services.queue_writer_json import QueueWriterJson
from vyomcloudbridge.utils.common import ServiceAbstract
from vyomcloudbridge.utils.logger_setup import setup_logger
import vyomcloudbridge.utils.converter as converter
from vyomcloudbridge.utils.throttle_utils import should_throttle


class SendDataToServer(Node, ServiceAbstract):
    """
    SendDataToServer is a ROS2 node responsible for subscribing to various topics, processing the received data,
    and writing the processed data to a queue in JSON format. The node dynamically creates subscribers based on
    a configuration file and handles different message types, including JSON and images.

    Attributes:
        callback_group (ReentrantCallbackGroup): A callback group to ensure reentrant callbacks.
        extracted_data_list (list): A list to store extracted data.
        subscribers (list): A list to store dynamically created subscribers.
        m_qos (QoSProfile): Quality of Service profile for the subscribers.
        mission_id (int): Identifier for the mission, used in the processed data.
        writer (QueueWriterJson): An instance of QueueWriterJson to handle writing messages to a queue.

    Methods:
        __init__(): Initializes the node, loads topics from a configuration file, and creates subscribers.
        get_subcribed_topics(): Retrieves the list of topics to subscribe to based on the configuration file.
        load_topic_list_from_file(): Loads the topic list from a JSON configuration file.
        create_listener_function(msg_type, f_topic): Creates a listener function for a specific topic and message type.
        import_class_from_string(class_string): Dynamically imports a class from its string representation.
        create_dynamic_subscribers(f_topic): Dynamically creates a subscriber for a given topic.
    """

    def __init__(self, get_current_mission: Callable = None):
        Node.__init__(self, "senddatatoserver")
        ServiceAbstract.__init__(self)

        self.logger.info("senddatatoserver node has started.")
        self.callback_group = ReentrantCallbackGroup()

        # Initialize extracted data list
        self.machine_subscribers = []
        self.mission_subscribers = []

        self.m_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=50,
            durability=QoSDurabilityPolicy.VOLATILE,
        )
        self.camera_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_ALL,
            depth=100,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        self.writer = QueueWriterJson()

        self.mission_id = default_mission_id
        self.is_running = False
        current_mission, error = get_current_mission()
        self.current_mission = current_mission
        self.get_current_mission = get_current_mission

        self.summariser = Summariser()

        # ros topic used to trigger updation of subscriber list
        self.topic_list_sub = self.create_subscription(
            String, "update_topic_list", self.update_topic_list_machine_callback, 10
        )
        self.topic_list_sub
        
        self.topic_list_sub_os = self.create_subscription(
            String, "update_topic_list_os", self.update_topic_list_mission_callback, 10
        )
        self.topic_list_sub_os
        
        self._freq_tracker = defaultdict(lambda: {"last_time": None})
        self.logger.info("SendDataToServer node initialized successfully.")
           
    def update_topic_list_mission_callback(self, msg):
        try:
            # Parse JSON array from message
            new_topics_list = json.loads(msg.data)
            if not isinstance(new_topics_list, list):
                self.logger.error("Expected a JSON list of topic objects.")
                return
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from /update_topic_list_os: {e}")
            return

        self.logger.info(f"Received new_topics mission: {new_topics_list}")
        available_topics = self.load_topic_list_from_file()

        # Build the final list of topics we will subscribe to
        updated_subscription_list = []
        for received_topic in new_topics_list:
            matching_topic_config = next(
                (topic for topic in available_topics if topic["name"] == received_topic["name"]),
                None
            )
            if matching_topic_config:
                # Override stored settings with any provided in the incoming message
                matching_topic_config.update({
                    "is_subscribed": received_topic.get("is_subscribed", matching_topic_config["is_subscribed"]),
                    "frequency": received_topic.get("frequency", matching_topic_config["frequency"]),
                    "send_live": received_topic.get("send_live", matching_topic_config["send_live"]),
                    "save_locally": received_topic.get("save_locally", matching_topic_config["save_locally"])
                })
                updated_subscription_list.append(matching_topic_config)
        
        new_topics = {topic["topic"] for topic in updated_subscription_list}
        self.logger.info(f"Received new_topics mission: {new_topics}")
        
        
        # Get current mission_subscribers
        current_subscriber_map = {sub.topic_name: sub for sub in self.mission_subscribers}
        current_topics = set(current_subscriber_map.keys())

        # # Early exit if no changes
        if current_topics == new_topics:
            self.logger.info("Topic list unchanged. No update needed.")
            return

        self.logger.info(f"New topics: {new_topics}, Current topics: {current_topics}")
        # Build the new subscriber list before destroying any
        self.mission_subscribers = [
            sub for sub in self.mission_subscribers if sub.topic_name in new_topics
        ]

        # Unsubscribe from topics that are no longer needed
        for topic_name in current_topics - new_topics:
            self.logger.info(f"Unsubscribing from topic: {topic_name}")
            self.destroy_subscription(current_subscriber_map[topic_name])

        self.logger.info(f"Subscribing to new topic: ")
        
        # Subscribe to new topics
        for topic in updated_subscription_list:
            if topic["topic"] not in current_topics:
                self.logger.info(
                    f"Subscribing to new topic: "
                    f"{topic['name']} | {topic['data_type']} | {topic['topic']} | "
                    f"live: {topic['send_live']} | freq: {topic['frequency']} | save: {topic['save_locally']}"
                )
                self.create_dynamic_subscribers(topic, self.mission_subscribers)
                

    def update_topic_list_machine_callback(self, msg):
        new_topic_list = self.get_subcribed_topics()
        self.logger.info(f"[Machine] Received new topic list: {new_topic_list}")

        new_topics = {topic["topic"] for topic in new_topic_list}
        current_subscriber_map = {sub.topic_name: sub for sub in self.machine_subscribers}
        current_topics = set(current_subscriber_map.keys())
        

        # Early exit if no changes
        if current_topics == new_topics:
            self.logger.debug("[Machine] Topic list unchanged. No update needed.")
            return

        # Build the new subscriber list before destroying any
        self.machine_subscribers = [
            sub for sub in self.machine_subscribers if sub.topic_name in new_topics
        ]

        # Unsubscribe from topics that are no longer needed
        for topic_name in current_topics - new_topics:
            self.logger.debug(f"[Machine] Unsubscribing from topic: {topic_name}")
            self.destroy_subscription(current_subscriber_map[topic_name])

        # Subscribe to new topics
        for topic in new_topic_list:
            if topic["topic"] not in current_topics:
                self.logger.debug(f"[Machine] Subscribing to new topic: {topic['topic']}")
                self.create_dynamic_subscribers(topic, self.machine_subscribers)

    def create_subscribers(self):
        self.is_running = True
        self.logger.debug(f"topics {self.get_subcribed_topics()}")
        for topic in self.get_subcribed_topics():
            self.logger.info(f"Subscribing to topic: {topic}")
            self.create_dynamic_subscribers(topic,self.machine_subscribers)

    def get_subcribed_topics(self):
        """
        Retrieve the list of subscribed topics.

        This method loads a list of topics from a file and filters them to return
        only those topics that are marked as subscribed.

        Returns:
            list: A list of dictionaries representing the subscribed topics.
        """

        topic_list = self.load_topic_list_from_file()
        return [topics for topics in topic_list if topics["is_subscribed"]]

    def load_topic_list_from_file(self):
        """
        Loads a list of topics from a JSON file.

        This method reads the file located at '/etc/vyomcloudbridge/machine_topics.json',
        deserializes its JSON content, and returns the resulting list of topics.

        Returns:
            list: A list of topics loaded from the JSON file.
        """
        with open("/etc/vyomcloudbridge/machine_topics.json", "r") as f:
            serialised_topic_list = json.load(f)
        return serialised_topic_list

    def replace_nan_with_null(self, obj):
        """
        Recursively traverse the input object and replace all float NaN values with None.
        This ensures compatibility with JSON serialization, where None is converted to null.
        """
        if isinstance(obj, dict):
            return {k: self.replace_nan_with_null(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.replace_nan_with_null(item) for item in obj]
        elif isinstance(obj, float) and math.isnan(obj):
            return None
        else:
            return obj

    def send_summary(self, summary):
        self.logger.debug(f"Summary {summary}")
        
        self.writer.write_message(
            message_data=summary,
            data_type="json",
            data_source="mission_summary",
            destination_ids=["gcs_mav"],
            filename=None,
            mission_id=self.mission_id,
            project_id=None,
            priority=3,
            merge_chunks=True,
            expiry_time_ms=5000,
            background=True
        )

        self.writer.write_message(
            message_data=summary,
            data_type="json",
            data_source="mission_summary",
            destination_ids=["s3", "gcs_mqtt"],
            filename=None,
            mission_id=self.current_mission.get("id"),
            project_id=None,
            priority=3,
            merge_chunks=True,
            send_live=True,
            background=True
        )

    def update_mission_id(self):
        self.current_mission, error = self.get_current_mission()

        if self.current_mission is None:
            return default_mission_id
        self.logger.debug(f"self.current_mission: {self.current_mission}")

        if self.current_mission.get("mission_status") == 1:
            self.summariser.set_mission_mode(1)
            return self.current_mission.get("id") or default_mission_id

        if self.current_mission.get("mission_status") == 2:
            if self.summariser.get_mission_mode() == 1:
                self.logger.debug("stopped")
                # self.summariser.print_summary()
                # self.send_summary(self.summariser.print_summary())
                # self.summariser.set_mission_mode(2)
                # self.summariser.reset()

        return default_mission_id

    def create_listener_function(self, f_msg_data_type, f_topic_name, f_topic, f_send_live, f_data_upload_frequency, f_save_locally):
        """
        Creates a listener function for processing incoming messages of a specific type and topic.

        The generated listener function performs the following:
            - Converts the incoming message to the desired format using a converter.
            - Extracts a timestamp from the message header if available.
            - Constructs a filename based on the current epoch time and a padding value.
            - Differentiates between image and JSON data types.
            - Prepares the extracted data for writing, including metadata such as timestamp,
              topic, mission ID, and the converted data.
            - Writes the processed data to a destination using the `self.writer.write_message` method.
        """

        # eg: f_msg_data_type=vyom_mission_msgs.msg.MissionStatus, f_topic_name=MISSION_TOPIC
        def callback(msg):
            if self.current_mission.get("mission_status") == 1:
                self.logger.debug("Mission is in progress, updating summariser")
                self.summariser.update(f_topic, msg)

            self.logger.debug(f"Ros data processing for ros_topic: {f_topic_name}")

            tracker = self._freq_tracker[f_topic_name]
            now = self._clock.now().nanoseconds / 1e9
            should_log, upload_freq, msg_freq = should_throttle(tracker, f_data_upload_frequency, now)
            
            if should_log:
                self.logger.info(
                    f"[{f_topic_name}] Msg Freq: {msg_freq:.2f} Hz | "
                    f"Upload Freq: {upload_freq:.2f} Hz | Msg: {msg}"
                )

                current_value = converter.convert(f_msg_data_type, 1, msg)

                cleaned_value = self.replace_nan_with_null(current_value)
                epoch_ms = int(time.time() * 1000)

                if (f_msg_data_type == "sensor_msgs.msg.Image" and f_msg_data_type.__module__ == "sensor_msgs.msg.Image"):
                    filename = f"{epoch_ms}.jpeg"
                    data_type = "image"
                    extracted_data = cleaned_value
                else:
                    filename = f"{epoch_ms}.json"
                    data_type = "json"
                    
                    timenow = time.time()
                    timestamp_sec = int(timenow)
                    timestamp_nsec = int((timenow - timestamp_sec) * 1_000_000_000)

                    extracted_data = {
                        "timestamp": {
                            "seconds": timestamp_sec,
                            "nanoseconds": timestamp_nsec,
                        },
                        "key": f_topic_name,
                        "mission_id": self.mission_id,
                        "data": {},
                    }
                    extracted_data["data"] = cleaned_value

                self.logger.debug(
                    f"Logs data type: {type(cleaned_value)}, filename: {filename}, data_type: {data_type} epoch_ms"
                )

                # Get mission id
                self.mission_id = self.update_mission_id()
                self.logger.info(f"self.mission_id: {self.mission_id}")

                if f_save_locally:
                    # Save the data locally
                    self.logger.info(f"Saving locally for: {f_topic_name}")

                    local_path = f"/var/log/vyomcloudbridge/mission_data/{self.mission_id}/{f_topic_name}"
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    with open(local_path, "a") as file:
                        if data_type == "image":
                            file.write(extracted_data)
                        else:
                            json.dump(extracted_data, file)

                else:
                    self.logger.info(f"Sending data for: {f_topic_name}")
                    success, error = self.writer.write_message(
                        message_data=extracted_data,  # json data
                        filename=filename,  # nullable or epoch time
                        data_source=f_topic_name,  # telemetry, mission_summary
                        data_type=data_type,  # file, video, image
                        mission_id=self.mission_id,  # mission_id
                        priority=1,  # 1  for velocity data, battery topic, and ROS data
                        destination_ids=["s3"],  # ["s3"]
                        merge_chunks=True,  # True for telemetry data
                        send_live=f_send_live,
                    )
                    self.writer.write_message(
                        message_data=extracted_data,  # json data
                        filename=filename,  # nullable or epoch time
                        data_source=f_topic_name,  # telemetry, mission_summary
                        data_type=data_type,  # file, video, image
                        mission_id=self.mission_id,  # mission_id
                        priority=1,  # 1  for velocity data, battery topic, and ROS data
                        destination_ids=["gcs_mqtt"],  # ["s3"] ["gcs_mqtt" via mqtt]
                        merge_chunks=True,  # True for telemetry data
                        send_persistent=False,
                        send_live=f_send_live,
                    )
                    if success:
                        self.logger.debug(
                            f"Successlly sent to S3 {success} for topic: {f_topic_name}"
                        )
                    elif error:
                        self.logger.error(
                            f"Not sent to S3. Error {error} for topic: {f_topic_name}"
                        )
                    else:
                        self.logger.info(
                            f"Not sent to S3. Status unknown for topic: {f_topic_name}"
                        )
                self.logger.info(f"Ros data processed for ros_topic: {f_topic_name}")

        return callback

    def import_class_from_string(self, class_string):
        """
        Dynamically imports and returns a class from its string representation.

        Args:
            class_string (str): A string representation of the class to import.
                The string can be in the format "<class 'module.submodule.ClassName'>"
                or simply "module.submodule.ClassName".

        Returns:
            type: The class object corresponding to the given string representation.
        """
        class_string = class_string.strip()
        if class_string.startswith("<class '") and class_string.endswith("'>"):
            # Extract the part between the quotes
            class_path = class_string[8:-2]  # Remove "<class '" and "'>"
        else:
            class_path = class_string

        # Split into module path and class name
        parts = class_path.split(".")
        module_path = ".".join(parts[:-1])
        class_name = parts[-1]

        # Import the module dynamically
        module = importlib.import_module(module_path)

        return getattr(module, class_name)

    def create_dynamic_subscribers(self, f_topic,f_subscribers):
        """
        Dynamically creates and adds a subscriber to the list of subscribers.
        This method takes a topic configuration, creates a subscription for the
        specified data type and topic path, and appends it to the `subscribers` list.

        Args:
            f_topic (dict): A dictionary containing the topic configuration with the following keys:
                - "data_type" (str): The fully qualified class name of the data type to subscribe to.
                - "path" (str): The topic path to subscribe to.
                - "name" (str): The name of the topic.
        """
        try:
            if "camera" in f_topic['topic'].lower():
                qos_profile = self.camera_qos
            else:
                qos_profile = self.m_qos
                
            f_subscribers.append(
                self.create_subscription(
                    self.import_class_from_string(f_topic["data_type"]),
                    f_topic["topic"],
                    self.create_listener_function(
                        f_topic["data_type"], f_topic["name"], f_topic["topic"], f_topic["send_live"], f_topic["frequency"], f_topic["save_locally"]
                    ),
                    callback_group=self.callback_group,
                    qos_profile=qos_profile,
                )
            )
            self.logger.info(f"Subscribed to topic: {f_topic['topic']} with type: {f_topic['data_type']}")
        except Exception as e:
            self.logger.error(
                f"Failed to subscribe to topic: {f_topic['topic']} with type: {f_topic['data_type']}. Error: {e}"
            )

    def subscriber_shutdown(self):
        """Shuts down all active subscribers and resets related variables."""
        self.is_running = False
        self.logger.info("Shutting down all subscribers.")

        # Explicitly destroy all subscriptions
        for subscriber in self.machine_subscribers:
            self.destroy_subscription(subscriber)

        self.machine_subscribers.clear()

    def start(self):
        pass

    def stop(self):
        pass

    def cleanup(self):
        pass


class RosPublisher(ServiceAbstract):
    def __init__(self):
        super().__init__()
        self.logger.info("Initializing RosPublisher..")
        self.is_running = False
        self.spin_thread = None
        self.mission_stats = MissionStats()
        self.get_current_mission = self.mission_stats.get_current_mission
        try:
            rclpy.init(args=None)
        except Exception as e:
            self.logger.warning(f"Failed to initialize ROS: {e}")

        self.send_data_to_server = SendDataToServer(self.get_current_mission)
        self.logger.info("RosPublisher Initialized successfully")

    def start(self):
        try:
            self.logger.info("Starting RosPublisher service...")
            self.is_running = True

            self.send_data_to_server.create_subscribers()
            def start_proccess():
                rclpy.spin(self.send_data_to_server)
                while self.is_running:
                    time.sleep(10)

            self.stats_thread = threading.Thread(target=start_proccess, daemon=True)
            self.stats_thread.start()
            self.logger.info("RosPublisher service started!")

        except Exception as e:
            self.logger.error(f"Error starting RosPublisher service: {str(e)}")
            self.stop()

    def stop(self):
        try:
            self.is_running = False
            self.send_data_to_server.subscriber_shutdown()
            rclpy.shutdown()
            self.spin_thread.join()
            self.logger.info("Shutdown complete. RosPublisher service stopped!")
        except Exception as e:
            self.logger.error(f"Error in stoping RosPublisher: {str(e)}")

    def cleanup(self):
        try:
            self.mission_stats.cleanup()
        except Exception as e:
            self.logger.error(f"----")

    def is_healthy(self):
        return self.is_running

    def __del__(self):
        """Destructor called by garbage collector to ensure resources are cleaned up, when object is about to be destroyed"""
        try:
            self.logger.error(
                "Destructor called by garbage collector to cleanup RosPublisher"
            )
            self.stop()
        except Exception as e:
            pass


def main(args=None):
    data_streamer = RosPublisher()
    try:
        data_streamer.start()
        time.sleep(100)
    finally:
        data_streamer.stop()
    print("Completed SendDataToServer service example")

if __name__ == "__main__":
    main()