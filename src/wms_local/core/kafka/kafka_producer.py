import json
from kafka import KafkaProducer
from ...model.wms_local import KafkaError
from ...core.log_json import Log


log = Log("kafka_producer")


class KafkaPublishMessage:
    """
        Class phục vụ việc publish message lên hệ thống kafka
        Các method implement:
        - Publish single message
        - Publish multiple message
        - Handle error khi publish (save kafka error to db)
    """
    def __init__(self, kafka_bootstrap_server, service_code):
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_server,
            retries=2,
            value_serializer=lambda m: json.dumps(m).encode("ascii")
        )
        self.kafka_bootstrap_server = kafka_bootstrap_server
        self.service_code = service_code

    def publish_single_message(self, topic, message):
        self.kafka_producer.send(topic=topic, value=message)

    def publish_multiple_message(self, topic, list_message):
        for message in list_message:
            try:
                future = self.kafka_producer.send(topic=topic, value=message)
                future.get(timeout=8)
            except BaseException as exc:
                log.error(str(exc))
                self.save_kafka_error(topic, message)

    def save_kafka_error(self, topic, message):
        kafka_error = KafkaError(
            services=self.service_code,
            kafka_cluster=self.kafka_bootstrap_server,
            kafka_topic=topic,
            msg=message,
            success=0
        )
        kafka_error.save()
