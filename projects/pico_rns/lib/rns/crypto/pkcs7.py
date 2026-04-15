# PKCS7 padding for AES block size (16 bytes)

_BLOCK = 16

def pad(data):
    n = _BLOCK - (len(data) % _BLOCK)
    return data + bytes([n] * n)

def unpad(data):
    n = data[-1]
    if n == 0 or n > _BLOCK:
        raise ValueError("Invalid PKCS7 padding byte: " + str(n))
    return data[:-n]
