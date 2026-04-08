# Module 00 — Setup & First Identity

## Goal

Confirm the environment works. Understand what RNS is doing at startup.

## Run It

```bash
pixi run verify
```

Expected output:
```
Checking imports...
  rns         0.x.x
  lxmf        0.x.x
  lxst        0.x.x

Starting Reticulum (local config)...
Generating identity...
  Identity hash : <a3b2...>
  Config path   : experiments/00_setup/rns_config

Creating a test destination...
  Destination hash : <7f91...>

All good. Environment is ready.
```

## What's Happening

1. `RNS.Reticulum(CONFIG_PATH)` — starts the stack. On first run it creates a default config at `rns_config/`. This config only uses `AutoInterface` (WiFi LAN broadcast) by default.
2. `RNS.Identity()` — generates a random Ed25519 + X25519 keypair. This is ephemeral (new each run). For persistent identities, save to a file — see Module 02.
3. `RNS.Destination(...)` — creates an addressable endpoint. The hash is deterministic: same identity + same app_name + aspects = same hash.

## Files Created

After running, `rns_config/` will contain:
```
rns_config/
├── config         # RNS configuration file
└── storage/       # Path tables, known identities, etc.
```

## Explore the Config

```bash
cat experiments/00_setup/rns_config/config
```

The default config enables `AutoInterface` which broadcasts on the local network via UDP multicast. Two machines on the same WiFi will automatically discover each other.

## Questions to Answer

1. What is the difference between an Identity hash and a Destination hash?
   - Run the script twice. Do the hashes change? Why?
2. What happens if you create two destinations with different aspects but the same identity?
3. Open `rns_config/config` — what does `enable_transport = no` mean? (See `docs/concepts.md`)
