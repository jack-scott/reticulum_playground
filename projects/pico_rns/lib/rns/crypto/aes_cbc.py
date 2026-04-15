# AES-CBC wrapper for ucryptolib (MicroPython).
# Key length determines AES variant: 16=AES-128, 32=AES-256.
# Reticulum derives a 64-byte key via HKDF and uses [32:64] as the
# encryption key (AES-256) and [:32] as the HMAC signing key.

import ucryptolib

_MODE_CBC = 2

def encrypt(key, iv, plaintext):
    return ucryptolib.aes(key, _MODE_CBC, iv).encrypt(plaintext)

def decrypt(key, iv, ciphertext):
    return ucryptolib.aes(key, _MODE_CBC, iv).decrypt(ciphertext)
