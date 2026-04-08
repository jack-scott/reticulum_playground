# Module 02 — Addressing Deep Dive

## Goal

Understand how destination hashes are derived. Save and reload identities. Use `rnid`.

## Key Questions

1. If you restart a script, does the destination hash change? (Yes — random identity each time)
2. If you save the identity to a file and reload it, does the hash stay the same? (Yes)
3. Two different identities with the same app_name + aspects — do they have the same destination hash? (No — hash includes public key)

## Experiments to Build

- `save_identity.py` — generate identity, save to `./my_identity`, print hash, exit
- `reload_identity.py` — load from `./my_identity`, verify same hash as before
- `recall_identity.py` — after hearing an announce, use `RNS.Identity.recall(dest_hash)` to get the identity back

## CLI Exploration

```bash
# Inspect an identity file
pixi run rnid --inspect ./experiments/02_addressing/my_identity

# Create a new identity
pixi run rnid --generate ./experiments/02_addressing/new_identity
```

## Reference

See `../reticulum_sources/Reticulum/RNS/Identity.py` for the full identity API.
How hashes are computed: `RNS/Destination.py` → `Destination.hash_from_name_and_identity()`
