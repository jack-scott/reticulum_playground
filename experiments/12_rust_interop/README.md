# Module 12 — Rust ↔ Python Interoperability

Demonstrates that Python RNS (reference implementation) and Reticulum-rs (Rust)
are wire-compatible and can exchange announce packets over TCP.

## What this tests

Both implementations use HDLC framing over TCP. The wire format is:
- Each frame is HDLC-escaped
- Frame boundary: `0x7E` flag byte
- Escape byte: `0x7D`, followed by escaped byte XOR'd with `0x20`

An **announce** packet contains:
- Destination hash (16 bytes, truncated SHA-256 of pubkey + name + aspects)
- Ed25519 public key
- Signature
- Optional app_data

Because both implementations derive destination hashes identically
(same truncated SHA-256 formula), a Rust-created destination hash is
directly interpretable by Python RNS and vice versa.

## Prerequisites

Build the Rust examples:

```bash
cd ../../reticulum_sources/Reticulum-rs
cargo build --example tcp_server --example tcp_client
```

Binaries land in `target/debug/examples/`.

## Run the tests

```bash
pixi run test-interop
```

Or for all tests including basics:

```bash
pixi run test && pixi run test-interop
```

## Test matrix

| Test | Direction | What it verifies |
|---|---|---|
| `test_rust_announces_to_python` | Rust → Python | HDLC framing, announce packet, crypto decode |
| `test_python_announces_to_rust` | Python → Rust | Reverse direction, Rust accepts Python packets |

## Architecture

```
test_rust_announces_to_python
─────────────────────────────
  [main test process]
      │
      ├── spawn subprocess: Python RNS TCPServer on :4242
      │       registers Handler(aspect_filter="example.app")
      │
      └── spawn subprocess: Rust tcp_client
              connects to 127.0.0.1:4242
              waits 3s
              announces SingleInputDestination("example", "app")
              │
              ▼ HDLC-framed TCP packet
  Python handler fires → writes hash to file → test asserts 16-byte hash


test_python_announces_to_rust
─────────────────────────────
  [main test process]
      │
      ├── spawn subprocess: Rust tcp_server on :4242
      │
      └── spawn subprocess: Python RNS TCPClient → :4242
              announces Destination("playground", "rust_interop")
              │
              ▼ HDLC-framed TCP packet
  Rust transport receives, processes without crash
  Test asserts Rust server still running after announce
```

Both sides use separate subprocesses because RNS is a process-level
singleton — only one instance per process.

## microReticulum (C++) native tests

The C++ port (microReticulum) does not have a TCP interface for native/desktop
builds — it uses a loopback-only interface. Native tests run entirely in one
process and cover crypto, transport, routing, and persistence.

Run the C++ tests:

```bash
cd ../../reticulum_sources/microReticulum
pixi run -e dev --manifest-path ../../reticulum_playground/pixi.toml pio test -e native14
```

Expected: 83 tests, all passing.

MCU cross-compilation (ESP32, nRF52) requires Docker — see
`docs/hardware.md` for the build workflow.
