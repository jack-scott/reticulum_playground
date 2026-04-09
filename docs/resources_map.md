# Reticulum Sources Map

All repos live at `sources/` inside this repo as git submodules.

To pull everything fresh on a new machine:

```bash
git submodule update --init --recursive
```

---

## Core Protocol

### `Reticulum/` — Python Reference Implementation
**The canonical spec and primary dev platform.**
GitHub: https://github.com/markqvist/Reticulum

| File | What it does |
|---|---|
| `RNS/Reticulum.py` | Stack init, config loading, shared instance |
| `RNS/Identity.py` | Ed25519+X25519 keys, recall/save/load, encryption |
| `RNS/Destination.py` | Addressing, announce, proof strategies |
| `RNS/Transport.py` | Routing tables, `has_path`, `request_path`, hop count |
| `RNS/Packet.py` | Wire-level packet construction and send |
| `RNS/Link.py` | Encrypted sessions (3 packets, 297 bytes, forward secrecy) |
| `RNS/Channel.py` | Reliable ordered delivery over a link |
| `RNS/Buffer.py` | Stream-like I/O over a link |
| `RNS/Resource.py` | Chunked transfer of large data (auto-compress, checksum, progress) |
| `RNS/__init__.py` | Public API surface |

**Examples (`Examples/`):**

| File | Teaches |
|---|---|
| `Minimal.py` | Stack init + announce (hello world) |
| `Announce.py` | Announce with app_data + register callback |
| `Echo.py` | Client/server with packet proofs, RTT measurement, RSSI/SNR |
| `Link.py` | Encrypted link setup, data exchange, link callbacks |
| `Channel.py` | Reliable delivery over a link |
| `Buffer.py` | Stream-like I/O over a link |
| `Request.py` | Lightweight RPC over a link |
| `Resource.py` | Large data transfer with progress |
| `Speedtest.py` | Throughput measurement |
| `Identify.py` | Remote identity verification over a link |
| `Ratchets.py` | Ratchet-based forward secrecy |
| `Broadcast.py` | GROUP destination (shared symmetric key broadcast) |
| `Filetransfer.py` | File transfer (like rncp) |
| `ExampleInterface.py` | How to write a custom interface plugin |

**Built-in CLI tools (from `pip install rns`):**

| Tool | What it does |
|---|---|
| `rnsd` | Daemon mode |
| `rnstatus` | Interface stats (tx/rx, link quality) |
| `rnpath` | View/flush routing tables |
| `rnprobe` | Connectivity check (like ping) |
| `rncp` | File copy over RNS |
| `rnx` | Remote command execution |
| `rnid` | Identity management, encrypt/decrypt |
| `rnodeconf` | Flash RNode firmware to ESP32 boards |

**Supported interface types:**
- Ethernet, TCP server/client, UDP/AutoInterface (WiFi LAN), Serial, KISS TNC
- RNode (LoRa over serial), Pipe/stdio, I2P

**Performance:** 150 bps to 500 Mbps. Designed around LoRa (~250 bps).

---

## Messaging Layer

### `LXMF/` — Lightweight Extensible Message Format
**The standard messaging protocol on top of RNS.**
GitHub: https://github.com/markqvist/LXMF

**Wire format (111 bytes overhead):**
```
16 bytes  destination hash
16 bytes  source hash
64 bytes  Ed25519 signature
N bytes   msgpack payload: [timestamp, content, title, fields_dict]
```

| File | What it does |
|---|---|
| `LXMF/LXMRouter.py` | All outbound/inbound queuing, delivery, path lookup, retries |
| `LXMF/LXMessage.py` | A single message (create, send, receive) |
| `LXMF/LXMPeer.py` | Propagation node peer sync logic |
| `LXMF/Handlers.py` | Propagation node logic |
| `docs/example_sender.py` | Minimal send example |
| `docs/example_receiver.py` | Minimal receive example |

**Delivery methods:**
1. `DIRECT` — over a Link (forward secrecy, default)
2. `OPPORTUNISTIC` — single packet, best-effort
3. Propagation node — store-and-forward for offline recipients

**Daemon:** `lxmd --propagation-node` runs a full propagation node.

---

## Streaming

### `LXST/` — Lightweight Extensible Signal Transport
**Real-time audio over RNS. EARLY ALPHA — APIs will change.**
GitHub: https://github.com/markqvist/LXST

| File | What it does |
|---|---|
| `LXST/Call.py` | Voice call setup/teardown |
| `LXST/Network.py` | RNS integration |
| `LXST/Pipeline.py` | Signal routing graph |
| `LXST/Sources.py` / `Sinks.py` | Audio I/O |
| `LXST/Generators.py` | Tone generators |
| `LXST/Filters.py` + `Filters.c` | DSP (C extension) |
| `LXST/Mixer.py` | Multi-channel mixing |

