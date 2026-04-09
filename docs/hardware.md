# Hardware Guide

Platform options, language decisions, and setup instructions.

---

## Platform Matrix

| Platform | Language | Approach | Notes |
|---|---|---|---|
| Linux laptop | Python | `pip install rns` via pixi | Primary dev platform |
| Raspberry Pi | Python | `pip install rns` or RETCON image | Full RNS, all features |
| Android | Python (Kivy) | Sideband APK | Download from GitHub releases |
| iOS | Python (Kivy) | Sideband (TestFlight) | Same codebase as Android |
| ESP32 (full node) | C++ | microReticulum + PlatformIO | Missing: Resource, Channel, Buffer |
| ESP32 (LoRa interface) | C++ (firmware) | RNode_Firmware | Makes ESP32 a radio interface for a host |
| RAK4631 (nRF52840) | C++ | microReticulum + PlatformIO | 28KB flash limit for path table |
| Raspi Pico (RP2040) | C++ | microReticulum (untested) | No platformio.ini board definition — needs work |
| Embedded Linux (Pi/Jetson) | Rust | Reticulum-rs | Good for drone companion computers |
| MicroPython | — | **Not supported** | microReticulum is C++, not MicroPython |

---

## Linux Laptop / Desktop

### Setup

```bash
# Install pixi (manages isolated Python envs)
curl -fsSL https://pixi.sh/install.sh | bash

# From repo root:
pixi install
pixi run verify
```

### Running rnsd as a service (optional)

```bash
# One-off
pixi run rnsd

# Or install system-wide for always-on service:
pip install rns
sudo systemctl enable --now rnsd
```

### WiFi AutoInterface

The default config uses `AutoInterface` which automatically discovers other Reticulum nodes on the same LAN via UDP multicast. No config needed for local testing between two machines on the same WiFi network.

---

## Raspberry Pi

### Full setup (Python RNS)

```bash
# Debian 12/13
sudo apt install python3-pip python3-pyaudio codec2

pip install rns lxmf lxst sbapp --break-system-packages

# Run daemon
rnsd
```

### LXST audio dependencies (voice calls)

```bash
# Debian 13 Trixie
sudo apt install python3-pyaudio codec2 xclip xsel

# Debian 12 Bookworm
sudo apt install python3-pip python3-pyaudio python3-dev build-essential \
    libopusfile0 libsdl2-dev libavcodec-dev portaudio19-dev codec2 libcodec2-1.0

# I2C for hardware control
pip install smbus2 --break-system-packages
sudo raspi-config  # enable I2C under Interface Options
sudo apt install python3-rpi.gpio
```

### RETCON — Turnkey Mesh Pi Image

For deploying a Pi as a mesh relay or access point node without manual config.

```bash
# On a Debian 12+ build machine:
git clone https://github.com/DanBeard/RETCON.git
cd RETCON
sudo ./install_prereqs.sh

# Copy and edit a profile
cp retcon_profiles/default.config retcon_profiles/active

# Build the image (takes a while)
./build_retcon.sh

# Flash to SD card
sudo dd if=output.img of=/dev/sdX bs=4M status=progress
```

Two modes:
- **Transport**: headless relay node (WiFi mesh + LoRa)
- **Client**: creates WiFi AP, serves MeshChat at `retcon.local`

Source: `sources/RETCON/`

---

## Android / iOS

### Android (Sideband)

