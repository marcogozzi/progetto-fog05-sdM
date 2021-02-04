import json
import time
from fog05 import FIMAPI
from fog05_sdk.interfaces.FDU import FDU


def read_file(filepath):
    with open(filepath, 'r') as f:
        data = f.read()
    return data


api = FIMAPI('192.168.31.232')
uuid_fisso = '01369aac-9965-4277-96c0-280cf007e953'
uuid_portatile = '9806ff42-cecc-48c1-9f44-da51955d4732'

descs = json.loads(read_file("./system.json"))
for label in descs["devices"]:
    print(label)
    print(descs["devices"][label])
    desc = json.loads(read_file("./" + descs["devices"][label]["desc"]))
    fdu_descriptor = FDU(desc)
    fduD = api.fdu.onboard(fdu_descriptor)
    fdu_id = fduD.get_uuid()
    inst_info = api.fdu.define(fdu_id, '9806ff42-cecc-48c1-9f44-da51955d4732')
    descs["devices"][label]["nuuid"] = uuid_portatile
    descs["devices"][label]["fuuid"] = fdu_id
    descs["devices"][label]["iuuid"] = inst_info.get_uuid()
    api.fdu.configure(inst_info.get_uuid())
    # env = "nuuid=" + uuid_portatile + \
    #       "fuuid=" + fdu_id + \
    #       "iuuid=" + inst_info.get_uuid() + \
    #       "port=" + descs["devices"][label]["connector"].get("port", str(9500)) + \
    #       "ip=" + descs["devices"][label]["connector"].get("ip", str(9500)) + \
    #       "broker=" + descs["devices"][label]["connector"].get("broker", str(9500))
    api.fdu.start(inst_info.get_uuid(), "")
with open("./system.json", "w") as outp:
    json.dump(descs, outp)
api.close()
exit(0)
