import json


def read_file(filepath):
    with open(filepath, 'r') as f:
        data = f.read()
    return data


def decode_state(payload):
    return json.loads(payload.decode('utf-8'))


def encode_state(json_state):
    return json.dumps(json_state).encode('utf-8')

