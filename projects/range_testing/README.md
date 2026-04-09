# Project E — Automated Range Testing

Systematically measure LoRa coverage: RSSI, SNR, delivery rate, and hop count vs distance.
Post-process into a coverage map.

## Hardware

- Laptop running `rangetest_client.py` + Python RNS + RNode (USB LoRa)
- Portable server: Raspberry Pi + RNode, running `rangetest_server.py`
- Optional: GPS dongle on laptop for position tagging

## Architecture

```
[Server — fixed location]          [Client — moving]
  rangetest_server.py                rangetest_client.py
        │                                  │
        │◀──── probe message ──────────────┤
        │──── LXMF reply (RSSI/SNR) ──────▶│
        │                                  │  logs: distance, RSSI, SNR, delivery %
```

## Run

```bash
# Server (fixed)
pixi run python ../sources/lxmf-cli/plugins/rangetest_server.py

# Client (walking/driving)
pixi run python ../sources/lxmf-cli/plugins/rangetest_client.py \
    --server <server_hash>
```

## What to build

- `projects/range_testing/analyse.py` — read the log CSV, compute delivery % per distance bucket
- `projects/range_testing/plot_coverage.py` — generate a coverage map with matplotlib or folium
  (GPS lat/lon → colour-coded scatter plot by RSSI)
- `projects/range_testing/configs/` — RNode configs for different LoRa spreading factors

## Metrics to capture

| Metric | What it tells you |
|---|---|
| RSSI (dBm) | Received signal strength — higher is better |
| SNR (dB) | Signal above noise floor — key for LoRa decode |
| Delivery % | Packet loss at this range |
| Hop count | Whether signal is direct or relayed |
| Distance (m) | GPS or manual log |

## Source reference

`sources/lxmf-cli/plugins/rangetest_client.py`
`sources/lxmf-cli/plugins/rangetest_server.py`
