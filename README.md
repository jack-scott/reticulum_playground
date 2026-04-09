# Reticulum Playground

A structured learning repo for [Reticulum](https://reticulum.network) — a cryptographic, decentralised mesh networking stack that works over LoRa, WiFi, serial, Ethernet, I2P, and more.

## What This Repo Is

Hands-on experiments, reference docs, and capstone projects for learning Reticulum from scratch through to real hardware deployments. Everything is kept here so context builds across sessions.

Source repos are in `sources/` as git submodules. See `docs/resources_map.md` for a full inventory of what's there.

## Quick Start

```bash
# Install pixi if you don't have it
curl -fsSL https://pixi.sh/install.sh | bash

# Pull all source repos (submodules)
git submodule update --init --recursive

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
├── tests/                     # Automated test suite (pixi run test)
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
│   ├── 05_reliable/           # Channel, Buffer, Request/Response (RPC)
│   ├── 06_lxmf/               # LXMF messaging, propagation nodes
│   ├── 07_resources/          # File transfer (Resource, rncp)
│   ├── 08_transports/         # Interface configs: WiFi, serial, TCP, LoRa
│   ├── 09_debug/              # rnprobe, rnpath, rnstatus
│   ├── 10_lxst_audio/         # Voice calls (Opus, Codec2)
│   ├── 11_microcontrollers/   # ESP32 microReticulum (C++/PlatformIO)
│   ├── 12_rust_interop/       # Python ↔ Rust (Reticulum-rs) wire compatibility
│   ├── 13_broadcast/          # GROUP destinations, shared-key broadcast
│   ├── 14_identify/           # Remote identity verification over links
│   ├── 15_ratchets/           # Ratchet-based per-packet forward secrecy
│   ├── 16_sideband_mobile/    # Android Sideband on the mesh
│   ├── 17_sideband_plugins/   # Write Sideband telemetry/command/service plugins
│   ├── 18_lxmf_cli_bots/      # lxmf-cli bots: echo, rssh, telegram bridge
│   ├── 19_multihop/           # Multi-hop routing, hop simulator, transport nodes
│   ├── 20_announce_directory/ # Announce collection, SQLite, network analysis
│   ├── 21_retcon/             # RETCON Pi mesh deployer for events
│   ├── 22_ip_over_rns/        # IP tunnelling + P2P VPN over RNS (Rust)
│   └── 23_custom_interface/   # Write a custom RNS interface plugin
├── projects/
│   ├── home_assistant/        # Sensor telemetry + control over LXMF
│   ├── viz_debug/             # Network visualiser and debug dashboard
│   ├── drone_sideband/        # MAVLink over RNS (rns-mavlink-rs)
│   ├── remote_access/         # Reverse SSH over the mesh (rssh plugin)
│   ├── range_testing/         # LoRa coverage measurement + mapping
│   └── telegram_bridge/       # Telegram ↔ LXMF bridge
└── tools/
    └── (helper scripts)
```

## Learning Path

Start at `docs/curriculum.md` for the full ordered module list. The short version:

1. **Fundamentals** (00–05): install, announce, addressing, echo, links, reliable delivery
2. **Messaging** (06–07): LXMF, propagation nodes, file transfer
3. **Transports** (08–09): WiFi, serial, LoRa config, debugging
4. **Streaming + Hardware** (10–11): LXST voice/audio, ESP32 with microReticulum C++
5. **Cross-implementation** (12): Python ↔ Rust interoperability
6. **Advanced messaging** (13–15): broadcast groups, identity verification, ratchets
7. **Applications** (16–18): Sideband mobile + plugins, lxmf-cli bots and automation
8. **Infrastructure** (19–21): multi-hop routing, network analysis, RETCON event mesh
9. **Network layer** (22–23): IP over RNS, custom interface plugins
10. **Projects** (A–F): Home Assistant, visualiser, drone, remote SSH, range testing, Telegram bridge

## Environment Notes

- Python environment managed by [pixi](https://pixi.sh) — no global installs needed
- `pixi run test` runs the automated RNS test suite; `pixi run test-interop` runs Rust interop tests
- C++/PlatformIO work (microReticulum, RNode firmware) uses Docker — see `docs/hardware.md`
- Rust tools (Reticulum-rs, rns-mavlink-rs, rns-vpn-rs) — build with `cargo build` directly
- All experiments use `--config ./rns_config` to keep RNS state local to the experiment directory

## Key Concepts

See `docs/concepts.md`. The one thing to internalise first:

> An **address** in Reticulum is not a location — it's a **hash of an identity**. Your address never changes when you move between WiFi, LoRa, serial, or Ethernet. The network routes to *who you are*, not *where you are*.
