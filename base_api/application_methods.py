import hashlib


def encryptSHA512(str):
    return hashlib.sha512(str).hexdigest()


def encryptSHA256(str):
    return hashlib.md5(str).hexdigest()
