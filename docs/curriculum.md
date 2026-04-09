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

## Suggested Order for Hardware Progression

```
Week 1:  Modules 00–03  (two terminal windows on one laptop)
Week 2:  Modules 04–05  (still single machine, two processes)
Week 3:  Modules 06–07  (LXMF + file transfer)
Week 4:  Module 08–09   (two laptops on WiFi, then TCP)
Week 5:  Module 10      (voice call between two machines)
Week 6:  Module 11      (ESP32, get it on the network)
Week 7+: Projects        (pick one, build it out)
```

Hardware to acquire for full experience:
- 2x LilyGO T-Beam (ESP32 + SX1276 LoRa + GPS) — RNode firmware + microReticulum experiments
- or 1x T-Beam as RNode interface + 1x generic ESP32 for microReticulum
- Raspberry Pi 4 or 5 (RETCON + home assistant)
- Android phone (Sideband)
