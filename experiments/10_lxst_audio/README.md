# Module 10 — LXST Voice & Audio

## Goal

Make a voice call between two machines using LXST. Understand codec tradeoffs.

## System Requirements

```bash
# Debian 12/13
sudo apt install python3-pyaudio codec2

# Verify pyaudio works
python -c "import pyaudio; p = pyaudio.PyAudio(); print(p.get_device_count(), 'audio devices')"
```

## Using rnphone (part of LXST)

```bash
# Install LXST (already in pixi.toml)
# Then use the rnphone program:
pixi run python -m lxst.rnphone
```

rnphone provides a simple voice call interface over LXMF. It announces itself and accepts incoming calls.

## Codec Comparison

| Codec | Bitrate | Works over | Quality |
|---|---|---|---|
| Codec2 1200 | 1.2 kbps | LoRa SF8+ | Intelligible voice, radio quality |
| Codec2 2400 | 2.4 kbps | LoRa SF7 | Good voice |
| Opus 4.5k | 4.5 kbps | Fast LoRa / WiFi | Good voice |
| Opus 8k | 8 kbps | WiFi | Clear voice |
| Opus 24k | 24 kbps | WiFi/LAN | Near-CD quality |

## LXST Pipeline Concept

```
Microphone (Source)
    │
    ▼
Codec2/Opus Encoder (Processing)
    │
    ▼
LXST Network (over RNS Link)
    │
    ▼
Codec2/Opus Decoder (Processing)
    │
    ▼
Speaker (Sink)
```

See pipeline examples in `../reticulum_sources/LXST/examples/`.

## Status Note

LXST is early alpha. APIs change frequently. `rnphone` in Sideband is the most battle-tested path for voice calls. The Python `lxst` package examples are good for understanding the pipeline architecture.