1. Download the APK from [GitHub releases](https://github.com/markqvist/Sideband/releases/latest)
2. Verify APK certificate SHA-256: `1c65f01f586a2b73ac4eb8bf48730b3899d046447185fd9d005685a4af20cdea`
3. Install, allow unknown sources
4. Works with GrapheneOS and de-googled ROMs

Connect to desktop RNS: add a `TCPClientInterface` in Sideband settings pointing to your `rnsd` instance.

### Android Terminal (Termux) — lxmf-cli

```bash
pkg update && pkg upgrade
pkg install python git termux-api
pip install rns lxmf colorama prompt_toolkit

git clone https://github.com/fr33n0w/lxmf-cli.git
cd lxmf-cli
python lxmf-cli.py
```

---

## ESP32 — microReticulum (Full RNS Node)

Use this when you want the ESP32 to **be** a Reticulum node itself (announce, link, send/receive packets).

### Docker Setup (no local installs)

```bash
# From experiments/11_microcontrollers/ or projects/
docker run --rm -it \
    -v "$(pwd)":/workspace \
    --device /dev/ttyUSB0:/dev/ttyUSB0 \
    --privileged \
    platformio/platformio \
    pio run -e ttgo-t-beam -t upload
```

### Key platformio.ini environments

| Env name | Board |
|---|---|
| `ttgo-t-beam` | TTGO T-Beam v1.1 |
| `ttgo-lora32-v21` | TTGO LoRa32 v2.1 |
| `lilygo_tbeam_supreme` | T-Beam Supreme |
| `heltec_wifi_lora_32_V4` | Heltec v4 / Wireless Tracker |
| `wiscore_rak4631` | RAK4631 (nRF52840) |
| `native` | Desktop Linux (testing only) |

### PSRAM

For Heltec v4 / boards with PSRAM, add to build flags:
```
-DBOARD_HAS_PSRAM=1
-DRNS_DEFAULT_ALLOCATOR=RNS_PSRAM_ALLOCATOR
-DRNS_CONTAINER_ALLOCATOR=RNS_PSRAM_POOL_ALLOCATOR
-DRNS_PSRAM_POOL_BUFFER_SIZE=2048000
```

### Missing features (as of 2025)

Resource, Channel, Buffer, and Ratchets are not yet implemented in microReticulum. For experiments needing these, use Python RNS on a Pi instead.

Source: `sources/microReticulum/`

---

## ESP32 — RNode (LoRa Radio Interface)

Use this when you want the ESP32 to act as a **LoRa radio interface** for a host computer running Python RNS. The ESP32 just does radio — the host does Reticulum routing.

### Flash (via host Python RNS env)

```bash
# Connect ESP32 via USB, then:
pixi run rnodeconf --autoinstall

# Or via web flasher: https://liamcottle.github.io/rnode-flasher/
```

### Host config for RNode interface

Add to `~/.reticulum/config` (or the local `rns_config` in your experiment):

```
[[RNodeInterface]]
type = RNodeInterface
enabled = yes
port = /dev/ttyUSB0
frequency = 868000000    # 868 MHz (EU) or 915000000 (US/AU)
bandwidth = 125000       # 125 kHz
txpower = 14             # dBm (max ~27 depending on board)
spreadingfactor = 8      # 7-12, higher = longer range, slower
codingrate = 5           # 4/5 to 4/8
```

### Supported hardware

All LilyGO T-Beam, T3S3, LoRa32, T-Echo, Heltec LoRa32 v2/v3/v4, RAK4631, generic ESP32 + SX1276/1278/1262/1268/1280.

Source: `sources/RNode_Firmware/`

---

## Rust Tools (Embedded Linux — Docker)

For `rns-mavlink-rs`, `rns-tun-rs`, `rns-vpn-rs`:

```bash
docker run --rm -it \
    -v "$(pwd)":/workspace \
    -w /workspace \
    rust:latest \
    cargo build --release
```

For ARM targets (Pi companion computer):

```bash
docker run --rm -it \
    -v "$(pwd)":/workspace \
    -w /workspace \
    rust:latest \
    bash -c "rustup target add aarch64-unknown-linux-gnu && \
             apt-get install -y gcc-aarch64-linux-gnu && \
             cargo build --target aarch64-unknown-linux-gnu --release"
```

---

## Transport Decision: LoRa vs WiFi vs Serial

| Transport | Range | Bandwidth | Setup complexity | Good for |
|---|---|---|---|---|
| WiFi AutoInterface | LAN (~50m) | Mbps | Zero — just enable | Local dev, home network |
| WiFi TCP | Internet | Mbps | Need IP/port | Connecting across internet |
| LoRa (RNode) | 1–100+ km | 250 bps–2 kbps | Need RNode hardware | Long range, off-grid |
| Serial | Cable only | 9600–115200 bps | Just a cable | Pi↔laptop, KISS TNC |
| Ethernet | LAN | Mbps | Just a cable | Stable wired setup |
| I2P | Internet | kbps | I2P daemon needed | Anonymity-focused |

**Start with WiFi AutoInterface** — works on any LAN with zero config changes. Move to LoRa once you understand the protocol.

---

## LoRa Frequency/Spreading Factor Tradeoffs

| SF | Approx data rate | Range | Use when |
|---|---|---|---|
| 7 | ~5.5 kbps | Short | High throughput needed, short range ok |
| 8 | ~3.1 kbps | Medium | Good balance for most use |
| 9 | ~1.8 kbps | Medium-long | Longer range, still usable bandwidth |
| 10 | ~0.98 kbps | Long | Range-critical |
| 11 | ~0.54 kbps | Very long | Very range-critical |
| 12 | ~0.29 kbps | Maximum | Emergency/extreme range, very slow |

Bandwidth 125 kHz is standard. 250 kHz doubles data rate, halves range.
