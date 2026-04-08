# Module 06 — LXMF Messaging

## Goal

Send and receive LXMF messages. Run a propagation node. Test offline delivery.

## What to Build

- `send_message.py` — create an LXMRouter, send an LXMF message to a known address
- `receive_messages.py` — register as an LXMF delivery target, print incoming messages

## Run It

**Terminal 1 — receiver:**
```bash
pixi run python experiments/06_lxmf/receive_messages.py
# Note the LXMF address printed
```

**Terminal 2 — sender:**
```bash
pixi run python experiments/06_lxmf/send_message.py <lxmf_address>
```

## Propagation Node Test

```bash
# Terminal 1 — run a propagation node
pixi run lxmd --propagation-node -v

# Terminal 2 — receiver (start, note address, then STOP it)
pixi run python experiments/06_lxmf/receive_messages.py

# Terminal 3 — send a message while receiver is offline
pixi run python experiments/06_lxmf/send_message.py <address>

# Now restart Terminal 2 — the message should be delivered from the propagation node
```

## Reference

```
../reticulum_sources/LXMF/docs/example_sender.py
../reticulum_sources/LXMF/docs/example_receiver.py
../reticulum_sources/LXMF/LXMF/LXMRouter.py   # full router API
../reticulum_sources/LXMF/LXMF/LXMessage.py    # message structure
```

## LXMF Message Structure

```python
msg = LXMF.LXMessage(
    destination,          # destination Destination object
    source,               # source LXMRouter local delivery identity
    "Message content",    # content (str)
    title="Optional title",
    fields={              # arbitrary dict — machine data, attachments, etc.
        "type": "sensor_reading",
        "value": 23.5
    }
)
```

## Delivery Methods

| Method | When used | Encryption |
|---|---|---|
| `DIRECT` | Path known, link can be established | Ephemeral ECDH (forward secrecy) |
| `OPPORTUNISTIC` | Direct not possible | Per-packet ECDH |
| Propagation node | Recipient offline | Stored encrypted at node |
