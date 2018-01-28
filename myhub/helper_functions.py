import time
import json


def get_timestamp():
    return round(time.time())


def encode_json(item):
    return json.dumps(item)


def decode_json(item):
    return json.loads(item)