**Codec profiles:**
- Codec2: 700 bps–3.2 kbps (works over LoRa)
- Opus: 4.5–96 kbps (many voice/music profiles)
- Raw PCM: lossless, arbitrary sample rate

**Examples in `examples/`:** fileplayer, filerecorder, filesource, filters, mixer, pipelines, tone_generator

**System deps:** `python3-pyaudio codec2` (+ `smbus2`, `rpi.gpio` for hardware I2C on Pi)

---

## User-Facing Apps

### `Sideband/` — Full-Featured GUI Client
**Cross-platform: Android APK, Linux pip, macOS DMG, Windows ZIP.**
GitHub: https://github.com/markqvist/Sideband

- LXMF messaging + LXST voice calls
- Image, file, audio message transfers (Codec2 audio works over LoRa)
- P2P telemetry and location sharing, offline + online maps
- Encrypted QR paper messages
- Android as impromptu Transport Instance
- Remote command execution

**Plugin system (`docs/example_plugins/`):**

| Plugin | What it shows |
|---|---|
| `telemetry.py` | Custom telemetry sensor |
| `bme280_telemetry.py` | BME280 temp/humidity/pressure |
| `basic.py` | Command plugin template |
| `gpsd_location.py` | GPS location from gpsd |
| `windows_location.py` | Windows location provider |
| `lxmd_telemetry.py` | LXMF propagation node stats |
| `view.py` | Camera/stream viewing |
| `service.py` | Service plugin template |

**Install (Linux):** `pip install sbapp --break-system-packages`
**Daemon mode:** `sideband --daemon`

---

### `meshchat/` — Two Minimal Chat Implementations
GitHub: https://github.com/jardous/meshchat

| File | What it is |
|---|---|
| `meshchat.py` | Raw RNS console chat (no LXMF). Server/client pattern. |
| `lxmf_chat.py` | Minimal LXMF console client. Persistent identity. Auto-announce. |

Good for: understanding bare RNS vs LXMF from clean, minimal code.

---

### `lxmf-cli/` — Terminal LXMF Client
**Feature-rich CLI with plugin system. Works on Linux/Windows/Android (Termux).**
GitHub: https://github.com/fr33n0w/lxmf-cli

Key features: conversation threading, contact management, stamp-cost spam protection, blacklist, hot-reload plugins.

**Notable plugins in `plugins/`:**

| Plugin | What it does |
|---|---|
| `echo_bot.py` | Auto-reply echo |
| `away_bot.py` | Away message responder |
| `keyword_alert.py` | Keyword monitoring + alerts |
| `pgp.py` | Full PGP encryption layer over LXMF |
| `rssh.py` | Reverse SSH over LXMF |
| `telegram_bridge.py` | Bridge LXMF ↔ Telegram |
| `rangetest_client/server.py` | Automated range testing |
| `groupchat.py` | Multi-party group messaging |
| `telemetry.py` | Sensor telemetry collection |

---

## Hardware

### `RNode_Firmware/` — LoRa Radio Firmware (Arduino/C++)
**Turns ESP32+LoRa boards into RNode radio interfaces for a Linux host.**
GitHub: https://github.com/markqvist/RNode_Firmware

> RNode = a **radio interface** (like a USB network card), not a standalone Reticulum node. The host runs Python RNS and attaches to the RNode via serial USB.

**Key source files:**

| File | What it does |
|---|---|
| `RNode_Firmware.ino` | Main firmware entry |
| `Boards.h` | Pin mappings for all supported boards |
| `Modem.h` | LoRa modulation config |
| `Framing.h` | Serial framing protocol (KISS-like) |
| `sx126x.cpp` / `sx127x.cpp` / `sx128x.cpp` | Transceiver drivers |
| `Python Module/RNode.py` | Python lib to control RNode directly |

**Supported boards:** LilyGO T-Beam/T3S3/LoRa32/T-Echo, Heltec LoRa32 v2/v3/v4, RAK4631, SeeedStudio XIAO, generic ESP32.

**Supported transceivers:** SX1276, SX1278, SX1262, SX1268, SX1280

**Bands:** 433/868/915 MHz / 2.4 GHz. Range: up to 100+ km LoS.

**Flash:** `rnodeconf --autoinstall` (included in `pip install rns`)

