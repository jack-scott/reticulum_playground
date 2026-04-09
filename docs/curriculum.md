# Reticulum Learning Curriculum

A course-style learning path. Each module builds on the previous one. Work through the experiments in order — each one has runnable code in its folder.

---

## Fundamentals Track

### Module 00 — Setup & First Identity
**Folder:** `experiments/00_setup/`

Goals:
- Confirm pixi environment works
- Start RNS, generate an identity, print its hash
- Understand where RNS stores its config and data

Key concepts: `RNS.Reticulum()`, `RNS.Identity()`, local config path

```bash
pixi run verify
```

---

### Module 01 — Hello RNS: Announces
**Folder:** `experiments/01_hello_rns/`

Goals:
- Create a destination and announce it
- Listen for announces from other nodes
- Run two terminals — one announces, one listens with a callback

Key concepts: Destination, Announce, `register_announce_handler`, app_name + aspects, destination hash

Source reference: `sources/Reticulum/Examples/Announce.py`

---

### Module 02 — Addressing Deep Dive
**Folder:** `experiments/02_addressing/`

Goals:
- Understand how destination hashes are derived (not arbitrary — deterministic from identity + naming)
- Save and reload an identity (same hash across restarts)
- Use `RNS.Identity.recall()` to look up a known identity from its hash
- Explore `rnid` utility

Key concepts: hash derivation, persistent identity, identity recall, `rnid`

---

### Module 03 — Packet Echo (Client/Server)
**Folder:** `experiments/03_echo/`

Goals:
- Build a simple echo server that receives packets and auto-proves them
- Build a client that sends and waits for delivery confirmation
- Measure round-trip time
- Read RSSI and SNR from packet receipts

Key concepts: `RNS.Packet`, `PacketReceipt`, delivery callback, timeout callback, proof strategy, RSSI/SNR

Source reference: `sources/Reticulum/Examples/Echo.py`

---

### Module 04 — Encrypted Links
**Folder:** `experiments/04_links/`

Goals:
- Establish an encrypted Link between client and server
- Send data back and forth over the link
- Handle link established/closed/data callbacks
- Understand forward secrecy (each link has ephemeral keys)

Key concepts: `RNS.Link`, `set_link_established_callback`, `set_packet_callback`, link lifecycle, 3-packet setup

Source reference: `sources/Reticulum/Examples/Link.py`

---

### Module 05 — Reliable Delivery: Channel, Buffer, Requests
**Folder:** `experiments/05_reliable/`

Goals:
- Use Channel for reliable ordered delivery over a link
- Use Buffer for stream-like I/O over a link
- Implement a simple request/response (RPC) pattern

Key concepts: `link.get_channel()`, `MessageBase`, `RNS.Buffer`, `register_request_handler`, `RNS.RequestReceipt`

Source references: `sources/Reticulum/Examples/Channel.py`, `Buffer.py`, `Request.py`

---

## Messaging Track

### Module 06 — LXMF Messaging
**Folder:** `experiments/06_lxmf/`

Goals:
- Send and receive an LXMF message between two scripts
- Understand the three delivery methods (direct, opportunistic, propagation)
- Run a local propagation node (`lxmd`)
- Test offline delivery — send to an offline recipient, it gets it when it comes back

Key concepts: `LXMRouter`, `LXMessage`, delivery methods, `lxmd`, propagation node sync

Source references: `sources/LXMF/docs/example_sender.py`, `example_receiver.py`

```bash
# In one terminal — propagation node
pixi run lxmd --propagation-node

# In another — receiver (then stop it, send a message, start it again)
pixi run python experiments/06_lxmf/receiver.py
```

---

### Module 07 — Resources & File Transfer
**Folder:** `experiments/07_resources/`

Goals:
- Transfer a file using `RNS.Resource` over a link
- Watch progress callbacks
- Measure actual throughput
- Try `rncp` for command-line file transfer

Key concepts: `RNS.Resource`, `ACCEPT_ALL`, resource progress callbacks, compression, `rncp`

Source reference: `sources/Reticulum/Examples/Resource.py`

---

## Transport Track

### Module 08 — Interface Configuration
**Folder:** `experiments/08_transports/`

