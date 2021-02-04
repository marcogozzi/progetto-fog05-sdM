import abc
import threading
import asyncio
import json
import os
from aiocoap import *
import aiocoap.numbers.codes as codes
import time
import fos_utils
import paho.mqtt.client as mqtt


class DeviceCommunicator(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def send(self, action, payload):
        return

    @abc.abstractmethod
    def stop(self):
        return


class Mqtt05Device(DeviceCommunicator):

    def __init__(self, payload_handler, nuuid, fuuid, iuuid, label, name, broker):
        # print("Connector for " + name)
        self.mngr = payload_handler

        self.mqttc = mqtt.Client()
        self.label = label
        self.topic = nuuid + "/" + fuuid + "/" + iuuid if iuuid != "" else nuuid + "/" + fuuid + "/" + label
        self.mqttc.connect(broker)
        self.mqttc.message_callback_add(self.topic, self._on_message_in)
        self.mqttc.subscribe(self.topic, 0)
        self.mqttc.loop_start()

    def _on_message_in(self, client, userdata, message_in):
        print("Mqtt05Device " + self.topic + " received")
        self.mngr(message_in.payload)

    def send(self, action, payload):
        msg_json = fos_utils.decode_state(payload)
        if "action" not in msg_json:
            msg_json["action"] = action
        self.mqttc.publish(self.topic + "/in", payload=fos_utils.encode_state(msg_json))
        print("Mqtt05Device sent to " + self.label + " at " + self.topic)

    def stop(self):
        self.mqttc.loop_stop()


def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()


class Coap05Device(DeviceCommunicator):
    def __init__(self, payload_handler, nuuid, fuuid, iuuid, label, name, ip, port):
        # print("Connector for " + name)
        self.ip = ip
        self.port = port
        self.iuuid = iuuid
        self.label = label
        self.mngr = payload_handler
        self.uri = "coap://" + ip + ":" + port + "/" + iuuid if iuuid != "" \
            else "coap://" + ip + ":" + port + "/" + label
        self.codes = {"PUT": codes.Code.PUT, "GET": codes.Code.GET}
        # asyncio.create_task(_receive()) # only Python 3.7+
        asyncio.get_event_loop().create_task(self._receive())
        # using the Thread class to run a background thread for send operation
        self.background_loop = asyncio.new_event_loop()
        self.t = threading.Thread(target=start_background_loop, args=(self.background_loop,), daemon=True)
        self.t.start()
        # do the sub

    def send(self, action, payload):
        # send using a different thread in order not to block the execution thread
        print("Coap05Device " + self.uri + " sending " + str(payload))
        asyncio.run_coroutine_threadsafe(self._send(action, payload), self.background_loop)
        # self.background_loop.call_soon(self._send, action, payload)
        # asyncio.ensure_future(self._send(action, payload))
        # using a Thread subclass, Timer
        # threading.Timer(0, asyncio.get_event_loop().create_task(self._send(action, payload)).start()) # not tested

    async def _receive(self):
        print("Coap05Device _receive")
        ctx = await Context.create_client_context()
        request = Message(code=codes.Code.GET, uri=self.uri, observe=0)
        self.subscription = ctx.request(request)
        self.subscription.observation.register_callback(self.msg_callback)
        async for msg in self.subscription.observation:
            # print("Coap05Device _receive " + str(msg.payload))
            pass

    def msg_callback(self, coap_message):
        self.mngr(coap_message.payload)

    async def _send(self, action, payload):
        context = await Context.create_client_context()
        print("Coap05Device _send " + action + " to " + self.uri + " payload= " + str(payload))
        # request = Message(code=PUT, payload=json.dumps({"state": "off"}).encode('utf-8'), uri=self.uri)  # works
        # request = Message(code=codes.Code.PUT, payload=json.dumps({"state": "off"}).encode('utf-8'), uri=self.uri)  # works
        # request = Message(code=self.codes[action], payload=json.dumps({"state": "off"}).encode('utf-8'), uri=self.uri)  # works
        request = Message(code=self.codes[action], payload=payload, uri=self.uri)  # works

        response = await context.request(request).response
        print("Coap05Device _send done with response   " + str(response.payload))
        self.mngr(response.payload)

    def stop(self):
        self.subscription.observation.cancel()  # stop CoAP subscription
        self.background_loop.stop()


def get_connector(config, handler):
    # (self, nuuid, fuuid, iuuid, broker, payload_handler)
    if config["connector"]["name"] == "mqtt":
        return Mqtt05Device(handler, config["nuuid"], config["fuuid"],
                            config["iuuid"], config["label"], **config["connector"])
    # (self, ip, port, label, payload_handler)
    elif config["connector"]["name"] == "coap":
        return Coap05Device(handler, config["nuuid"], config["fuuid"],
                            config["iuuid"], config["label"], **config["connector"])


class manager:

    def __init__(self):
        self.devices = {}

    def payload_handler(self, payload):
        # get json dict of state received
        content = fos_utils.decode_state(payload)
        # extract sending-device label and update the state representation
        self.devices[content["label"]]["state"] = content
        return content


'''
Needed from Environment
"nuuid"
"fuuid"
"iuuid"
"label" 
"config" # path to mappings configuration file
'''


class manager05(manager):

    def __init__(self):
        # fog05 env parameters loading
        super().__init__()
        self.nuuid = os.environ["nuuid"] if "nuuid" in os.environ else "no_nuiid"
        self.fuuid = os.environ["fuuid"] if "fuuid" in os.environ else "no_fuuid"
        self.iuuid = os.environ["iuuid"] if "iuuid" in os.environ else "manager05"
        self.label = os.environ["label"] if "label" in os.environ else "manager05"
        # if system instance description is given through Env variable
        if "system" in os.environ:
            self.config = json.loads(os.environ["system"].replace("^", ", ").replace("%", "\"").replace(":", ": "))
        else:
            self.config = json.loads(fos_utils.read_file("/var/fos/demo/deploy/system_instance.json"))
        self.mappings = json.loads(fos_utils.read_file(os.environ["config"]))
        self.lock = threading.Lock()

        self.critic = False
        if "A" in self.mappings.keys() and "B" in self.mappings.keys():
            from fog05 import FIMAPI
            from fog05_sdk.interfaces.FDU import FDU
            self.critic = True
            self.critic_nodes = {self.config["devices"]["A"]["nuuid"], self.config["devices"]["B"]["nuuid"]}
            self.fos_api = FIMAPI(self.config.get("fimapi", "192.168.31.232"))
            print("+++ this is the critic manager +++")
            if "json" in self.config["fdu_control"]:  # if descriptor is a filename, load it in fog05
                print("fog05 onboarding " + self.config["fdu_control"])
                fdu_descriptor = FDU(json.loads(fos_utils.read_file(self.config["fdu_control"])))
                fduD = self.fos_api.fdu.onboard(fdu_descriptor)
                self.config["fdu_control"] = fduD.get_uuid()

        # rebuild with factory
        # iterate on keys (i.e. labels)
        # create a set of all the managed labels
        devices = set(self.mappings.keys())
        for label in self.mappings.keys():
            for mapping in self.mappings[label]:
                devices.add(mapping["label"])
        print(str(devices))
        # for device in self.config["devices"]:
        for device in devices:
            self.devices[device] = {}
            self.devices[device]["connector"] = get_connector(self.config["devices"][device], self.payload_handler)
            # self.devices[device["label"]] = get_connector(device["connector"], self.payload_handler)

        for label in self.devices.keys():
            if "sens" in self.config["devices"][label]["desc"]:
                payload = {"action": "PUT", "state": "on"}
                # print("Manager turning on sensor " + label + " with msg " + str(payload))
                self.devices[label]["connector"].send("PUT", fos_utils.encode_state(payload))
        # for device in self.config["devices"]:
        # (self, nuuid, fuuid, iuuid, broker, payload_handler)
        # self.devices[device["label"]] = Mqtt05_comm(device["nuuid"],
        #                                             device["fuuid"],
        #                                             device["iuuid"],
        #                                             device["broker"],
        #                                             self.payload_handler)
        # # (self, ip, port, label, payload_handler)
        # self.devices[device["label"]] = Coap05_comm(device["ip"],
        #                                             device["port"],
        #                                             device["iuuid"],
        #                                             device["label"],
        #                                             self.payload_handler)
        asyncio.get_event_loop().run_forever()

    """
    If incoming message is from an appropriate device (as defined in config file)
    Send the given configuration to the mapped device 
    """

    def payload_handler(self, payload):
        # update state
        content = {}
        with self.lock:
            content = super().payload_handler(payload)
            if self.critic:
                self.devices[content["label"]]["last_update"] = int(time.time())
        # execute actions
        mappings = self.mappings[content["label"]]
        for mapping in mappings:
            self.devices[mapping["label"]]["connector"].send("PUT", fos_utils.encode_state(mapping))
        if self.critic and (content["label"] == "A" or content["label"] == B):
            time_delta = self.devices["A"].get("last_update", 100) - self.devices["A"].get("last_update", 0)
            if -5 < time_delta < 5:
                print("deploy maintenance fog05")
                for node in self.critic_nodes:
                    self.fos_api.fdu.instantiate(self.config["fdu_control"], node, wait=False)
                # reset timestamps so that two more alarms have to arrive to trigger another control
                self.devices["A"]["last_update"] = 100
                self.devices["A"]["last_update"] = 0
        return content


def main():
    # fog05 real deploy
    # os.environ["config"] = "deploy/system_instance.json"
    manager05()


def main_test():
    # simulated deploy
    os.environ["config"] = "deploy/system_instance.json"
    dev = Coap05Device(prints, "1", "2", "", "B", "name", "localhost", "9500")
    dev.send("PUT", fos_utils.encode_state({"state": "off"}))
    asyncio.get_event_loop().run_forever()


def prints(string):
    print(string)


if __name__ == "__main__":
    main()
    # main_test()

# class TestSuper:
#     def __init__(self):
#         self.a = "a"
#     def base(self, arg):
#         return self.a + arg
#
#
# class TestSub(TestSuper):
#     def __init__(self):
#         super().__init__()
#         self.b = "b"
#     def base(self, arg):
#         returned = super().base(arg)
#         print(returned + " << " + arg)
