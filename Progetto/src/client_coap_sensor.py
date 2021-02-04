import asyncio
import json

from aiocoap import *
import time


async def main():
    # uri = "coap://localhost:9100/sensor-coap"
    uri = "coap://localhost:9500/B"
    context = await Context.create_client_context()

    request = Message(code=GET, payload="", uri=uri)
    response = await context.request(request).response
    print(str(response.payload))
    print(str(response))
    json_p = json.loads(response.payload.decode('utf-8'))
    print(str(json_p))

    # request = Message(code=PUT,
    #                   payload=(json.dumps({"state": "on"}).encode('utf-8')),
    #                   uri=uri)
    # response = await context.request(request).response
    # json_p = json.loads(response.payload.decode('utf-8'))
    # print(str(json_p))
    # time.sleep(20)
    #
    # request = Message(code=GET, payload="", uri=uri)
    # # print(str(request.opt))
    # response = await context.request(request).response
    #
    # json_p = json.loads(response.payload.decode('utf-8'))
    # print(str(json_p))
    #
    # time.sleep(5)
    #
    # request = Message(code=PUT,
    #                   payload=(json.dumps({"state": "off"}).encode('utf-8')),
    #                   uri=uri)
    # response = await context.request(request).response
    # json_p = json.loads(response.payload.decode('utf-8'))
    # print(str(json_p))

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
