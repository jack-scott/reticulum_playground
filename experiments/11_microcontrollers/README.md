# Module 11 — Microcontrollers (microReticulum C++)

## Goal

Run Reticulum on an ESP32 using microReticulum (C++/PlatformIO). Get it to announce and communicate with a Python RNS host.

## No Local Installs — Docker Only

```bash
# Build for native Linux (test first, no hardware needed)
docker run --rm -it \
    -v /home/jack/Documents/projects/reticulum_sources/microReticulum:/workspace \
    -w /workspace \
    python:3.11 \
    bash -c "pip install platformio && pio run -e native14"

# Build and flash to TTGO T-Beam (USB must be accessible)
docker run --rm -it --privileged \
    -v /home/jack/Documents/projects/reticulum_sources/microReticulum:/workspace \
    -w /workspace \
    -v /dev:/dev \
    python:3.11 \
    bash -c "pip install platformio && pio run -e ttgo-t-beam -t upload && pio device monitor"
```

## Supported Boards

| PlatformIO env | Board | Notes |
|---|---|---|
| `native14` | Linux desktop | Test without hardware |
| `ttgo-t-beam` | TTGO T-Beam v1.1 | LoRa + GPS + ESP32 |
| `ttgo-lora32-v21` | TTGO LoRa32 v2.1 | Simpler, no GPS |
| `heltec_wifi_lora_32_V4` | Heltec v4 | Has PSRAM, more memory |
| `wiscore_rak4631` | RAK4631 | nRF52840, note 28KB flash limit |

## What microReticulum Can Do

Implemented and working:
- `RNS::Identity` — Ed25519 + X25519 keypair
- `RNS::Destination` — addressing, announce
- `RNS::Transport` — path table, routing
- `RNS::Link` — encrypted sessions
- `RNS::Packet` — send/receive

NOT yet implemented:
- `RNS::Resource` — large data transfer
- `RNS::Channel` / `RNS::Buffer` — reliable delivery
- Ratchets

## Custom Experiment Code

Put experiment code in `src/main.cpp`. The library is at `../reticulum_sources/microReticulum/src/`.

See the microReticulum source for API patterns — it mirrors the Python API closely:
```cpp
RNS::Reticulum rns;
RNS::Identity identity;
RNS::Destination dest(identity, RNS::Destination::IN, RNS::Destination::SINGLE, "playground", "hello");
dest.announce();
```

## Debug Output

All firmware experiments should have serial debug output. Monitor at 115200 baud:
```bash
docker run --rm -it --privileged -v /dev:/dev \
    python:3.11 \
    bash -c "pip install platformio && pio device monitor --port /dev/ttyUSB0 --baud 115200"
```

## Python ↔ ESP32 Interop

The ESP32 running microReticulum should be fully interoperable with Python RNS. To connect them:
1. Configure Python RNS with a `TCPClientInterface` pointing to the ESP32's TCP server, OR
2. Use a shared WiFi network with `AutoInterface` (ESP32 + Python both on same WiFi)
