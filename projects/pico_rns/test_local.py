# Local test suite for pico_rns crypto and packet layers.
# Runs under the MicroPython Unix port — no Pico, no WiFi needed.
#
#   pixi run test
#
# Tests: identity generation, encrypt/decrypt round-trip, announce/data
# packet build and parse. Ed25519 operations are skipped by default because
# they take 30-120s on a real Pico (and are slow even on desktop MicroPython).
# Set SKIP_SLOW = False to include them.

import sys
import ubinascii
sys.path.insert(0, 'lib')

def to_hex(b):
    return ubinascii.hexlify(b).decode()

def from_hex(s):
    return ubinascii.unhexlify(s)

SKIP_SLOW = False   # Set False to test Ed25519 sign/verify

_passed = 0
_failed = 0

def ok(name):
    global _passed
    _passed += 1
    print("PASS", name)

def fail(name, reason):
    global _failed
    _failed += 1
    print("FAIL", name, "—", reason)

def expect_eq(name, got, want):
    if got == want:
        ok(name)
    else:
        fail(name, "got " + repr(got) + " want " + repr(want))

def expect_true(name, val):
    if val:
        ok(name)
    else:
        fail(name, "expected True, got " + repr(val))

def expect_raises(name, fn, exc_type):
    try:
        fn()
        fail(name, "expected " + str(exc_type) + " but no exception raised")
    except exc_type:
        ok(name)
    except Exception as e:
        fail(name, "expected " + str(exc_type) + " got " + str(type(e)) + ": " + str(e))


# ── HMAC ──────────────────────────────────────────────────────────────────────

print("\n--- HMAC ---")
from rns.crypto.hmac import hmac_sha256

# RFC 4231 test vector 1
key = bytes([0x0b] * 20)
msg = b"Hi There"
got = hmac_sha256(key, msg)
expect_eq("hmac_sha256 rfc4231_tv1",
    to_hex(got),
    "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7")

# Key longer than block size gets hashed first
long_key = bytes(range(100))
result = hmac_sha256(long_key, b"test")
expect_true("hmac_sha256 long_key returns 32 bytes", len(result) == 32)


# ── HKDF ──────────────────────────────────────────────────────────────────────

print("\n--- HKDF ---")
from rns.crypto.hkdf import hkdf

# Basic: output length respected
out = hkdf(64, b"input key material", salt=b"salt", context=b"context")
expect_true("hkdf 64 bytes output", len(out) == 64)

out16 = hkdf(16, b"ikm", salt=b"s")
expect_true("hkdf 16 bytes output", len(out16) == 16)

# Deterministic
out_a = hkdf(32, b"ikm", salt=b"salt")
out_b = hkdf(32, b"ikm", salt=b"salt")
expect_eq("hkdf deterministic", out_a, out_b)

# Different salt → different output
out_c = hkdf(32, b"ikm", salt=b"other")
expect_true("hkdf different salt", out_a != out_c)


# ── PKCS7 ─────────────────────────────────────────────────────────────────────

print("\n--- PKCS7 ---")
from rns.crypto.pkcs7 import pad, unpad

for n in (1, 15, 16, 17, 31, 32):
    data = bytes(n)
    padded = pad(data)
    expect_true("pkcs7 pad len multiple of 16 (n=" + str(n) + ")", len(padded) % 16 == 0)
    expect_eq("pkcs7 round-trip (n=" + str(n) + ")", unpad(padded), data)

expect_raises("pkcs7 unpad bad byte", lambda: unpad(b'\x00' * 15 + b'\x11'), ValueError)


# ── X25519 ────────────────────────────────────────────────────────────────────

print("\n--- X25519 ---")
from rns.crypto import x25519

prv_a = x25519.generate_private()
prv_b = x25519.generate_private()
pub_a = x25519.public_key(prv_a)
pub_b = x25519.public_key(prv_b)

expect_true("x25519 pub_a is 32 bytes", len(pub_a) == 32)
expect_true("x25519 pub_b is 32 bytes", len(pub_b) == 32)
expect_true("x25519 keys differ",       pub_a != pub_b)

shared_ab = x25519.exchange(prv_a, pub_b)
shared_ba = x25519.exchange(prv_b, pub_a)
expect_eq("x25519 ECDH symmetry", shared_ab, shared_ba)
expect_true("x25519 shared is 32 bytes", len(shared_ab) == 32)

# RFC 7748 test vector
tv_prv = from_hex("a546e36bf0527c9d3b16154b82465edd62144c0ac1fc5a18506a2244ba449ac4")
tv_pub = from_hex("e6db6867583030db3594c1a424b15f7c726624ec26b3353b10a903a6d0ab1c4c")
tv_out = from_hex("c3da55379de9c6908e94ea4df28d084f32eccf03491c71f754b4075577a28552")
expect_eq("x25519 rfc7748 test vector", x25519.exchange(tv_prv, tv_pub), tv_out)


# ── AES-CBC ───────────────────────────────────────────────────────────────────

print("\n--- AES-CBC ---")
from rns.crypto.aes_cbc import encrypt, decrypt
import os

key32 = os.urandom(32)
iv    = os.urandom(16)
pt    = b"hello reticulum!"  # exactly 16 bytes

ct = encrypt(key32, iv, pt)
expect_true("aes256 ciphertext != plaintext", ct != pt)
expect_true("aes256 ciphertext is 16 bytes",  len(ct) == 16)

