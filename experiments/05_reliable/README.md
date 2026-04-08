# Module 05 — Reliable Delivery: Channel, Buffer, Requests

## Goal

Use Channel for ordered reliable delivery, Buffer for streams, and Request/Response for RPC.

## What to Build

### Channel
- `channel_server.py` — register a message type, receive Channel messages over a link
- `channel_client.py` — establish link, get channel, send structured messages

Channel messages must implement `RNS.MessageBase`. Messages are guaranteed to arrive in order.

### Buffer
- `buffer_demo.py` — create bidirectional Buffer over a link, pipe stdin through it

### Request/Response
- `rpc_server.py` — register request handlers at named paths, return computed responses
- `rpc_client.py` — call remote handlers, handle async responses via callback

## Reference

```
../reticulum_sources/Reticulum/Examples/Channel.py
../reticulum_sources/Reticulum/Examples/Buffer.py
../reticulum_sources/Reticulum/Examples/Request.py
```

## Channel vs Packet vs Buffer

| Mechanism | Ordering | Reliability | Overhead | Good for |
|---|---|---|---|---|
| Packet | None | Best effort | Low | Fire-and-forget, small data |
| Channel | Ordered | Reliable (ACKs) | Medium | Structured messages |
| Buffer | Ordered | Reliable | Medium | Streams, large text |
| Resource | N/A | Reliable + checksum | High | Files, large data |
