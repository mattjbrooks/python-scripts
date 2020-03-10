import hashlib

def hashfile(filepath, blocksize = 65536):
    hash_obj = hashlib.sha256()
    with open(filepath, 'rb') as f:
        chunk = f.read(blocksize)
        while len(chunk):
            hash_obj.update(chunk)
            chunk = f.read(blocksize)
    return(hash_obj.hexdigest())
