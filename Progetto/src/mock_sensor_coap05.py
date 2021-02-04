import sys
from sensor import MockSensor
from sensor import MockSub
import datetime
import logging
import json
import asyncio
from time import sleep
import aiocoap.resource as resource
import aiocoap
import os
import sensor
import threading
import fos_utils

'''
Needed from Environment
"nuuid"
"fuuid"
"iuuid"
"label" 
"port"
'''


class MockSensorCoap05(resource.ObservableResource, MockSub):
    """Call `update_state` to trigger sending notifications."""

    def __init__(self, mock_sensor: MockSensor):
        super().__init__()
        # sensor init
        self.sensor = mock_sensor
        self.sensor.subscribe(self)
        # fog05 env parameters loading
        self.nuuid = os.environ["nuuid"]
        self.fuuid = os.environ["fuuid"]
        self.iuuid = os.environ["iuuid"] if "iuuid" in os.environ else "mock-sensor-coap"
        self.label = os.environ["label"] if "label" in os.environ else "sensor-coap"
        self.port = int(os.environ["port"]) if "port" in os.environ else 9050

        # self.uri_uuid = "coap://" + \
        #                 self.config.get("hostname", "localhost") + ":" + \
        #                 str(self.config.get("port", "9500")) + "/" + \
        #                 self.iuuid
        #
        # self.uri_label = "coap://" + \
        #                  self.config.get("hostname", "localhost") + ":" + \
        #                  str(self.config.get("port", "9500")) + "/" + \
        #                  self.label
        #
        # print(self.uri_uuid)
        # print(self.uri_label)

        root = resource.Site()
        root.add_resource(['.well-known', 'core'],
                          resource.WKCResource(root.get_resources_as_linkheader))
        root.add_resource([self.iuuid], self)
        root.add_resource([self.label], self)

        # IPv6 address needed for create_server_context
        asyncio.Task(aiocoap.Context.create_server_context(root,
                                                           bind=('0:0:0:0:0:ffff:7f00:1',
                                                                 self.port)))
        self.loop = asyncio.get_event_loop()
        asyncio.get_event_loop().run_forever()

    def alert(self, value: int):
        print("mock sensor coap new value from sensor " + str(value))
        self.loop.call_soon_threadsafe(self.notify)
        # self.notify()

    def update_observation_count(self, count):
        print("update_observation_count " + str(count))

    def notify(self):
        # coap observable resource notificator
        self.updated_state()

    def encode_state(self):
        return fos_utils.encode_state({"threshold": self.sensor.threshold,
                                       "delay": self.sensor.delay,
                                       "state": self.sensor.state,
                                       "um": self.sensor.um,
                                       "value": self.sensor.value,
                                       "label": self.label})

    async def render_get(self, request):
        # self.sensor.measure()
        print("new msg get " + str(request.payload))
        return aiocoap.Message(payload=self.encode_state())

    async def render_put(self, request):
        print("new msg put " + str(request.payload))
        msg_json = fos_utils.decode_state(request.payload)
        self.sensor.threshold = msg_json.get("threshold", self.sensor.threshold)
        self.sensor.delay = msg_json.get("delay", self.sensor.delay)
        self.sensor.state = msg_json.get("state", self.sensor.state)
        return aiocoap.Message(payload=self.encode_state())


def main():
    # fog05 real deploy
    # um, delay=1, threshold=0
    MockSensorCoap05(MockSensor(um="cm", delay=2, threshold=95))


def main_test():
    # simulated deploy
    os.environ["nuuid"] = "1"
    os.environ["fuuid"] = "2"
    os.environ["iuuid"] = "3"
    os.environ["label"] = "sensor-coap"
    os.environ["port"] = "9100"
    mock = MockSensor("cm", 2, 5)
    # mock.start_measuring()
    coap_sensor = MockSensorCoap05(mock)


def new_device(config: dict):
    os.environ["nuuid"] = config["nuuid"]
    os.environ["fuuid"] = config["fuuid"]
    os.environ["iuuid"] = config["iuuid"]
    os.environ["label"] = config["label"]
    os.environ["broker"] = config["connector"]["broker"]
    mock = MockSensor("cm", 2, 5)
    MockSensorCoap05(mock)


if __name__ == "__main__":
    main()
    # main_test()
    # _config = json.loads(read_file("system.config"))
    # threading.Timer(1.0, new_device(_config["A"]))
    # threading.Timer(1.0, new_device(_config["C"]))
