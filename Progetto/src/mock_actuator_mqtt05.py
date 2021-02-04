from time import sleep
import sys
import os
import json
from actuator import MockTimedActuator
from actuator import MockSub
import threading
import paho.mqtt.client as mqtt
import paho.mqtt.publish as mqtt_pub
import random
import fos_utils

'''
Needed from Environment
"nuuid"
"fuuid"
"iuuid"
"label" 
"broker"
'''


class MockActMqtt05(MockSub):

    def __init__(self, mock_actuator: MockTimedActuator):
        # actuator init
        self.actuator = mock_actuator
        self.actuator.subscribe(self)

        # fog05 env parameters loading
        self.nuuid = os.environ["nuuid"]
        self.fuuid = os.environ["fuuid"]
        self.iuuid = os.environ["iuuid"] if "iuuid" in os.environ else "mock-actuator-mqtt"
        self.label = os.environ["label"] if "label" in os.environ else "actuator-mqtt"
        self.broker = os.environ["broker"]

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
        return fos_utils.encode_state({"execution_time": self.actuator.execution_time,
                                       "state": self.actuator.state,
                                       "label": self.label})

    def alert(self, value: int):
        self.advert()

    def advert(self):
        representation = {"execution_time": self.actuator.execution_time,
                          "state": self.actuator.state,
                          "label": self.label}
        print("\tadvert!! -> " + json.dumps(representation))
        self.mqttc.publish(self.topic_uuid, payload=self.encode_state())
        self.mqttc.publish(self.topic_label, payload=self.encode_state())

    def on_message_in(self, client, userdata, message):
        # dict msg_json
        # print("custom message callback")
        # print(message.payload)
        msg_json = fos_utils.decode_state(message.payload)
        # if msg_json["action"] == "GET":
        if msg_json["action"] == "PUT":
            # dict.get(key, default) returns value associated to key if key exists, default if not
            self.actuator.execution_time = msg_json.get("execution_time", self.actuator.execution_time)
            self.actuator.state = msg_json.get("state", self.actuator.state)
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
                        "state": "execute",
                    }).encode('UTF-8'))
    sleep(7)
    mqtt_pub.single("1/2/3/in",
                    json.dumps({
                        "action": "GET"
                    }).encode('UTF-8'))
    mqtt_pub.single("1/2/3/in",
                    json.dumps({
                        "action": "PUT",
                        "execution_time": 6,
                        "state": "execute"
                    }).encode('UTF-8'))


def new_device(config: dict):
    os.environ["nuuid"] = config["nuuid"]
    os.environ["fuuid"] = config["fuuid"]
    os.environ["iuuid"] = config["iuuid"]
    os.environ["label"] = config["label"]
    os.environ["ip"] = config["connector"]["ip"]
    os.environ["port"] = config["connector"]["port"]
    mock = MockTimedActuator()
    MockActMqtt05(mock)


def main():
    # fog05 real deploy
    filepath = os.environ["filepath"] if "filepath" in os.environ else "/var/fos/no-file-name"
    MockActMqtt05(MockTimedActuator(file_name=filepath))


def main_test():
    # simulated deploy
    os.environ["nuuid"] = "1"
    os.environ["fuuid"] = "2"
    os.environ["iuuid"] = "3"
    os.environ["label"] = "act-mqtt"
    os.environ["port"] = "9100"
    mock = MockTimedActuator()
    # mqtt_actuator = MockActMqtt05(mock)


if __name__ == "__main__":
    main()
    # main_test()
    # _config = json.loads(read_file("system.config"))
    # threading.Timer(1, new_device(_config["A"])).start()
    # threading.Timer(1, new_device(_config["C"])).start()
