# Reticulum Playground — AI Session Context

## What This Repo Is

A structured learning and experimentation repo for Reticulum networking. The goal is to learn Reticulum by doing — working through a curriculum of experiments, building up to capstone projects.

## Source Repos Location

All reference source code is at `../reticulum_sources/` (relative to this repo). Full inventory in `docs/resources_map.md`.

Key repos to reference:
- `../reticulum_sources/Reticulum/` — Python reference impl + 14 examples in `Examples/`
- `../reticulum_sources/LXMF/` — messaging protocol, `docs/example_sender.py` + `example_receiver.py`
- `../reticulum_sources/microReticulum/` — C++ MCU port, `platformio.ini` for board configs
- `../reticulum_sources/rns-mavlink-rs/` — drone MAVLink bridge (Rust)
- `../reticulum_sources/RNode_Firmware/` — LoRa radio firmware (Arduino/C++)

## Environment

- Python environment: **pixi** (`pixi.toml` in root). Run Python via `pixi run python`.
- C++/PlatformIO: use **Docker** (see `docs/hardware.md`)
- Rust tools: use **Docker** (see project-specific READMEs)
- RNS config: always pass `--config ./rns_config` or `RNS.Reticulum("./rns_config")` to keep state local to each experiment directory

## Repo Structure

```
experiments/     # Numbered learning modules (00_setup through 11_microcontrollers)
projects/        # Capstone projects (home_assistant, viz_debug, drone_sideband)
docs/            # Reference docs (resources_map, curriculum, concepts, hardware)
tools/           # Helper scripts
```

## Key Facts About Reticulum

- **No IP addresses** — destinations are 16-byte truncated hashes of (public_key + app_name + aspects)
- **No source addresses in packets** — initiator anonymity is built in
- **Transport nodes** route blindly via cryptographic proofs (not administrative tables)
- **Client mode** vs **Transport mode** — set `enable_transport = yes` in config
- **Announce** = broadcasting your presence; the network builds routing tables from announces
- **Link** = 3-packet encrypted session setup (297 bytes total), provides forward secrecy
- **Resource** = large data transfer over a Link (auto-chunked, compressed, checksummed)
- **LXMF** = the standard messaging layer on top of RNS (not part of core RNS)
- **RNode** = a radio interface (not a Reticulum node itself) — ESP32 + LoRa that a host attaches to

## Platform / Language Matrix for MCUs

| Platform | Recommended | Notes |
|---|---|---|
| ESP32 (standalone RNS node) | microReticulum C++ / PlatformIO | Full RNS on-device |
| ESP32 (LoRa interface only) | RNode_Firmware | Makes ESP32 a transparent radio for a Linux host |
| Raspberry Pi | Python RNS | Full reference impl |
| Linux laptop | Python RNS | Primary dev platform |
| Android/iOS | Sideband (pip install sbapp) | Kivy-based GUI |
| Raspi Pico | C++ possible, untested | No explicit PlatformIO support yet |
| MicroPython | Not supported | microReticulum is C++, not MicroPython |
| Rust on bare metal | Not yet | Reticulum-rs uses std, targets Linux |

## Coding Conventions

- Keep RNS config local: `RNS.Reticulum("./rns_config")`
- Always add `Serial.println()` / `Serial.printf()` debug output in firmware
- Use pixi for all Python work — no global pip installs
- Helper scripts go in `tools/`
