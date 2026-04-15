# HKDF-SHA256 for MicroPython

from .hmac import hmac_sha256
from math import ceil

def hkdf(length, derive_from, salt=None, context=None):
    hash_len = 32
    if salt is None or len(salt) == 0:
        salt = bytes(hash_len)
    if context is None:
        context = b""
    prk = hmac_sha256(salt, derive_from)
    block = b""
    derived = b""
    for i in range(ceil(length / hash_len)):
        block = hmac_sha256(prk, block + context + bytes([(i + 1) & 0xFF]))
        derived += block
    return derived[:length]
