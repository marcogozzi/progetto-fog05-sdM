import json
import time
from fog05 import FIMAPI
from fog05_sdk.interfaces.FDU import FDU

BROKER_IP='192.168.31.232'

def read_file(filepath):
	with open(filepath, 'r') as f:
		data = f.read()
	return data

api = FIMAPI(BROKER_IP)
uuid_fisso = '01369aac-9965-4277-96c0-280cf007e953'
uuid_portatile = '9806ff42-cecc-48c1-9f44-da51955d4732'


desc = json.loads(read_file('./fdu_migra_rel.json'))


fdu_descriptor =  FDU(desc)
fduD = api.fdu.onboard(fdu_descriptor)
fdu_id = fduD.get_uuid()
print('fdu_id: {}'.format(fdu_id))


# local-node specific section
inst_info=api.fdu.define(fdu_id,'01369aac-9965-4277-96c0-280cf007e953')
api.fdu.configure(inst_info.get_uuid())
api.fdu.start(inst_info.get_uuid(), "sleep_period=10,iterations=60,env_output=state_test_f")

time.sleep(20)
# api.fdu.pause(inst_info.get_uuid()) # at the moment not implemented

# remote-node specific section
inst_info_remote=api.fdu.define(fdu_id,'9806ff42-cecc-48c1-9f44-da51955d4732')
api.fdu.configure(inst_info_remote.get_uuid())
api.fdu.start(inst_info_remote.get_uuid(), "sleep_period=10,iterations=60,env_output=state_test_p,load_state=yes")


api.fdu.pause(inst_info.get_uuid())
with open('/home/marco/fos/new/' + inst_info.get_uuid(), 'w') as uuid_old:
	uuid_old.write(inst_info_remote.get_uuid())
	uuid_old.write("\n")
	uuid_old.write("192.168.31.232")

# scp-specific content
#with open('/home/marco/fos/dest/' + inst_info_remote.get_uuid(), 'w') as uuid_new_dest:
#	uuid_new_dest.write("marco@192.168.31.232")

api.fdu.terminate(inst_info.get_uuid())

time.sleep(20)

api.fdu.terminate(inst_info_remote.get_uuid())

#api.fdu.migrate(inst_info.get_uuid(),'01369aac-9965-4277-96c0-280cf007e953')
#api.fdu.migrate(inst_info.get_uuid(),'9806ff42-cecc-48c1-9f44-da51955d4732')

api.close()
exit(0)