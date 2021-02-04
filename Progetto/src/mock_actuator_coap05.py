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
from actuator import MockTimedActuator
import fos_utils

'''
Needed from Environment
"nuuid"
"fuuid"
"iuuid"
"label" 
"port"
"filepath"
'''


class MockActCoap05(resource.ObservableResource, MockSub):
    """Call `update_state` to trigger sending notifications."""

    def __init__(self, mock_actuator: MockTimedActuator):
        super().__init__()
        # actuator init
        self.actuator = mock_actuator
        self.actuator.subscribe(self)
        # fog05 env parameters loading
        self.nuuid = os.environ["nuuid"]
        self.fuuid = os.environ["fuuid"]
        self.iuuid = os.environ["iuuid"] if "iuuid" in os.environ else "mock-actuator-coap"
        self.label = os.environ["label"] if "label" in os.environ else "actuator-coap"
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

        root = resource.Site()
        root.add_resource(['.well-known', 'core'],
                          resource.WKCResource(root.get_resources_as_linkheader))
        root.add_resource([self.iuuid], self)
        root.add_resource([self.label], self)

        # IPv6 address needed for create_server_context
        asyncio.Task(aiocoap.Context.create_server_context(root,
                                                           bind=('0:0:0:0:0:ffff:7f00:1',
                                                                 self.port)))
        print("Act coap " + self.label + " port " + str(self.port))
        self.loop = asyncio.get_event_loop()
        asyncio.get_event_loop().run_forever()

    def alert(self, value: int):
        self.loop.call_soon_threadsafe(self.notify)

    def notify(self):
        # coap observable resource notificator
        self.updated_state()

    def encode_state(self):
        return fos_utils.encode_state({"execution_time": self.actuator.execution_time,
                                       "state": self.actuator.state,
                                       "label": self.label})

    async def render_get(self, request):
        return aiocoap.Message(payload=self.encode_state())

    async def render_put(self, request):
        print("Act coap put " + self.label + " port " + str(self.port))
        msg_json = fos_utils.decode_state(request.payload)
        self.actuator.execution_time = msg_json.get("execution_time", self.actuator.execution_time)
        self.actuator.state = msg_json.get("state", self.actuator.state)
        print(str(msg_json))
        print(self.encode_state())
        return aiocoap.Message(payload=self.encode_state())


def main():
    # fog05 real deploy
    filepath = os.environ["filepath"] if "filepath" in os.environ else "/var/fos/no-file-name"
    MockActCoap05(MockTimedActuator(file_name=filepath))


def main_test():
    # simulated deploy
    os.environ["nuuid"] = "1"
    os.environ["fuuid"] = "2"
    os.environ["iuuid"] = "3"
    os.environ["label"] = "act-coap"
    os.environ["port"] = "9100"
    mock = MockTimedActuator()
    coap_act = MockActCoap05(mock)


if __name__ == "__main__":
    main()
    # main_test()