Goals:
- Configure and test TCP server/client (two laptops or two terminals)
- Configure UDP AutoInterface (automatic WiFi LAN discovery)
- Understand Client mode vs Transport mode
- Multi-interface config (WiFi + TCP simultaneously)
- Inspect routing tables with `rnpath`

Key concepts: `TCPServerInterface`, `TCPClientInterface`, `AutoInterface`, `enable_transport`, interface modes (full/access-point/roaming/boundary/gateway)

Config files to build: `tcp_server.config`, `tcp_client.config`, `wifi_auto.config`, `transport_node.config`

---

### Module 09 — Debug & Analysis
**Folder:** `experiments/09_debug/`

Goals:
- Use `rnstatus` to read interface stats
- Use `rnpath` to inspect and flush routing tables
- Use `rnprobe` to test connectivity to a specific destination
- Use `rns_announce_view` to watch all announce traffic
- Run `rns_hop_simulator` to simulate 3-hop path on one machine
- Set log levels and interpret RNS debug output

Key tools: `rnstatus`, `rnpath`, `rnprobe`, `rns_announce_view.py`, `rns_hop_simulator.py`

Source reference: `sources/RNS-Tools/`

```bash
# Hop simulator (3 hops)
pixi run python ../sources/RNS-Tools/rns_hop_simulator/rns_hop_simulator.py \
    -c 3 --cfg_entry entry.cfg --cfg_exit exit.cfg
```

---

## Advanced Track

### Module 10 — LXST Voice & Audio
**Folder:** `experiments/10_lxst_audio/`

Goals:
- Understand the LXST pipeline (Source → Codec → Network → Decode → Sink)
- Make a voice call between two machines using `rnphone`
- Compare Codec2 (700 bps, LoRa-capable) vs Opus (4.5 kbps+)
- Explore pipeline examples from LXST source

System deps required: `sudo apt install python3-pyaudio codec2`

Source reference: `sources/LXST/examples/`

---

### Module 11 — Microcontrollers (ESP32)
**Folder:** `experiments/11_microcontrollers/`

Goals:
- Build microReticulum on the native (Linux) target to understand the C++ API
- Flash to an ESP32 (TTGO T-Beam or similar)
- Get the ESP32 to announce on the network and be discovered by Python RNS

**Uses Docker — no PlatformIO installed locally.**

```bash
# Build for native (Linux) to test first
docker run --rm -it -v "$(pwd)":/workspace -w /workspace \
    python:3.11 bash -c "pip install platformio && pio run -e native14"

# Build and flash to ESP32
docker run --rm -it --privileged \
    -v "$(pwd)":/workspace -w /workspace \
    -v /dev:/dev \
    python:3.11 bash -c "pip install platformio && pio run -e ttgo-t-beam -t upload"
```

Source reference: `sources/microReticulum/`

---

## Capstone Projects

### Project A — Home Assistant Integration
**Folder:** `projects/home_assistant/`

Build a sensor telemetry system:
- Sensor node (Pi Zero or ESP32) collects data (temp, humidity, etc.)
- Sends as LXMF Fields dict to a collector node
- Collector stores readings and serves them via a NomadNet page or REST API
- Optional: LXMF command messages to trigger actions

Components:
- `sensor_node.py` — reads sensor, sends LXMF
- `collector.py` — receives LXMF, stores to SQLite
- `dashboard.py` — Flask/FastAPI serving readings

Reference: Sideband telemetry plugins (`sources/Sideband/docs/example_plugins/bme280_telemetry.py`)

---

### Project B — Network Visualiser & Debug Tools
**Folder:** `projects/viz_debug/`

Build a real-time Reticulum network map:
- Listen to all announces
- Build a graph of nodes (hash, app name, hop count, RSSI if available)
- Serve as a web dashboard (Flask + D3.js or similar)
- Log to SQLite for historical analysis

Components:
- `tools/announce_monitor.py` — announce listener + database writer
- `projects/viz_debug/dashboard.py` — web dashboard
- `projects/viz_debug/static/` — frontend

Reference: `sources/RNS-Tools/rns_announce_directory/rns_announce_directory.py`

---

### Project C — Drone Sideband (MAVLink over RNS)
**Folder:** `projects/drone_sideband/`