rt = decrypt(key32, iv, ct)
expect_eq("aes256 round-trip", rt, pt)

# Different key → different ciphertext
key2 = os.urandom(32)
ct2  = encrypt(key2, iv, pt)
expect_true("aes256 different key", ct != ct2)


# ── Identity ──────────────────────────────────────────────────────────────────

print("\n--- Identity ---")
from rns.identity import Identity

id_a = Identity()
expect_true("identity pub 64 bytes",  len(id_a.get_public_key()) == 64)
expect_true("identity hash 16 bytes", len(id_a.hash) == 16)
expect_true("identity prv 64 bytes",  len(id_a.get_private_key()) == 64)

# Round-trip through private key bytes
id_b = Identity(id_a.get_private_key())
expect_eq("identity reload hash",      id_b.hash,           id_a.hash)
expect_eq("identity reload pub",       id_b.get_public_key(), id_a.get_public_key())

# Different identities have different hashes
id_c = Identity()
expect_true("identity unique hashes", id_a.hash != id_c.hash)

# Destination hash is deterministic
dh1 = id_a.dest_hash("pico", "hello")
dh2 = id_a.dest_hash("pico", "hello")
expect_eq("dest_hash deterministic",  dh1, dh2)

dh3 = id_a.dest_hash("pico", "other")
expect_true("dest_hash aspect differs", dh1 != dh3)

dh4 = id_c.dest_hash("pico", "hello")
expect_true("dest_hash identity differs", dh1 != dh4)


# ── Encrypt / Decrypt ─────────────────────────────────────────────────────────

print("\n--- Encrypt / Decrypt ---")

sender   = Identity()
receiver = Identity()

plaintext = b"Hello from Pico!"
token = sender.encrypt_for(receiver.get_public_key(), plaintext)

expect_true("token min length", len(token) >= 32 + 16 + 16 + 32)  # eph + iv + 1 block + hmac

recovered = receiver.decrypt(token)
expect_eq("encrypt/decrypt round-trip", recovered, plaintext)

# Wrong key → HMAC failure
wrong = Identity()
expect_raises("decrypt wrong key", lambda: wrong.decrypt(token), ValueError)

# Tampered token → HMAC failure
bad = bytearray(token)
bad[40] ^= 0xFF
expect_raises("decrypt tampered", lambda: receiver.decrypt(bytes(bad)), ValueError)

# Various payload sizes
for size in (1, 15, 16, 17, 100, 400):
    msg = bytes(size)
    t   = sender.encrypt_for(receiver.get_public_key(), msg)
    expect_eq("encrypt/decrypt size=" + str(size), receiver.decrypt(t), msg)


# ── Packet build/parse ────────────────────────────────────────────────────────

print("\n--- Packets ---")
from rns.packet import (
    build_announce, build_data, parse,
    PKT_ANNOUNCE, PKT_DATA,
)

identity  = Identity()
dest_hash = identity.dest_hash("test", "app")

if not SKIP_SLOW:
    ann = build_announce(dest_hash, identity, "test", "app", app_data=b"hello")
    p   = parse(ann)
    expect_true("announce parse not None",         p is not None)
    expect_eq(  "announce pkt_type",               p['pkt_type'], PKT_ANNOUNCE)
    expect_eq(  "announce dest_hash",              p['dest_hash'], dest_hash)
    expect_true("announce data has pub_key+more",  len(p['data']) >= 64 + 10 + 10 + 64)
else:
    print("SKIP announce build (Ed25519 signing — set SKIP_SLOW=False to enable)")

# Data packet round-trip (no signing needed)
token  = identity.encrypt_for(identity.get_public_key(), b"test payload")
pkt    = build_data(dest_hash, token)
parsed = parse(pkt)
expect_true("data parse not None",    parsed is not None)
expect_eq(  "data pkt_type",          parsed['pkt_type'], PKT_DATA)
expect_eq(  "data dest_hash",         parsed['dest_hash'], dest_hash)
expect_eq(  "data round-trip",        parsed['data'], token)

# Short packet returns None
expect_eq("parse too short", parse(b'\x00' * 5), None)


# ── Ed25519 (slow — skipped by default) ───────────────────────────────────────

if not SKIP_SLOW:
    print("\n--- Ed25519 (slow) ---")
    from rns.crypto import ed25519
    import os

    seed = os.urandom(32)
    pub  = ed25519.public_key(seed)
    expect_true("ed25519 pub 32 bytes", len(pub) == 32)

    msg = b"test message for signing"
    sig = ed25519.sign(seed, msg)
    expect_true("ed25519 sig 64 bytes",  len(sig) == 64)
    expect_true("ed25519 verify valid",  ed25519.verify(pub, sig, msg))
    expect_true("ed25519 reject tamper", not ed25519.verify(pub, sig, msg + b"x"))

    wrong_seed = os.urandom(32)
    wrong_pub  = ed25519.public_key(wrong_seed)
    expect_true("ed25519 reject wrong key", not ed25519.verify(wrong_pub, sig, msg))
else:
    print("\nSKIP ed25519 tests (set SKIP_SLOW=False to enable)")


# ── Summary ───────────────────────────────────────────────────────────────────

print("\n" + "="*40)
print("Results: {} passed, {} failed".format(_passed, _failed))
if _failed:
    sys.exit(1)
