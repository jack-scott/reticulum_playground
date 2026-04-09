# Project B — Network Visualiser & Debug Dashboard

## Goal

Build a real-time Reticulum network map. Listen to all announces, build a topology graph, display as a web dashboard.

## Architecture

```
announce_monitor.py
  - Registers an announce handler with aspect_filter=None
  - Receives ALL announces on the network
  - Stores: destination hash, app name, hop count, RSSI, SNR, timestamp, app_data
  - Writes to SQLite

dashboard.py (Flask)
  - Reads from SQLite
  - Serves JSON API for network topology
  - Serves HTML page with D3.js force-directed graph
  - Auto-refreshes every 5 seconds
```

## Node Data Model

```python
{
    "hash": "83b7328926fed0d2e6a10a7671f9e237",
    "app_name": "playground.hello",
    "hop_count": 2,
    "rssi": -85,         # dBm, from radio interfaces
    "snr": 7.5,          # dB
    "last_seen": 1712345678.0,
    "app_data": "optional payload",
}
```

## What to Build

- `tools/announce_monitor.py` — background announce listener + SQLite writer
- `projects/viz_debug/dashboard.py` — Flask app serving topology
- `projects/viz_debug/templates/index.html` — D3.js network graph
- `projects/viz_debug/api.py` — REST endpoints

## Reference

`sources/RNS-Tools/rns_announce_directory/rns_announce_directory.py`
— this does the SQLite storage part. Adapt the announce handler and storage, replace the NomadNet frontend with a web dashboard.

## Announce Handler API

```python
class NetworkMapHandler:
    aspect_filter = None  # receive ALL announces

    def received_announce(self, destination_hash, announced_identity, app_data):
        # destination_hash: bytes (16)
        # announced_identity: RNS.Identity (has .hash, .get_public_key())
        # app_data: bytes or None
        pass
```

Hop count is not directly available in the announce callback. It can be read from the transport path table after the announce: `RNS.Transport.hops_to(destination_hash)`
