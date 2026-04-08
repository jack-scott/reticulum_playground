# Reticulum Core Concepts

A reference glossary for the fundamental building blocks. Read this before touching code.

---

## Identity

An **Identity** is a cryptographic keypair:
- Ed25519 key (256-bit) — for signatures
- X25519 key (256-bit) — for ECDH key exchange

Together these are a 512-bit Elliptic Curve keyset. An Identity is the root of everything in Reticulum — addresses, encryption, and authentication all derive from it.

```python
identity = RNS.Identity()           # generate new random identity
identity.save("./my_identity")      # persist to file
identity = RNS.Identity.from_file("./my_identity")  # reload
```

Identities are also recallable by destination hash (if previously seen on network):
```python
identity = RNS.Identity.recall(destination_hash_bytes)
```

---

## Destination

A **Destination** is an addressable endpoint. Its address is a 16-byte (128-bit) truncated hash of:

```
truncated_SHA256(identity.public_key + app_name + aspects...)
```

This means the address is **derived from the identity**, not assigned by a registrar. It never changes when you move between networks.

```python
destination = RNS.Destination(
    identity,
    RNS.Destination.IN,      # direction: IN (receive) or OUT (send)
    RNS.Destination.SINGLE,  # type: SINGLE, GROUP, or PLAIN
    "myapp",                 # app name
    "service",               # aspect 1 (can add more)
)
print(RNS.prettyhexrep(destination.hash))  # e.g. <83b7328926fed0d2e6a10a7671f9e237>
```

**Destination types:**
- `SINGLE` — encrypted to one identity (most common)
- `GROUP` — shared symmetric key, broadcast to group
- `PLAIN` — unencrypted (for announce-like discovery)

---

## Announce

An **Announce** is a signed broadcast that says "I exist at this destination hash, here's my public key". It propagates through the network hop by hop, building routing tables as it goes.

```python
destination.announce()                          # bare announce
destination.announce(app_data=b"some data")    # with app_data payload
```

**Receiving announces:**
```python
class MyHandler:
    aspect_filter = "myapp.service"             # None = receive all
    def received_announce(self, dest_hash, identity, app_data):
        print(RNS.prettyhexrep(dest_hash))

RNS.Transport.register_announce_handler(MyHandler())
```

Announces are the mechanism for path discovery. Without an announce, no path exists and you can't send to a destination.

---

## Transport (Routing)

**Transport nodes** forward packets for others. A node becomes a transport node with `enable_transport = yes` in its config. Transport nodes:
- Build and maintain path tables from announces
- Forward packets toward their destination
- Do this **blindly** — they see only encrypted data, not who is talking to whom
- Route based on cryptographic proofs, not IP addresses

**Client nodes** (default) don't forward for others — they only send and receive for themselves.

Key API:
```python
RNS.Transport.has_path(destination_hash)         # do we know a route?
RNS.Transport.request_path(destination_hash)     # ask network for a route
```

CLI: `rnpath -t` shows the current routing table.

---

## Packet

A **Packet** is a single, fire-and-forget transmission. Up to ~500 bytes payload. Can be encrypted or plain.

```python
packet = RNS.Packet(destination, data)
receipt = packet.send()

# Delivery confirmation (requires SINGLE destination with PROVE_ALL)
receipt.set_delivery_callback(lambda r: print("delivered"))
receipt.set_timeout_callback(lambda r: print("timed out"))
receipt.set_timeout(5.0)
```

Packets to `SINGLE` destinations are automatically encrypted with the destination's public key.

---

## Link

A **Link** is a lightweight encrypted session between two endpoints. Once established it provides:
- Forward secrecy (ephemeral keys per link)
- Bidirectional data exchange
- Reliable delivery via Channel/Buffer

**Cost:** 3 packets, 297 bytes to establish. Maintained at only 0.44 bits/second.

