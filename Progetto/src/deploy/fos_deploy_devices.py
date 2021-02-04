import json
import time
from fog05 import FIMAPI
from fog05_sdk.interfaces.FDU import FDU


def read_file(filepath):
    with open(filepath, 'r') as f:
        data = f.read()
    return data


json_prova = {"a": "b", "c": "d", "nested": {"aa": "bb", "cc": "dd"}}
api = FIMAPI('192.168.31.232')
uuid_fisso = '01369aac-9965-4277-96c0-280cf007e953'
uuid_portatile = '9806ff42-cecc-48c1-9f44-da51955d4732'

descs = json.loads(read_file("/var/fos/demo/deploy/system.json"))
for label in descs["devices"]:
    print(label)
    print(descs["devices"][label])
    if "desc" in descs["devices"][label]:  # ensure descriptor is onboarded
        desc = json.loads(read_file("/var/fos/demo/deploy/" + descs["devices"][label]["desc"]))
        fdu_descriptor = FDU(desc)
        fduD = api.fdu.onboard(fdu_descriptor)
        fdu_id = fduD.get_uuid()
    elif "fuuid" in descs["devices"][label]:  # FDU descriptor already onboarded
        fdu_id = descs["devices"][label]["fuuid"]
    else:
        continue  # no FDU descriptor available, skip this device
    inst_info = api.fdu.define(fdu_id, descs["devices"][label]["nuuid"])
    descs["devices"][label]["nuuid"] = uuid_portatile
    descs["devices"][label]["fuuid"] = fdu_id
    descs["devices"][label]["iuuid"] = inst_info.get_uuid()
    time.sleep(1)
    api.fdu.configure(inst_info.get_uuid())
    # env = "nuuid=" + uuid_portatile + \
    env = "nuuid=" + descs["devices"][label]["nuuid"] + \
          ",fuuid=" + fdu_id + \
          ",iuuid=" + inst_info.get_uuid() + \
          ",label=" + label + \
          ",port=" + descs["devices"][label]["connector"].get("port", str(9500)) + \
          ",ip=" + descs["devices"][label]["connector"].get("ip", str(9500)) + \
          ",broker=" + descs["devices"][label]["connector"].get("broker", str(9500))
    print(env)
    time.sleep(1)
    api.fdu.start(inst_info.get_uuid(), env)

with open("./system_instance.json", "w") as outp:
    json.dump(descs, outp, indent=4)

# managers
desc = json.loads(read_file("/var/fos/demo/deploy/fdu_manager.json"))
fdu_descriptor = FDU(desc)
fduD = api.fdu.onboard(fdu_descriptor)
fdu_id = fduD.get_uuid()
# replace item separator "," with ";" and double quotes with "%"
# to avoid string splitting during env parsing operation
sys_desc = json.dumps(descs, separators=("^", ":")).replace("\"", "%")
for manager in ["service_x", "service_y"]:
    inst_info = api.fdu.define(fdu_id, '9806ff42-cecc-48c1-9f44-da51955d4732')
    # inst_info = api.fdu.define(fdu_id, descs["devices"][label]["nuuid"])
    time.sleep(1)
    api.fdu.configure(inst_info.get_uuid())
    env = "nuuid=" + uuid_portatile + \
          ",fuuid=" + fdu_id + \
          ",iuuid=" + inst_info.get_uuid() + \
          ",label=" + manager + \
          ",config=" + "/var/fos/demo/" + manager + ".json" + \
          ",system=" + sys_desc
    # delete .json in label
    time.sleep(1)
    api.fdu.start(inst_info.get_uuid(), env)
    time.sleep(1)
api.close()
exit(0)
