# Project C — Drone Sideband (MAVLink over RNS)

## Goal

Replace the traditional drone radio link with a Reticulum mesh using rns-mavlink-rs.
QGroundControl on laptop ↔ Pixhawk on drone, linked via RNS (LoRa or WiFi).

## Architecture

```
Drone (Companion Computer — Pi or similar)
  Pixhawk ──serial──► fc binary (Rust)
                           │
                        RNS mesh (LoRa via RNode, or WiFi)
                           │
Laptop
  gc binary (Rust) ──UDP──► QGroundControl (127.0.0.1:14550)
```

## Build the Binaries (Docker)

```bash
cd projects/drone_sideband

# Copy source
cp -r sources/rns-mavlink-rs/ ./rns-mavlink-rs/
cd rns-mavlink-rs

# Build for x86 Linux (laptop gc binary)
docker run --rm -it \
    -v "$(pwd)":/workspace \
    -w /workspace \
    rust:latest \
    cargo build --release --bin gc

# Build for ARM64 Linux (Pi companion computer fc binary)
docker run --rm -it \
    -v "$(pwd)":/workspace \
    -w /workspace \
    rust:latest \
    bash -c "
        rustup target add aarch64-unknown-linux-gnu
        apt-get update && apt-get install -y gcc-aarch64-linux-gnu
        CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER=aarch64-linux-gnu-gcc \
        cargo build --release --bin fc --target aarch64-unknown-linux-gnu
    "
```

## Configuration

### Gc.toml (laptop — ground control)

```toml
gc_udp_address = "127.0.0.1:14550"   # where QGroundControl listens
gc_reply_port = 9999                   # local port for QGC replies
fc_destination = ""                    # FILL IN: RNS hash of the fc node
```

### Fc.toml (companion computer — flight controller)

```toml
serial_port = "/dev/ttyACM0"           # serial port to Pixhawk
serial_baud = 115200                   # baud rate
gc_destination = ""                    # FILL IN: RNS hash of the gc node
```

## Setup Steps

1. Build binaries (above)
2. Start GC on laptop: `./target/release/gc`
3. Note the GC destination hash printed in the logs
4. Copy fc binary + Fc.toml to companion computer
5. Edit Fc.toml with GC destination hash
6. Start FC on companion computer: `./fc`
7. Note FC destination hash, edit Gc.toml
8. Restart GC
9. Open QGroundControl — MAVLink telemetry should appear

## Transport Options

### Bench testing (WiFi)

Both machines on same WiFi, AutoInterface in RNS config. No extra hardware needed.

### Field use (LoRa)

Attach an RNode to both machines (USB).

RNS config on both:
```
[[RNodeInterface]]
type = RNodeInterface
enabled = yes
port = /dev/ttyUSB1     # adjust — don't conflict with Pixhawk serial
frequency = 868000000
bandwidth = 125000
txpower = 17
spreadingfactor = 9     # SF9 for good range/bandwidth balance
codingrate = 5
```

## Reference

`sources/rns-mavlink-rs/`
`sources/Reticulum-rs/`

## Notes

- MAVLink is high-frequency (50Hz+ on some streams) — you'll need to configure MAVLink stream rates down for low-bandwidth LoRa links
- Use QGroundControl's MAVLink Inspector to see what's actually flowing
- rns-mavlink-rs uses Reticulum-rs internally — see its README for Kaonic (tactical radio) build instructions for ARM targets
