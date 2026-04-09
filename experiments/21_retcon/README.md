# Module 21 — RETCON: Event Mesh Deployment

## Goal

Build pre-configured Raspberry Pi SD images that auto-form a Reticulum mesh on boot.
Deploy them at an event or in an emergency — no configuration needed on site.

## Two modes

| Mode | What it does | Use case |
|---|---|---|
| Transport | Headless relay — no WiFi AP, just extends range | Roof/high-point nodes |
| Client | Creates WiFi AP + runs MeshChat at `retcon.local` | End-user access points |

Nodes auto-discover each other via 2.4 GHz WiFi. RNodes (LoRa) and Meshtastic devices
are auto-detected on USB boot.

## Build a RETCON image

Requires: Debian 12+, 8 GB RAM, arm64 or qemu

```bash
cd ../sources/RETCON

# 1. Install build prereqs
./install_prereqs.sh

# 2. Choose a profile and customise it
cp retcon_profiles/default.config my_event.config
# Edit: node name, WiFi SSID/password, transport vs client mode, LoRa freq

# 3. Build (takes ~15 min)
./build_retcon.sh my_event.config

# 4. Flash to SD card
dd if=retcon_output.img of=/dev/sdX bs=4M status=progress
# or use Raspberry Pi Imager
```

## Administration via LXMF

Once deployed, each node has an LXMF identity. Send admin messages to it:
- Change mode (transport ↔ client)
- Update WiFi AP password
- Reboot

## Profiles to study

| Profile | What it shows |
|---|---|
| `default.config` | Minimal reference — understand all fields |
| `dc33.config` | DEF CON 33 real-world deployment |
| `chimesh.config` | Community mesh example |

Source: `sources/RETCON/retcon_profiles/`

## Exercises

1. Read `default.config` — identify every field, understand defaults
2. Build a transport-mode image and a client-mode image
3. Boot both Pis, confirm they find each other (`rnstatus` on one should show the other's interface)
4. Connect a phone to the client node's WiFi AP, open `retcon.local`
