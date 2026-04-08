# Module 04 — Encrypted Links

## Goal

Establish an encrypted link between two endpoints. Send data back and forth. Understand the link lifecycle.

## Key Concepts

- A Link is 3 packets, 297 bytes to establish
- Each link has ephemeral ECDH keys — forward secrecy per link
- Links have callbacks: established, closed, packet received, remote identified
- Links can be kept alive (maintained at 0.44 bits/second)

## Experiments to Build

- `server.py` — listens for incoming links, prints data received, sends a response
- `client.py` — establishes a link to server, sends messages, reads responses

## Reference

`../reticulum_sources/Reticulum/Examples/Link.py` — complete working example to adapt.

## Link Lifecycle

```
Client                          Server
  |                               |
  |--- PathRequest (if needed) -->|
  |<-- Announce ------------------|
  |                               |
  |--- LinkRequest -------------->|
  |<-- LinkProof -----------------|
  |--- LinkProof ACK ------------>|
  |                               |
  |    (link established)         |
  |<---------------------------- data
  |--- data ---------------------->
  |                               |
  |--- close -------------------->|
```

## What to Try

1. Build server + client. Exchange a few messages.
2. Stop the server mid-conversation — what callback fires on the client?
3. Measure how long link establishment takes (time from `RNS.Link()` to established callback).
4. What happens if you try to use a link after it's been closed?
