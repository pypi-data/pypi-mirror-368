import sqlite3

# pyre-fixme[21]
from rosidl_runtime_py.utilities import get_message

# pyre-fixme[21]
from rclpy.serialization import deserialize_message
from mcap.reader import make_reader
from mcap_ros2.decoder import DecoderFactory


class BagFileParser:
    def __init__(self, bag_file):
        self.bag_file = bag_file
        if bag_file.endswith(".db3"):
            self.conn = sqlite3.connect(bag_file)
            self.cursor = self.conn.cursor()

            # create a message type map
            topics_data = self.cursor.execute(
                "SELECT id, name, type FROM topics"
            ).fetchall()
            self.topic_type = {
                name_of: type_of for id_of, name_of, type_of in topics_data
            }
            self.topic_id = {name_of: id_of for id_of, name_of, type_of in topics_data}
            self.topic_msg_message = {
                name_of: get_message(type_of) for id_of, name_of, type_of in topics_data
            }
        elif bag_file.endswith(".mcap"):
            self.mcap_file = open(bag_file, "rb")
            self.mcap_reader = make_reader(
                self.mcap_file, decoder_factories=[DecoderFactory()]
            )
            self.topic_type = {}
            self.topic_msg_message = {}
            for schema, channel, _, _ in self.mcap_reader.iter_decoded_messages():
                if channel.topic not in self.topic_type:
                    self.topic_type[channel.topic] = schema.name
                    self.topic_msg_message[channel.topic] = get_message(schema.name)

    def __del__(self):
        if hasattr(self, "conn"):
            self.conn.close()
        elif hasattr(self, "mcap_file"):
            self.mcap_file.close()

    def get_messages(self, topic_name):
        """
        Return [(timestamp0, message0), (timestamp1, message1), ...]
        """
        if hasattr(self, "conn"):
            topic_id = self.topic_id[topic_name]
            rows = self.cursor.execute(
                "SELECT timestamp, data FROM messages WHERE topic_id = {}".format(
                    topic_id
                )
            ).fetchall()
            # Deserialize all and timestamp them
            return [
                (
                    timestamp,
                    deserialize_message(data, self.topic_msg_message[topic_name]),
                )
                for timestamp, data in rows
            ]
        elif hasattr(self, "mcap_reader"):
            messages = []
            for (
                schema,
                channel,
                message,
                ros_msg,
            ) in self.mcap_reader.iter_decoded_messages():
                if channel.topic == topic_name:
                    timestamp = message.log_time
                    messages.append((timestamp, ros_msg))
            return messages

    def get_last_message(self, topic_name):
        if hasattr(self, "conn"):
            topic_id = self.topic_id[topic_name]
            timestamp, msg = self.cursor.execute(
                "SELECT timestamp, data FROM messages WHERE topic_id = {} ORDER BY timestamp DESC LIMIT 1".format(
                    topic_id
                )
            ).fetchone()
            return (
                timestamp,
                deserialize_message(msg, self.topic_msg_message[topic_name]),
            )
        elif hasattr(self, "mcap_reader"):
            last_message = None
            for (
                schema,
                channel,
                message,
                ros_msg,
            ) in self.mcap_reader.iter_decoded_messages():
                if channel.topic == topic_name:
                    last_message = (message.log_time, ros_msg)
            return last_message
