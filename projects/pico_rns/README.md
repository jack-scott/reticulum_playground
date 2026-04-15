# pico_rns

A minimal Reticulum thin-client for the Raspberry Pi Pico 2W, written in MicroPython.

## What it does

Connects a Pico 2W to a Reticulum mesh network over WiFi UDP, using a nearby
RNode router (e.g. a T-Beam running `microReticulum_Firmware`) as the single
network hop.

```
[Pico 2W]
  MicroPython
  pico_rns lib
     │
     │  UDP :4242 broadcast
     │  (same WiFi LAN)
     ▼
[T-Beam / RNode]
  microReticulum_Firmware
  transport_enabled = true
     │
     │  LoRa
     ▼
[rest of Reticulum mesh]
```

The Pico is a **thin client** — it participates fully (has its own cryptographic
identity and destination address) but does not route for others. All path
discovery and LoRa forwarding is handled by the router.

## How it works

Every Reticulum node is identified by a keypair:

- **X25519** (32 bytes) — used for ECDH encryption of data packets
- **Ed25519** (32 bytes seed) — used to sign announces

The destination address is a 16-byte truncated SHA-256 hash derived from the
public key and an app name. No registration is needed — the address is
deterministic from the keypair.

To be reachable, the Pico broadcasts a signed **announce** packet over UDP.
The router picks this up and propagates it over LoRa. Any node that wants to
send to the Pico encrypts a packet with the Pico's X25519 public key (learned
from the announce) and sends it toward the router, which forwards it over UDP.

Encryption uses Reticulum's Token scheme:
```
shared  = X25519-ECDH(ephemeral_prv, recipient_pub)
derived = HKDF-SHA256(shared, salt=recipient_hash, length=64)
token   = AES-256-CBC(PKCS7(plaintext), key=derived[32:], iv) + HMAC-SHA256(derived[:32], iv+ct)
wire    = ephemeral_pub(32) + token
```

## Project layout

```
pico_rns/
├── main.py               # Entry point — runs on Pico 2W
├── test_local.py         # Crypto/packet tests — runs on desktop MicroPython
├── pixi.toml             # Desktop dev environment (micropython + mpremote)
└── lib/
    └── rns/
        ├── crypto/
        │   ├── hmac.py   # HMAC-SHA256 (pure Python, no bytes.translate)
        │   ├── hkdf.py   # HKDF-SHA256
        │   ├── pkcs7.py  # PKCS7 pad/unpad
        │   ├── aes_cbc.py# AES-256-CBC wrapper for ucryptolib
        │   ├── x25519.py # Curve25519 DH (RFC 7748 Montgomery ladder)
        │   └── ed25519.py# Ed25519 sign/verify (RFC 8032, iterative)
        ├── identity.py   # Keypair, encrypt_for(), decrypt(), dest_hash()
        ├── packet.py     # Wire format construction and parsing
        └── node.py       # UDP socket, announce loop, send/receive
```

## Local testing

Tests the crypto and packet layers under the MicroPython Unix port — no Pico
or WiFi needed.

```bash
pixi run test
```

## Deploying to Pico 2W

Edit `main.py` and set `WIFI_SSID` / `WIFI_PASSWORD`, then:

```bash
pixi run deploy
```

This copies `lib/` and `main.py` to the Pico over USB. The identity keypair is
generated on first boot and saved to `/rns_identity.key` on the Pico's flash.

## Performance notes

All crypto runs in pure MicroPython except AES (hardware-accelerated via
`ucryptolib`). Expected times on Pico 2W at 133 MHz:

| Operation           | Approx. time | Frequency          |
|---------------------|--------------|--------------------|
| Ed25519 key gen     | 30–120 s     | Once, on first boot|
| Ed25519 sign        | 30–120 s     | Every 5 min (announce) |
| X25519 key gen      | 5–15 s       | Once               |
| X25519 exchange     | 5–15 s       | Per incoming message |
| AES-256-CBC decrypt | < 1 s        | Per message        |

The announce signing delay is acceptable since it only happens at startup and
every 5 minutes. Key generation is a one-time cost saved to flash.

## Dependencies

MicroPython built-ins used (all present in standard Pico W firmware):

- `uhashlib` — sha256, sha512
- `ucryptolib` — AES (CBC mode)
- `usocket` / `socket`
- `network`
- `os.urandom`
