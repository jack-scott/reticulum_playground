# Ed25519 sign/verify — pure Python, RFC 8032.
# Adapted from the pure25519 library (MIT) included in Reticulum.
# WARNING: Signing is slow on Pico W (~30-120s). Only called at announce time.
# Verification is skipped in thin-client mode (we trust the router).

import uhashlib

_Q = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493

try:
    uhashlib.sha512  # available on Pico/ESP32 MicroPython builds
    def _sha512(data):
        return uhashlib.sha512(data).digest()
except AttributeError:
    # unix MicroPython port omits sha512 — use pure Python fallback
    from .sha512 import sha512 as _sha512

def _inv(x):
    return pow(x, _Q - 2, _Q)

_d  = -121665 * _inv(121666) % _Q
_I  = pow(2, (_Q - 1) // 4, _Q)
_By = 4 * _inv(5) % _Q

def _xrecover(y):
    xx = (y * y - 1) * _inv(_d * y * y + 1) % _Q
    x  = pow(xx, (_Q + 3) // 8, _Q)
    if (x * x - xx) % _Q != 0:
        x = x * _I % _Q
    if x % 2 != 0:
        x = _Q - x
    return x

_Bx = _xrecover(_By)
_B  = (_Bx % _Q, _By % _Q, 1, _Bx * _By % _Q)
_ID = (0, 1, 1, 0)  # neutral element in extended coordinates

def _pt_add(P, R):
    x1, y1, z1, t1 = P
    x2, y2, z2, t2 = R
    A = (y1 - x1) * (y2 - x2) % _Q
    B = (y1 + x1) * (y2 + x2) % _Q
    C = 2 * t1 * t2 * _d % _Q
    D = 2 * z1 * z2 % _Q
    E = B - A; F = D - C; G = D + C; H = B + A
    return (E*F % _Q, G*H % _Q, F*G % _Q, E*H % _Q)

def _scalarmult(P, e):
    # Iterative double-and-add (LSB first) — avoids recursion depth issues.
    Q = _ID
    while e > 0:
        if e & 1:
            Q = _pt_add(Q, P)
        P = _pt_add(P, P)
        e >>= 1
    return Q

def _encode_pt(P):
    x, y, z, _ = P
    zi = _inv(z)
    x = x * zi % _Q
    y = y * zi % _Q
    b = bytearray(y.to_bytes(32, 'little'))
    b[31] ^= (x & 1) << 7
    return bytes(b)

def _decode_pt(s):
    y    = int.from_bytes(s, 'little') & ((1 << 255) - 1)
    sign = s[31] >> 7
    x    = _xrecover(y)
    if x % 2 != sign:
        x = _Q - x
    return (x % _Q, y % _Q, 1, x * y % _Q)

def _clamp_scalar(b):
    h = bytearray(b[:32])
    h[0]  &= 248
    h[31] &= 63
    h[31] |= 64
    return int.from_bytes(h, 'little')

def _hint(m):
    return int.from_bytes(_sha512(m), 'little')

def public_key(seed):
    """Derive Ed25519 public key from 32-byte seed."""
    assert len(seed) == 32
    h = _sha512(seed)
    a = _clamp_scalar(h[:32])
    return _encode_pt(_scalarmult(_B, a))

def sign(seed, msg):
    """Sign msg with seed. Returns 64-byte signature."""
    assert len(seed) == 32
    h      = _sha512(seed)
    a      = _clamp_scalar(h[:32])
    prefix = bytes(h[32:])
    pk     = public_key(seed)
    r      = _hint(prefix + msg) % _L
    R      = _encode_pt(_scalarmult(_B, r))
    S      = (r + _hint(R + pk + msg) * a) % _L
    return R + S.to_bytes(32, 'little')

def verify(pk, sig, msg):
    """Verify sig over msg with public key pk. Returns True/False."""
    if len(sig) != 64 or len(pk) != 32:
        return False
    try:
        R  = _decode_pt(sig[:32])
        A  = _decode_pt(pk)
        S  = int.from_bytes(sig[32:], 'little')
        h  = _hint(sig[:32] + pk + msg)
        v1 = _scalarmult(_B, S)
        v2 = _pt_add(R, _scalarmult(A, h))
        return _encode_pt(v1) == _encode_pt(v2)
    except Exception:
        return False
