# HMAC-SHA256 for MicroPython
# Uses uhashlib (MicroPython's hashlib). No bytes.translate — uses XOR directly.

import uhashlib

_BLOCK = 64

def hmac_sha256(key, data):
    if len(key) > _BLOCK:
        key = uhashlib.sha256(key).digest()
    if len(key) < _BLOCK:
        key = key + b'\x00' * (_BLOCK - len(key))
    ipad = bytes(k ^ 0x36 for k in key)
    opad = bytes(k ^ 0x5c for k in key)
    inner = uhashlib.sha256(ipad)
    inner.update(data)
    inner_digest = inner.digest()
    outer = uhashlib.sha256(opad)
    outer.update(inner_digest)
    return outer.digest()
