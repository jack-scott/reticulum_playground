# Curve25519 Diffie-Hellman (X25519) — pure Python, RFC 7748.
# Key generation only happens once at startup; exchange on every decrypt.
# On Pico W (~133 MHz MicroPython) expect ~2-5s per operation.

import os

_P  = 2**255 - 19
_A24 = 121665
_BASE = bytes([9] + [0] * 31)

def _clamp(k):
    b = bytearray(k)
    b[0]  &= 248
    b[31] &= 127
    b[31] |= 64
    return bytes(b)

def _decode_u(u):
    b = bytearray(u)
    b[31] &= 127
    return int.from_bytes(bytes(b), 'little')

def _encode_u(u):
    return (u % _P).to_bytes(32, 'little')

def _ladder(k_bytes, u_bytes):
    k  = int.from_bytes(_clamp(k_bytes), 'little')
    u  = _decode_u(u_bytes)
    x1 = u
    x2, z2 = 1, 0
    x3, z3 = u, 1
    swap = 0
    for t in range(254, -1, -1):
        k_t  = (k >> t) & 1
        swap ^= k_t
        if swap:
            x2, x3 = x3, x2
            z2, z3 = z3, z2
        swap = k_t
        A  = (x2 + z2) % _P
        AA = A * A % _P
        B  = (x2 - z2) % _P
        BB = B * B % _P
        E  = (AA - BB) % _P
        C  = (x3 + z3) % _P
        D  = (x3 - z3) % _P
        DA = D * A % _P
        CB = C * B % _P
        x3 = pow(DA + CB, 2, _P)
        z3 = x1 * pow(DA - CB, 2, _P) % _P
        x2 = AA * BB % _P
        z2 = E * (AA + _A24 * E) % _P
    if swap:
        x2, x3 = x3, x2
        z2, z3 = z3, z2
    return _encode_u(x2 * pow(z2, _P - 2, _P))

def generate_private():
    return os.urandom(32)

def public_key(prv):
    return _ladder(prv, _BASE)

def exchange(prv, peer_pub):
    return _ladder(prv, peer_pub)
