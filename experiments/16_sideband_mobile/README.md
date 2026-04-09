# Module 16 — Mobile Networking with Sideband

## Goal

Connect an Android phone running Sideband to your desktop RNS node and exchange LXMF messages,
share location, and optionally use the phone as a Transport Instance (router).

## Prerequisites

- Android phone (works on de-googled ROMs including GrapheneOS)
- APK from: https://github.com/markqvist/Sideband/releases (never from app stores)
- Desktop running `pixi run rnsd`

## Setup

### Desktop
Start rnsd with a TCP server interface in the config:

```ini
[interfaces]
  [[TCPServer]]
  type = TCPServerInterface
  enabled = yes
  listen_ip = 0.0.0.0
  listen_port = 4965
```

```bash
pixi run rnsd
```

### Phone (Sideband)
1. Install APK
2. Open Sideband → Settings → Interfaces → Add Interface
3. Type: TCP Client, host: your laptop IP, port: 4965
4. Restart Sideband

## Exercises

1. Exchange LXMF messages between phone and laptop
2. Enable location sharing on phone — view position on desktop
3. Enable Transport mode on phone (`Settings → Reticulum → Enable Transport`) — phone becomes a relay
4. Try sending a message when phone is offline — does propagation node delivery work?

## Source reference

`sources/Sideband/`

Daemon mode (headless telemetry collector, no GUI):
```bash
pip install sbapp
sideband --daemon
```
