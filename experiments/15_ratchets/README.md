# Module 15 — Ratchet Forward Secrecy

## Goal

Enable ratchets on a destination so that each incoming packet uses a derived key that
advances forward — compromising one key doesn't expose past or future messages.

## Key concepts

- **Link-level forward secrecy** (Module 04): ephemeral keys per link session
- **Ratchet forward secrecy** (this module): per-packet key rotation, persisted to disk
- Ratchet state is stored in a file alongside the identity — losing it doesn't lose the identity
- A sender must have received the current ratchet key (via the destination's announce) before encrypting

## How it works

```
Destination enables ratchets → stores ratchet state in ratchet_path/
Each packet encrypted with a new derived key
Old keys are discarded → past ciphertext stays safe even if current key leaks
Ratchet key is included in the destination's announce → senders pick it up
```

## Source to study

`sources/Reticulum/Examples/Ratchets.py`

## Exercises

1. Run the example, observe the ratchet file being created
2. Send multiple packets — inspect that the ratchet state file changes each time
3. Delete the ratchet file mid-session — what happens?
4. Threat model exercise: if an attacker records encrypted traffic for a week then seizes the machine, what do they get without ratchets vs with ratchets?
