# Reticulum Playground

A structured learning repo for [Reticulum](https://reticulum.network) — a cryptographic, decentralised mesh networking stack that works over LoRa, WiFi, serial, Ethernet, I2P, and more.

## What This Repo Is

Hands-on experiments, reference docs, and capstone projects for learning Reticulum from scratch through to real hardware deployments. Everything is kept here so context builds across sessions.

Source repos are in `../reticulum_sources/`. See `docs/resources_map.md` for a full inventory of what's there.

## Quick Start

```bash
# Install pixi if you don't have it
curl -fsSL https://pixi.sh/install.sh | bash

# Install the environment (no global installs)
pixi install

# Verify everything works
pixi run verify

# Run the RNS daemon (in a separate terminal)
pixi run rnsd
```

## Structure

```
reticulum_playground/
├── pixi.toml                  # Python environment (rns, lxmf, lxst)
├── docs/
│   ├── resources_map.md       # All source repos — what each one is and what's in it
│   ├── curriculum.md          # Ordered learning path (modules + projects)
│   ├── concepts.md            # Core RNS concept glossary
│   └── hardware.md            # Hardware guide (ESP32, Pi, mobile, LoRa)
├── experiments/
│   ├── 00_setup/              # Verify install, first identity
│   ├── 01_hello_rns/          # Announce + callback
│   ├── 02_addressing/         # Identity, hashes, recall
│   ├── 03_echo/               # Packet echo server/client, RTT, RSSI
│   ├── 04_links/              # Encrypted links, Channel, Buffer
│   ├── 05_requests/           # Request/Response (RPC over RNS)
│   ├── 06_lxmf/               # LXMF messaging, propagation nodes
│   ├── 07_resources/          # File transfer (Resource, rncp)
│   ├── 08_transports/         # Interface configs: WiFi, serial, TCP, LoRa
│   ├── 09_debug/              # rnprobe, rnpath, rnstatus, hop simulator
│   ├── 10_lxst_audio/         # Voice calls (Opus, Codec2)
│   └── 11_microcontrollers/   # ESP32 microReticulum (C++/PlatformIO)
├── projects/
│   ├── home_assistant/        # Sensor telemetry + control over LXMF
│   ├── viz_debug/             # Network visualiser and debug dashboard
│   └── drone_sideband/        # MAVLink over RNS (rns-mavlink-rs)
└── tools/
    └── (helper scripts)
```

## Learning Path

Start at `docs/curriculum.md` for the full ordered module list. The short version:

1. **Fundamentals** (experiments 00–05): install, announce, addressing, echo, links, requests
2. **Messaging** (06–07): LXMF, propagation nodes, file transfer
3. **Transports** (08–09): WiFi, serial, LoRa config, debugging
4. **Streaming** (10): LXST voice/audio
5. **Hardware** (11): ESP32 with microReticulum C++
6. **Projects**: Home Assistant, visualiser, drone link

## Environment Notes

- Python environment managed by [pixi](https://pixi.sh) — no global installs needed
- C++/PlatformIO work (microReticulum, RNode firmware) uses Docker — see `docs/hardware.md`
- Rust tools (rns-mavlink-rs, rns-vpn-rs) use Docker — see `projects/drone_sideband/`
- All experiments use `--config ./rns_config` to keep RNS state local to the experiment directory

## Key Concepts

See `docs/concepts.md`. The one thing to internalise first:

> An **address** in Reticulum is not a location — it's a **hash of an identity**. Your address never changes when you move between WiFi, LoRa, serial, or Ethernet. The network routes to *who you are*, not *where you are*.
