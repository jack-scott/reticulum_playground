# Module 19 — Multi-Hop Routing Deep Dive

## Goal

Understand how RNS builds routing tables from announces, how paths are discovered across
multiple hops, and how to configure transport nodes.

## Key concepts

- RNS is **reactive** — a node only knows how to reach a destination after it has heard an announce from it (or had a path request propagated)
- `enable_transport = yes` — makes a node forward announces and relay packets for other nodes
- Hop limit — announces degrade with each hop; default max is 128 hops
- `rnpath` shows the current path table including hop counts and interface
- `has_path()` / `request_path()` — check/request a path programmatically

## Hop simulator

The hop simulator from RNS-Tools creates N RNS instances on one machine, connected in a chain via TCP:

```
[Entry Node] ──TCP──▶ [Relay 1] ──TCP──▶ [Relay 2] ──TCP──▶ [Exit Node]
```

```bash
cd ../sources/RNS-Tools/rns_hop_simulator
python rns_hop_simulator.py -c 3 \
    --cfg_entry entry.cfg \
    --cfg_exit exit.cfg
```

Then run a client pointing at the entry config and a server at the exit config — packets travel 3 hops.

## Exercises

1. Run the hop simulator with 3 hops, send a packet from entry to exit
2. Use `rnpath` to see the path table at each simulated node
3. Increase to 5 hops — does announce still reach the exit?
4. Set `announce_hop_limit = 3` in a relay config — what stops propagating?
5. Run `rnprobe` from entry to exit — measures RTT through all hops

## Announce propagation rules

- Each Transport node decrements hop count by 1 before reforwarding
- Duplicate announces are suppressed (hashed, stored in filter)
- Announce rate-limiting applies per-interface to prevent flooding
- Path table entry expires if not refreshed by a new announce

## Source reference

`sources/RNS-Tools/rns_hop_simulator/rns_hop_simulator.py`
