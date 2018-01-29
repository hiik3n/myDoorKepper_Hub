import time
import json


def get_timestamp():
    return time.time()*1000


def encode_json(item):
    return json.dumps(item)


def decode_json(item):
    return json.loads(item)
