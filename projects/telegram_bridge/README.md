# Project F — Telegram ↔ LXMF Bridge

Bridge your LXMF mesh contacts into Telegram. Contacts who won't run Reticulum can still
reach you on the mesh — and you can reply from either side.

## Architecture

```
[Telegram contact]           [Bridge node]              [Mesh contacts]
       │                   lxmf-cli + telegram_bridge.py      │
       │──── Telegram ────▶│                                   │
       │                   │──── LXMF ───────────────────────▶│
       │                   │◀─── LXMF ────────────────────────│
       │◀─── Telegram ─────│
```

The bridge runs as a persistent lxmf-cli instance with the plugin active. It needs to be
online to relay messages — it won't store-and-forward to Telegram.

## Setup

### Telegram bot
1. Message @BotFather on Telegram, create a bot, get the API token
2. Add the bot to the Telegram chats you want to bridge

### Bridge node
```bash
# Copy plugin
cp ../sources/lxmf-cli/plugins/telegram_bridge.py lxmf_client_storage/plugins/

# Edit telegram_bridge.py:
#   TELEGRAM_TOKEN = "your-bot-token"
#   BRIDGE_CHAT_ID = 12345678  # Telegram chat ID to bridge

# Run
pixi run python ../sources/lxmf-cli/lxmf-cli.py
```

## What to build

- `projects/telegram_bridge/config.py` — externalise token and chat mapping to a config file
- `projects/telegram_bridge/run_bridge.sh` — systemd-compatible startup script
- Contact mapping: LXMF destination hash ↔ Telegram user ID (so replies route correctly)

## Extension ideas

- Two-way contact sync: new LXMF contacts automatically create Telegram threads
- Media forwarding: pass image attachments both ways (Sideband → Telegram, Telegram → LXMF)
- Status indicator: post to a Telegram channel when mesh nodes come online/offline

## Source reference

`sources/lxmf-cli/plugins/telegram_bridge.py`

See also: `sources/lxmf-cli/plugins/` for similar bridge patterns (rtcom_bridge for real-time communications).
