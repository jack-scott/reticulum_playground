# Reticulum identity — keypair management, encryption, decryption, addressing.
#
# A Reticulum identity holds two 32-byte keypairs:
#   x25519_prv / x25519_pub  — Curve25519 DH, used for encryption
#   ed25519_seed / ed25519_pub — Ed25519, used for signing announces
#
# The identity hash is SHA-256(x25519_pub + ed25519_pub)[:16].
# A destination hash is SHA-256(name_hash(10) + identity_hash(16))[:16].
#
# Encryption (Token scheme from Reticulum):
#   1. Ephemeral X25519 key exchange with recipient's pub key
#   2. HKDF(shared_secret, salt=recipient_hash, length=64) → derived_key
#   3. sign_key = derived[:32], enc_key = derived[32:]  (AES-256)
#   4. token = iv(16) + AES-256-CBC(PKCS7(plaintext)) + HMAC-SHA256(sign_key, iv+ct)
#   5. wire  = eph_pub(32) + token

import os
import ubinascii
import uhashlib

from .crypto import x25519, ed25519, hkdf, hmac_sha256, aes_encrypt, aes_decrypt, pad, unpad

_TRUNCATED  = 16   # destination / identity hash length in bytes
_NAME_HASH  = 10   # name hash length in bytes
_DERIVED    = 64   # HKDF output: 32 sign + 32 enc (AES-256)


def _sha256(data):
    return uhashlib.sha256(data).digest()

def truncated_hash(data):
    return _sha256(data)[:_TRUNCATED]


class Identity:
    def __init__(self, prv_bytes=None):
        if prv_bytes is not None:
            self._load(prv_bytes)
        else:
            self._generate()

    # --- key management ---

    def _generate(self):
        self.x25519_prv  = x25519.generate_private()
        self.ed25519_seed = os.urandom(32)
        self._derive_public()

    def _load(self, prv_bytes):
        if len(prv_bytes) != 64:
            raise ValueError("Private key must be 64 bytes (32 x25519 + 32 ed25519 seed)")
        self.x25519_prv   = prv_bytes[:32]
        self.ed25519_seed = prv_bytes[32:]
        self._derive_public()

    def _derive_public(self):
        self.x25519_pub  = x25519.public_key(self.x25519_prv)
        self.ed25519_pub = ed25519.public_key(self.ed25519_seed)
        self.pub_bytes   = self.x25519_pub + self.ed25519_pub
        self.hash        = truncated_hash(self.pub_bytes)

    def get_private_key(self):
        return self.x25519_prv + self.ed25519_seed

    def get_public_key(self):
        return self.pub_bytes

    # --- addressing ---

    def dest_hash(self, app_name, *aspects):
        """Compute the destination hash for app_name + aspects under this identity."""
        name = app_name
        for a in aspects:
            name += "." + a
        name_hash = _sha256(name.encode())[:_NAME_HASH]
        return truncated_hash(name_hash + self.hash)

    # --- signing ---

    def sign(self, message):
        return ed25519.sign(self.ed25519_seed, message)

    # --- encryption (send to a known recipient) ---

    def encrypt_for(self, recipient_pub_bytes, plaintext):
        """Encrypt plaintext for a recipient identified by their 64-byte public key."""
        recipient_x25519 = recipient_pub_bytes[:32]
        recipient_hash   = truncated_hash(recipient_pub_bytes)

        eph_prv = x25519.generate_private()
        eph_pub = x25519.public_key(eph_prv)
        shared  = x25519.exchange(eph_prv, recipient_x25519)

        derived   = hkdf(_DERIVED, shared, salt=recipient_hash)
        sign_key  = derived[:32]
        enc_key   = derived[32:]

        iv         = os.urandom(16)
        ciphertext = aes_encrypt(enc_key, iv, pad(plaintext))
        signed     = iv + ciphertext
        mac        = hmac_sha256(sign_key, signed)

        return eph_pub + signed + mac

    # --- decryption (receive data addressed to us) ---

    def decrypt(self, token):
        """Decrypt a Reticulum data token addressed to this identity."""
        if len(token) < 32 + 16 + 16 + 32:
            raise ValueError("Token too short: " + str(len(token)))

        eph_pub  = token[:32]
        payload  = token[32:]
        shared   = x25519.exchange(self.x25519_prv, eph_pub)

        derived   = hkdf(_DERIVED, shared, salt=self.hash)
        sign_key  = derived[:32]
        enc_key   = derived[32:]

        mac      = payload[-32:]
        expected = hmac_sha256(sign_key, payload[:-32])
        if mac != expected:
            raise ValueError("HMAC verification failed — wrong key or corrupted data")

        iv         = payload[:16]
        ciphertext = payload[16:-32]
        return unpad(aes_decrypt(enc_key, iv, ciphertext))

    # --- persistence ---

    def save(self, path):
        with open(path, 'wb') as f:
            f.write(self.get_private_key())

    @staticmethod
    def load_or_create(path):
        try:
            with open(path, 'rb') as f:
                prv = f.read()
            identity = Identity(prv)
            print("RNS: loaded identity", ubinascii.hexlify(identity.hash).decode())
        except OSError:
            identity = Identity()
            identity.save(path)
            print("RNS: created identity", ubinascii.hexlify(identity.hash).decode())
        return identity
