import abc
import json
from kafka import KafkaProducer
from ...constant import KAFKA_BOOTSTRAP_SERVER
from ...system_config import get_system_config_by_key, update_system_config
from ...log_manager import LOG_CELERY_TASK


class SyncDataKafka:
    def __init__(self, system_config_key, kafka_topic):
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
            retries=2,
            value_serializer=lambda m: json.dumps(m).encode("ascii")
        )
        self.system_config_key = system_config_key
        self.kafka_topic = kafka_topic
        self.previous_id_sync = get_system_config_by_key(key=system_config_key)
        if self.previous_id_sync is None:
            LOG_CELERY_TASK.warn("Not config {}".format(system_config_key))
            raise Exception("SYSTEM CONFIG is disabled for {}".format(system_config_key))

    def publish_kafka_message(self, message):
        print("publish kafka: ", message)
        self.kafka_producer.send(self.kafka_topic, value=message)

    @abc.abstractmethod
    def get_data_sync(self):
        """
        Implement this method:
            - Get data sync from database
            - Get max_id_sync to new id
        """
        return list(), self.previous_id_sync

    def update_current_sync_id(self, new_value):
        update_system_config(key=self.system_config_key, value=new_value)

    def run_sync(self):
        list_sync_data, max_id = self.get_data_sync()
        # publish all messages
        for data in list_sync_data:
            self.publish_kafka_message(data)
        # update new sync data id
        self.update_current_sync_id(new_value=max_id)
        return len(list_sync_data)