Build a drone comms link:
- FC side: companion computer (Pi) connected to Pixhawk via serial, running `rns-mavlink-rs fc`
- GCS side: laptop running `rns-mavlink-rs gc`, forwarding to QGroundControl via UDP
- Transport: LoRa via RNode for radio range, or WiFi for bench testing
- Optional: Sideband telemetry display for position/status

**Uses Docker for Rust build.**

```bash
# Build both binaries
docker run --rm -it \
    -v "$(pwd)":/workspace \
    -w /workspace \
    rust:latest \
    cargo build --release

# Run GCS (edit Gc.toml first with FC destination hash)
sudo ./target/release/gc
```

Config files: `Gc.toml` (gc_udp_address, gc_reply_port, fc_destination), `Fc.toml` (serial_port, serial_baud, gc_destination)

Source reference: `sources/rns-mavlink-rs/`

---

---

## Advanced Messaging & Crypto Track

### Module 13 — Broadcast & GROUP Destinations
**Folder:** `experiments/13_broadcast/`

Goals:
- Understand GROUP destinations — a shared symmetric key, not an individual identity
- Send a broadcast packet that any node holding the group key can decrypt
- Compare GROUP (broadcast) vs SINGLE (unicast) vs PLAIN (unencrypted) destination types
- Build a simple group chat channel with a shared key distributed out-of-band

Key concepts: `RNS.Destination.GROUP`, group key, symmetric encryption, no source address in GROUP packets

Source reference: `sources/Reticulum/Examples/Broadcast.py`

---

### Module 14 — Remote Identity Verification
**Folder:** `experiments/14_identify/`

Goals:
- Prove your identity to a remote peer over an established link
- Understand when you know *who* you're talking to (after identify) vs just *that* there's a node (after link)
- Build a server that only responds after identity is verified
- Understand the trust model: RNS provides confidentiality and integrity by default; identity verification is opt-in

Key concepts: `link.identify()`, `set_remote_identified_callback`, `Identity.validate()`, trust establishment

Source reference: `sources/Reticulum/Examples/Identify.py`

---

### Module 15 — Ratchet Forward Secrecy
**Folder:** `experiments/15_ratchets/`

Goals:
- Understand what a ratchet is and why it matters (per-message key rotation)
- Enable ratchets on a destination and observe the key evolution
- Understand what's protected: if a session key is compromised, past messages remain safe
- Compare link-level forward secrecy (ephemeral keys per link) vs ratchet forward secrecy (per-packet)

Key concepts: `Destination.enable_ratchets()`, ratchet file paths, `ENCRYPT_FILE` vs `RATCHET_FILE`, forward secrecy threat model

Source reference: `sources/Reticulum/Examples/Ratchets.py`

---

## Applications & Plugins Track

### Module 16 — Mobile Networking with Sideband
**Folder:** `experiments/16_sideband_mobile/`

Goals:
- Install Sideband on Android (APK from GitHub releases, never app stores)
- Connect Sideband to your desktop `rnsd` over WiFi TCP
- Exchange LXMF messages between phone and laptop
- Share location from phone, receive on desktop
- Understand how Android can act as a Transport Instance (router)

Install:
```bash
# Desktop — start rnsd with a TCP server
pixi run rnsd
```

Then in Sideband → Settings → Interfaces → add TCPClientInterface pointing at your laptop IP.

Source reference: `sources/Sideband/`

---

### Module 17 — Sideband Plugin Development
**Folder:** `experiments/17_sideband_plugins/`

Goals:
- Write a Telemetry plugin that reports custom sensor data (CPU temp, disk usage, etc.)
- Write a Command plugin that executes an action when triggered via LXMF
- Write a Service plugin that reacts to Sideband lifecycle events
- Hot-reload plugins without restarting Sideband

Plugin types:
| Type | Triggered by | Returns |
|---|---|---|
| Telemetry | Periodic or on-demand | Dict of sensor values |
| Command | Incoming LXMF message matching prefix | LXMF reply |
| Service | Sideband events (start, message, etc.) | — |

Source reference: `sources/Sideband/docs/example_plugins/`

