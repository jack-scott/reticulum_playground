# Module 18 — lxmf-cli Bots & Automation

## Goal

Use lxmf-cli's hot-reload plugin system to build bots and automations. Progress from simple
echo bots to reverse SSH over the mesh.

## Install & run

```bash
# lxmf-cli uses the same rns/lxmf deps as this project
pixi run python ../sources/lxmf-cli/lxmf-cli.py
```

Identity and message history stored in `lxmf_client_storage/`.
Plugins go in `lxmf_client_storage/plugins/` — they hot-reload on file change.

## Plugin interface

```python
class MyPlugin:
    name = "my_plugin"

    def __init__(self, lxmf_client):
        self.client = lxmf_client

    def on_message(self, message):
        # Called for every received message
        sender_hash = message.source_hash.hex()
        content = message.content.decode("utf-8")
        # Reply:
        # self.client.send_message(sender_hash, "hello back")

    def handle_command(self, command, args, message):
        # Called when message starts with /<command>
        pass
```

## Progression

### Step 1 — echo_bot
Copy `echo_bot.py` to `lxmf_client_storage/plugins/`. Send yourself a message — it bounces back.

### Step 2 — keyword_alert
Configure `keyword_alert.py` with words to watch. It fires a notification (or prints) when keywords arrive.

### Step 3 — away_bot
Set a custom away message. Anyone who messages you gets an auto-reply while you're AFK.

### Step 4 — rssh (reverse SSH)
```bash
# On the remote machine (behind NAT, no port forwarding needed)
cp sources/lxmf-cli/plugins/rssh.py lxmf_client_storage/plugins/

# From anywhere on the mesh:
/rssh <remote_machine_hash>
# → opens a reverse SSH tunnel back to you
```

### Step 5 — telegram_bridge
Bridge your LXMF contacts into Telegram. Requires a Telegram Bot API token.

```bash
cp sources/lxmf-cli/plugins/telegram_bridge.py lxmf_client_storage/plugins/
# Edit the plugin — add your bot token
```

## Source reference

`sources/lxmf-cli/plugins/` — 30+ plugins including echo_bot, away_bot, keyword_alert,
pgp, rssh, telegram_bridge, rangetest_client/server, groupchat, scheduler, sys_info
