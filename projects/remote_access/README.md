# Project D — Reverse SSH & Remote Access

Reach machines behind NAT via the RNS mesh — no port forwarding, no VPN, no static IP.

## How it works

```
[Remote machine, behind NAT]          [Your laptop, anywhere on mesh]
  lxmf-cli + rssh.py plugin
        │
        │  ◀── LXMF message: /rssh ──────────────────────────┐
        │                                                     │
        └──── opens SSH reverse tunnel ──────────────────────▶│
              (ssh -R port:localhost:22 your_laptop)
```

The remote machine receives an LXMF message, opens a reverse tunnel to you, and you SSH in
through it. RNS handles all the routing — the remote machine only needs to be able to reach
any RNS node.

## Setup

### Remote machine
```bash
# Install lxmf-cli + rssh plugin
git clone https://github.com/fr33n0w/lxmf-cli ../sources/lxmf-cli
cp ../sources/lxmf-cli/plugins/rssh.py lxmf_client_storage/plugins/

# Edit rssh.py — set your SSH public key
# Run lxmf-cli (starts the bot)
pixi run python ../sources/lxmf-cli/lxmf-cli.py
```

### Your laptop
```bash
# Get the remote machine's LXMF destination hash
# (it prints it on startup)

# Trigger the reverse shell
/rssh <remote_machine_hash>
```

## What to build

- `projects/remote_access/setup_remote.sh` — one-shot setup script for a remote machine
- `projects/remote_access/connect.sh` — wrapper that sends the LXMF trigger and waits for the SSH tunnel
- Configuration for multiple machines (names → destination hashes)

## Source reference

`sources/lxmf-cli/plugins/rssh.py`