```python
# Server side
destination.set_link_established_callback(on_link)

def on_link(link):
    link.set_packet_callback(on_data)
    link.set_remote_identified_callback(on_identified)

# Client side
link = RNS.Link(destination)
link.set_link_established_callback(on_established)
```

---

## Channel

A **Channel** provides reliable, ordered delivery over a Link. Like TCP but over RNS.

```python
channel = link.get_channel()

# Send
channel.send(my_message_object)   # must implement MessageBase

# Receive
channel.register_message_type(MyMessage)
channel.add_message_handler(handler_func)
```

---

## Buffer

A **Buffer** provides stream-like I/O over a Link. Works like a socket buffer.

```python
# Write side
buf = RNS.Buffer.create_bidirectional_buffer(0, 0, link, recv_callback)
buf.write(b"hello")
buf.flush()
```

---

## Resource

A **Resource** transfers arbitrary amounts of data over a Link — files, large messages, anything. Handles chunking, compression, checksumming, and progress reporting automatically.

```python
# Send
resource = RNS.Resource(data, link, callback=on_done)

# Receive (on server side, in link callback)
link.set_resource_callback(on_resource)
link.set_resource_strategy(RNS.Link.ACCEPT_ALL)
```

---

## Request / Response

A lightweight RPC mechanism over a Link.

```python
# Register on server
destination.register_request_handler("mypath", response_generator, allow=RNS.RequestReceipt.ALLOW_ALL)

# Call from client
receipt = RNS.RequestReceipt(link, data=request_data, path="mypath", response_callback=on_response)
```

---

## Interface

An **Interface** is how Reticulum connects to a physical or virtual medium. Defined in `~/.reticulum/config`. Types:

```
AutoInterface   - WiFi LAN broadcast discovery (easiest start)
TCPServerInterface / TCPClientInterface - over IP
UDPInterface    - UDP over IP
SerialInterface - raw serial port
RNodeInterface  - LoRa via RNode device
KISSInterface   - packet radio TNC
```

Key principle: **you don't code to the interface**. You send to a destination. RNS picks the best path across all available interfaces automatically.

---

## LXMF (Layer above RNS)

LXMF is NOT part of core RNS — it's a separate package (`pip install lxmf`) that builds messaging on top.

**LXMRouter** — the main object. Handles all LXMF operations.
**LXMessage** — a single message. Has: destination, source, content, title, fields (arbitrary dict), signature, timestamp.

```python
import LXMF

router = LXMF.LXMRouter(storagepath="./lxmf_storage")
my_identity = RNS.Identity()
source = router.register_delivery_identity(my_identity, display_name="Alice")

msg = LXMF.LXMessage(dest, source, "Hello world")
router.handle_outbound(msg)
```

---

## Config File Structure

Default location: `~/.reticulum/config`

```
[reticulum]
enable_transport = no    # set yes to become a router for others
share_instance = yes     # share with other local RNS processes

[interfaces]

  [[AutoInterface]]
  type = AutoInterface
  enabled = yes

  [[TCPServerInterface]]
  type = TCPServerInterface
  enabled = yes
  listen_ip = 0.0.0.0
  listen_port = 4242

  [[TCPClientInterface]]
  type = TCPClientInterface
  enabled = yes
  target_host = 192.168.1.10
  target_port = 4242

  [[RNodeInterface]]
  type = RNodeInterface
  enabled = yes
  port = /dev/ttyUSB0
  frequency = 868000000
  bandwidth = 125000
  txpower = 14
  spreadingfactor = 8
  codingrate = 5
```

In experiments, always use a local config path:
```python
rns = RNS.Reticulum("./rns_config")
```

---

## Useful CLI Quick Reference

```bash
pixi run rnsd -v                          # start daemon, verbose
pixi run rnstatus                         # interface status
pixi run python -m RNS.Tools.rnpath -t   # routing table
pixi run python -m RNS.Tools.rnprobe <hash>  # probe destination
```
