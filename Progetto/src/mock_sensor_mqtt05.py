from time import sleep
import sys
import os
import json
from sensor import MockSensor
from sensor import MockSub
import threading
import fos_utils
import paho.mqtt.client as mqtt
import paho.mqtt.publish as mqtt_pub
import random

'''
Needed from Environment
"nuuid"
"fuuid"
"iuuid"
"label" 
"broker"
'''


class MockSensorMqtt05(MockSub):

    def __init__(self, mock_sensor: MockSensor):

        # sensor init
        self.sensor = mock_sensor
        self.sensor.subscribe(self)

        # fog05 env parameters loading
        self.nuuid = os.environ["nuuid"] if "nuuid" in os.environ else "1"
        self.fuuid = os.environ["fuuid"] if "fuuid" in os.environ else "1"
        self.iuuid = os.environ["iuuid"] if "iuuid" in os.environ else "mock-sensor-mqtt"
        self.label = os.environ["label"] if "label" in os.environ else "sensor-mqtt"
        self.broker = os.environ["broker"] if "nuuid" in os.environ else "localhost"
        self.topic_uuid = self.nuuid + "/" + self.fuuid + "/" + self.iuuid
        self.topic_label = self.nuuid + "/" + self.fuuid + "/" + self.label

        self.mqttc = mqtt.Client()
        self.mqttc.message_callback_add(self.topic_uuid + "/in", self.on_message_in)
        self.mqttc.message_callback_add(self.topic_label + "/in", self.on_message_in)
        self.mqttc.connect(self.broker)
        self.mqttc.subscribe(self.topic_uuid + "/in", 0)
        self.mqttc.subscribe(self.topic_label + "/in", 0)

        self.mqttc.loop_forever()
        # self.mqttc.loop_start()
        # test
        # self.advert()

    def encode_state(self):
        return fos_utils.encode_state({"threshold": self.sensor.threshold,
                                       "delay": self.sensor.delay,
                                       "state": self.sensor.state,
                                       "um": self.sensor.um,
                                       "value": self.sensor.value,
                                       "label": self.label})

    def alert(self, value: int):
        self.advert()

    def advert(self):
        representation = {"threshold": self.sensor.threshold, "delay": self.sensor.delay,
                          "state": self.sensor.state, "um": self.sensor.um, "value": self.sensor.value,
                          "label": self.label}
        print("\tadvert!! -> " + json.dumps(representation))
        self.mqttc.publish(self.topic_uuid, payload=self.encode_state())
        self.mqttc.publish(self.topic_label, payload=self.encode_state())

    def on_message_in(self, client, userdata, message):
        msg_json = fos_utils.decode_state(message.payload)
        if msg_json["action"] == "GET":
            self.sensor.measure()
        elif msg_json["action"] == "PUT":
            # dict.get(key, default) returns value associated to key if key exists, default if not
            self.sensor.threshold = msg_json.get("threshold", self.sensor.threshold)
            self.sensor.delay = msg_json.get("delay", self.sensor.delay)
            self.sensor.state = msg_json.get("state", self.sensor.state)
        self.advert()


def test():
    print(" in test ")
    mqtt_pub.single("1/2/3/in",
                    json.dumps({
                        "action": "GET"
                    }).encode('UTF-8'))
    sleep(5)
    mqtt_pub.single("1/2/3/in",
                    json.dumps({
                        "action": "PUT",
                        "state": "on",
                        "delay": 1
                    }).encode('UTF-8'))
    sleep(7)
    mqtt_pub.single("1/2/3/in",
                    json.dumps({
                        "action": "PUT",
                        "state": "off"
                    }).encode('UTF-8'))


def main():
    # fog05 real deploy
    # um, delay=1, threshold=0
    MockSensorMqtt05(MockSensor(um="cm", delay=2, threshold=95))
    # simulated deploy
    # os.environ["nuuid"] = "1"
    # os.environ["fuuid"] = "2"
    # os.environ["iuuid"] = "3"
    # os.environ["broker"] = "localhost"
    # threading.Timer(5, test).start()  # testing, subscribe to topic 1/2/3
    #
    # mock = MockSensor("cm", 2, 5)
    # mqtt_sensor = MockSensorMqtt05(mock)


if __name__ == "__main__":
    main()
