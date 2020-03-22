import datetime
import hashlib
import json


def current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def hashfile(filepath, blocksize = 65536):
    hash_obj = hashlib.sha256()
    with open(filepath, 'rb') as f:
        chunk = f.read(blocksize)
        while len(chunk):
            hash_obj.update(chunk)
            chunk = f.read(blocksize)
    return(hash_obj.hexdigest())


def load_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


def write_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f)