```bash
# Reference plugins to study:
# bme280_telemetry.py — temperature/humidity/pressure
# basic.py            — minimal command plugin template
# service.py          — minimal service plugin template
# gpsd_location.py    — GPS via gpsd daemon
```

---

### Module 18 — lxmf-cli Bots & Automation
**Folder:** `experiments/18_lxmf_cli_bots/`

Goals (progressive):
1. Run `lxmf-cli` and send a message to yourself
2. Enable `echo_bot` plugin — auto-replies to every message
3. Add `keyword_alert` — fires on specific words in received messages
4. Enable `away_bot` — auto-reply with a custom message while you're offline
5. Explore `rssh.py` — reverse SSH tunnel back to a machine over the RNS mesh (reach machines behind NAT)
6. Explore `telegram_bridge.py` — bridge your LXMF contacts into Telegram

Key insight: lxmf-cli plugins use a simple interface — `on_message()` + `handle_command()` — and hot-reload on file change.

Source reference: `sources/lxmf-cli/plugins/`

```bash
# Run lxmf-cli (creates persistent identity in lxmf_client_storage/)
pixi run python ../sources/lxmf-cli/lxmf-cli.py
```

---

## Infrastructure Track

### Module 19 — Multi-Hop Routing Deep Dive
**Folder:** `experiments/19_multihop/`

Goals:
- Run `rns_hop_simulator` to create a 3-hop chain on a single machine
- Watch how announces propagate hop by hop and build the path table
- Use `rnpath` to inspect the table and see hop counts
- Configure a node as a Transport Instance (`enable_transport = yes`) and observe how routing changes
- Understand announce propagation rules: hop limit, rate limiting, duplicate suppression

Key insight: RNS builds paths from announces. A node only knows how to reach a destination after it has heard (or been told about) an announce from it.

Source reference: `sources/RNS-Tools/rns_hop_simulator/`

```bash
# 3-hop simulator
pixi run python ../sources/RNS-Tools/rns_hop_simulator/rns_hop_simulator.py \
    -c 3 --cfg_entry entry.cfg --cfg_exit exit.cfg
```

---

### Module 20 — Network Analysis & Announce Directory
**Folder:** `experiments/20_announce_directory/`

Goals:
- Run `rns_announce_directory` to collect all heard announces into SQLite
- Query the database: which destinations have we seen, when, with what app_data, from how many hops?
- Run `rns_announce_view` for a real-time console feed of announces (like a network scanner)
- Serve a NomadNet page with a browse interface over RNS
- Understand what you can learn about a mesh just by listening

Source reference: `sources/RNS-Tools/rns_announce_directory/`, `rns_announce_view/`

```bash
# Start the collector
pixi run python ../sources/RNS-Tools/rns_announce_directory/rns_announce_directory.py

# Real-time view
pixi run python ../sources/RNS-Tools/rns_announce_view/rns_announce_view.py
```

---

### Module 21 — RETCON: Event Mesh Deployment
**Folder:** `experiments/21_retcon/`

Goals:
- Understand RETCON's two modes: Transport (relay node) and Client (WiFi AP + MeshChat)
- Build a RETCON image for a Raspberry Pi
- Deploy 2+ Pi nodes and form a mesh automatically
- Administer a node via LXMF (change mode, AP password, etc.)
- Understand the use case: conferences, emergency response, off-grid events

Config profiles to study:
- `default.config` — minimal reference config
- `dc33.config` — DEF CON 33 mesh (real-world example)
- `chimesh.config` — community mesh example

Source reference: `sources/RETCON/`

```bash
# Build a RETCON image (requires Debian 12+, 8 GB RAM)
cd ../sources/RETCON
./install_prereqs.sh
cp retcon_profiles/default.config my_event.config
# edit my_event.config — set node name, wifi credentials, etc.
./build_retcon.sh my_event.config
```

---

## Advanced Network Layer

### Module 22 — IP over RNS
**Folder:** `experiments/22_ip_over_rns/`

Goals:
- Run `rns-tun-rs` to create a TUN virtual network interface over RNS (requires root)
- Reach a remote machine by its virtual IP address as if it were on a local network
- Step up to `rns-vpn-rs` for a full P2P VPN with CIDR addressing and peer-by-hash configuration
- Understand what this enables: any IP protocol (SSH, HTTP, UDP games) over any RNS transport

