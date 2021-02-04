import asyncio
import json

from aiocoap import *
import time


async def main():
    # uri = "coap://localhost:9100/sensor-coap"  # test
    uri = "coap://localhost:9500/B"  # fog deploy
    ctx = await Context.create_client_context()
    request = Message(code=GET, uri=uri, observe=0)
    subscription = ctx.request(request)
    subscription.observation.register_callback(prints)
    resp = await subscription.response
    print("Coap05Device " + uri + " first received" + str(resp.payload))

    # request2 = Message(code=PUT, uri=uri, payload=(json.dumps({"state": "off"})).encode('utf-8'))
    # subscription2 = ctx.request(request2)
    # resp2 = await subscription2.response
    # print("Coap05Device " + uri + " state_ON received" + str(resp2))

    async for msg in subscription.observation:
        pass
        # print("")
        # print("")
        # print("Coap05Device " + uri + " received \t\t\t" + str(msg.payload.decode('utf-8')))
        # request = Message(code=GET, uri=uri)
        # subscription = ctx.request(request)
        # resp = await subscription.response
        # print("Coap05Device " + uri + " successive received\t" + str(resp.payload.decode('utf-8')))


def prints(msg):
    print("prints " + msg.payload.decode('utf-8'))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
