# Module 13 — Broadcast & GROUP Destinations

## Goal

Understand GROUP destinations — a shared symmetric key that any participating node can use to
decrypt incoming packets. Build a simple group broadcast channel.

## Key concepts

- `RNS.Destination.GROUP` — shared symmetric key, no identity attached
- `RNS.Destination.SINGLE` — individual (asymmetric, per-identity)
- `RNS.Destination.PLAIN` — unencrypted, no key
- Broadcast packets carry no source address — sender anonymity within the group

## The pattern

```
Sender                          Receivers
  │                               │
  │  GROUP destination (shared key)
  │──────────── packet ───────────▶│  (all nodes with the key can decrypt)
  │                               │
```

## Source to study

`sources/Reticulum/Examples/Broadcast.py`

## Exercises

1. Run the example in two terminals — one sends, multiple receive
2. Modify it to send structured app_data (msgpack dict)
3. Add a sequence number to detect dropped packets
4. Compare: what happens if you send to a SINGLE destination vs a GROUP destination? (Size, encryption, anonymity)