Key insight: rns-tun-rs is ~300 lines; rns-vpn-rs adds proper routing and multi-peer. Both use Reticulum-rs (Rust) under the hood.

Source references:
- `sources/rns-tun-rs/` — TUN device
- `sources/rns-vpn-rs/` — P2P VPN

```bash
# Build
cd ../sources/rns-tun-rs && cargo build --release
cd ../sources/rns-vpn-rs && cargo build --release

# TUN (two terminals, both root)
sudo ./target/release/server -p 4242
sudo ./target/release/client -s 192.168.0.99:4242

# VPN — configure Config.toml with peer destination hashes, then:
sudo ./target/release/rns-vpn
```

---

### Module 23 — Custom Interface Plugin
**Folder:** `experiments/23_custom_interface/`

Goals:
- Read and understand `ExampleInterface.py` — how any physical layer attaches to RNS
- Understand what an interface must implement: `process_incoming()`, `process_outbound()`, MTU, bitrate
- Write a minimal loopback-only interface (useful for testing without network)
- Understand how RNS is completely transport-agnostic: LoRa, TCP, serial, audio modem — all the same from the stack's perspective

Key concepts: `RNS.Interfaces.Interface`, `process_incoming`, `process_outbound`, `bitrate`, `online`, framing responsibility

Source reference: `sources/Reticulum/Examples/ExampleInterface.py`

---

## Expanded Capstone Projects

### Project D — Reverse SSH & Remote Access
**Folder:** `projects/remote_access/`

Build a system to reach machines behind NAT via the RNS mesh:
- Install `lxmf-cli` with `rssh.py` plugin on a remote machine
- Send it an LXMF command → it opens a reverse SSH tunnel back to you
- No port forwarding, no VPN, no static IP needed
- Works over any RNS transport (WiFi, LoRa, TCP)

Source reference: `sources/lxmf-cli/plugins/rssh.py`

---

### Project E — Automated Range Testing
**Folder:** `projects/range_testing/`

Build a systematic LoRa range testing rig:
- Flash `rangetest_server.py` to a portable device (Pi + RNode)
- Run `rangetest_client.py` on a laptop while walking/driving away
- Logs: RSSI, SNR, hop count, delivery %, GPS coordinates (if available)
- Post-process into a coverage map (matplotlib or folium)

Source reference: `sources/lxmf-cli/plugins/rangetest_client.py`, `rangetest_server.py`

---

### Project F — Telegram ↔ LXMF Bridge
**Folder:** `projects/telegram_bridge/`

Bridge your LXMF mesh contacts into Telegram:
- Run `telegram_bridge.py` plugin in lxmf-cli on a server node
- Messages from Telegram contacts appear as LXMF messages on the mesh
- Replies from the mesh are forwarded back to Telegram
- Useful for contacts who won't run Reticulum but you want to reach via mesh

Requires: Telegram Bot API token

Source reference: `sources/lxmf-cli/plugins/telegram_bridge.py`

---

## Suggested Order for Hardware Progression

```
Week 1:   Modules 00–03   (two terminal windows on one laptop)
Week 2:   Modules 04–05   (still single machine, two processes)
Week 3:   Modules 06–07   (LXMF + file transfer)
Week 4:   Modules 08–09   (two laptops on WiFi, then TCP)
Week 5:   Module 10       (voice call between two machines)
Week 6:   Module 11       (ESP32, get it on the network)
Week 7:   Modules 12–15   (Rust interop, broadcast, identify, ratchets)
Week 8:   Modules 16–18   (Sideband mobile + plugins, lxmf-cli bots)
Week 9:   Modules 19–21   (multi-hop, announce analysis, RETCON)
Week 10:  Modules 22–23   (IP over RNS, custom interface)
Week 11+: Projects         (pick from A–F, build it out)
```

Hardware to acquire for full experience:
- 2x LilyGO T-Beam (ESP32 + SX1276 LoRa + GPS) — RNode firmware + microReticulum experiments
- or 1x T-Beam as RNode interface + 1x generic ESP32 for microReticulum
- Raspberry Pi 4 or 5 (RETCON + home assistant + range testing server)
- Android phone (Sideband + mobile mesh experiments)
