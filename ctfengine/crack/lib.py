import crypt
import hashlib


def __hashlib_hash(algo, password):
    h = hashlib.new(algo)
    h.update(password.encode('utf-8'))
    return h.hexdigest()


def hashpw(algo, password):
    if algo == 'raw-md5':
        return __hashlib_hash('md5', password)
    elif algo == 'raw-sha1':
        return __hashlib_hash('sha1', password)
    elif algo == 'raw-sha256':
        return __hashlib_hash('sha256', password)
    elif algo == 'raw-sha512':
        return __hashlib_hash('sha512', password)
