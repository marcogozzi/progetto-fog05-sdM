import asyncio
import json

from aiocoap import *
import time


async def main():
    uri = "coap://localhost:9100/act-coap"
    context = await Context.create_client_context()

    request = Message(code=GET, payload="", uri=uri)
    response = await context.request(request).response
    json_p = json.loads(response.payload.decode('utf-8'))

    # request = Message(code=PUT,
    #                   payload=(json.dumps({"state": "execute", "execution_time": 5}).encode('utf-8')),
    #                   uri=uri)
    # response = await context.request(request).response
    # json_p = json.loads(response.payload.decode('utf-8'))

    time.sleep(int(json_p["execution_time"]) + 1)
    request = Message(code=GET, payload="", uri=uri)
    # print(str(request.opt))
    response = await context.request(request).response

    json_p = json.loads(response.payload.decode('utf-8'))
    print(str(json_p))

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
