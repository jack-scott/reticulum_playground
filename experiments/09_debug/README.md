# Module 09 — Debug & Analysis

## Goal

Use the RNS debug tools to understand what's happening on the network.

## Tools

### rnstatus — Interface Status

```bash
pixi run rnstatus
```

Shows: interface name, type, state, bytes sent/received, packets sent/received.

### rnpath — Routing Table

```bash
# Show all known paths
pixi run python -m RNS.Utilities.rnpath -t

# Look up path to a specific destination
pixi run python -m RNS.Utilities.rnpath <destination_hash>

# Flush all paths (force rediscovery)
pixi run python -m RNS.Utilities.rnpath -f
```

### rnprobe — Connectivity Check

```bash
# Test if a destination is reachable (sends a packet, waits for proof)
pixi run python -m RNS.Utilities.rnprobe <destination_hash>

# With timeout
pixi run python -m RNS.Utilities.rnprobe --timeout 10 <destination_hash>
```

### rns_announce_view — Live Announce Sniffer

Watch all announces heard by this node in real-time:

```bash
# Watch all announces (replace "app_name" with a specific aspect to filter)
pixi run python sources/RNS-Tools/rns_announce_view/rns_announce_view.py -f app_name
```

### rns_hop_simulator — Multi-Hop Test on One Machine

Simulates N transport hops using multiple RNS instances connected via TCP:

```bash
# Build config files first (see hop_sim/ subdirectory)
pixi run python sources/RNS-Tools/rns_hop_simulator/rns_hop_simulator.py \
    -c 3 \
    --cfg_entry experiments/09_debug/hop_sim/entry.config \
    --cfg_exit experiments/09_debug/hop_sim/exit.config
```

Then run announcer/listener pointing at entry and exit configs respectively.

### Log Levels

Set in config or programmatically:

```python
RNS.loglevel = RNS.LOG_DEBUG    # 7 — very verbose
RNS.loglevel = RNS.LOG_INFO     # 5 — useful info
RNS.loglevel = RNS.LOG_WARNING  # 3 — only warnings
```

Or via CLI: `rnsd -v` (verbose), `rnsd -vv` (very verbose)

## Experiments

1. Run `rnstatus` while running the echo experiment — watch byte counts change
2. Run `rnpath -t` before and after an announce — see paths appear
3. Use `rns_announce_view` while running any experiment — observe what announces look like
4. Set up hop simulator with 3 hops — verify that rnpath shows hop count = 3