**Active development** moved to [RNode_Firmware_CE](https://github.com/liberatedsystems/RNode_Firmware_CE).

---

### `microReticulum/` — C++ RNS for Microcontrollers
**Full C++ port of the Reticulum stack. PlatformIO. NOT MicroPython.**
GitHub: https://github.com/attermann/microReticulum

**Implemented:** Identity, Destination, Transport, Link, Packet, AES-256, persistence

**NOT yet:** Resource, Channel, Buffer, Ratchets

**Supported boards (from `platformio.ini`):**

| Env | Board |
|---|---|
| `ttgo-lora32-v21` | TTGO LoRa32 v2.1 |
| `ttgo-t-beam` | TTGO T-Beam |
| `lilygo_tbeam_supreme` | T-Beam Supreme |
| `heltec_wifi_lora_32_V4` | Heltec v4 / Wireless Tracker (PSRAM) |
| `wiscore_rak4631` | RAK4631 (nRF52840) |
| `native` | Linux/macOS (for testing) |

**Raspi Pico:** NOT in platformio.ini. Possible but requires a new board definition.

**Dependencies:**
- `ArduinoJson ^7.4.2`
- `MsgPack ^0.4.2`
- `attermann/Crypto` (Curve25519 support)
- `attermann/microStore` (Bitcask storage for path table)

**Build (Docker):** `pio run -e ttgo-t-beam -t upload`

---

## Rust Ecosystem (Beechat Network Systems)

### `Reticulum-rs/` — Rust RNS Implementation
**Targets embedded Linux (Pi, Jetson). NOT bare-metal MCU (uses std).**
GitHub: https://github.com/BeechatNetworkSystemsLtd/Reticulum-rs

Supports: TCP, serial, UDP, Kaonic (gRPC-based tactical radio).

| Directory | Contents |
|---|---|
| `src/` | Core protocol (identity, destination, transport, packet, iface, crypt) |
| `examples/` | tcp_client, tcp_server, kaonic_client/mesh, link_client, multihop, udp_link, testnet_client |
| `proto/kaonic/` | Kaonic gRPC .proto definition |

**Build:** `cargo build --release` (requires `protoc` for Kaonic)

---

### `rns-mavlink-rs/` — MAVLink Bridge over RNS
**Connects flight controller to ground station over Reticulum mesh.**
GitHub: https://github.com/BeechatNetworkSystemsLtd/rns-mavlink-rs

| Component | Runs on | Does |
|---|---|---|
| `fc` binary | Companion computer (Pi) | Serial from Pixhawk → RNS → GCS |
| `gc` binary | Laptop | RNS → UDP to QGroundControl on `127.0.0.1:14550` |

**Config files:** `Fc.toml` (serial_port, serial_baud, gc_destination hash), `Gc.toml` (gc_udp_address, gc_reply_port, fc_destination hash)

**Systemd services included.** Kaonic build via Docker for ARM targets.

---

### `rns-tun-rs/` — TUN Interface over RNS
GitHub: https://github.com/BeechatNetworkSystemsLtd/rns-tun-rs
Minimal TUN virtual network device over RNS. Server + client. Requires root. Entire impl in `src/lib.rs`.

---

### `rns-vpn-rs/` — P2P VPN over RNS
GitHub: https://github.com/BeechatNetworkSystemsLtd/rns-vpn-rs
Full peer-to-peer VPN. CIDR subnet (`Config.toml`), peers by destination hash. X25519+Ed25519 keys via `genkeys.sh`.

---

## Infrastructure

### `RETCON/` — Raspberry Pi Mesh Deployer
**Builds pre-configured Pi SD images that auto-form mesh networks.**
GitHub: https://github.com/DanBeard/RETCON

| Mode | What it does |
|---|---|
| Transport | Headless relay — extends mesh range via WiFi + LoRa |
| Client | WiFi AP + MeshChat at `retcon.local` for end users |

Auto-detects RNodes and Meshtastic devices. Admin via LXMF.

**Config profiles:** `retcon_profiles/default.config`, `dc33.config`, `chimesh.config`

**Build flow:** `install_prereqs.sh` → configure profile → `build_retcon.sh` → `dd` to SD card

---

### `RNS-Tools/` — Utility Scripts
GitHub: https://github.com/SebastianObi/RNS-Tools
Standalone Python tools by Sebastian Obi. All support systemd service mode.

| Tool | What it does |
|---|---|
| `rns_announce_directory/` | SQLite/Postgres DB of all heard announces. NomadNet page viewer. |
| `rns_announce_view/` | Real-time console viewer of all announces (hash, app name, timestamp, hop count) |
| `rns_announce_test/` | Automated announce testing — sends configurable announces, logs responses |
| `rns_hop_simulator/` | Simulates N hops on one machine via TCP. Critical for local multi-hop testing. |
| `rns_server_page/` | Hosts a NomadNet-browsable page over RNS |

**Hop simulator CLI:** `rns_hop_simulator.py -c 3 --cfg_entry entry.cfg --cfg_exit exit.cfg`
