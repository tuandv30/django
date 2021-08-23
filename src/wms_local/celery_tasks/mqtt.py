import paho.mqtt.client as mqtt


class MqttServices:
    def __init__(self, host, port, user, pwd):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(user, pwd)
        self.mqtt_client.connect(host=host, port=port, keepalive=60)
        # self.mqtt_client.on_disconnect = on_disconnect

    def publish_messages(self, topic, payload, qos=0):
        self.mqtt_client.publish(topic=topic, payload=payload, qos=qos)

    def disconnect(self):
        self.mqtt_client.disconnect()
