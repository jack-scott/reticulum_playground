# Module 22 — IP over RNS

## Goal

Create a virtual network interface that tunnels standard IP traffic over a Reticulum mesh.
Run SSH, HTTP, UDP — anything — through LoRa or WiFi without the application knowing.

## Two tools

### rns-tun-rs — minimal TUN device
~300 lines of Rust. Creates a Linux TUN interface. Server side assigns an IP, client connects to it.
Requires root (TUN device creation).

```bash
cd ../sources/rns-tun-rs
cargo build --release

# Terminal 1 (server)
sudo ./target/release/server -p 4242

# Terminal 2 (client)
sudo ./target/release/client -s 192.168.0.99:4242
```

### rns-vpn-rs — full P2P VPN
Multi-peer. CIDR subnet. Peers addressed by destination hash — no IP configuration needed upfront.
Generates X25519 + Ed25519 keys with `genkeys.sh`.

```bash
cd ../sources/rns-vpn-rs
cargo build --release

# Generate keypair
./genkeys.sh

# Edit Config.toml:
#   network = "10.20.0.0/16"
#   [[peers]]
#   destination = "<peer destination hash>"
#   address = "10.20.0.2"

sudo ./target/release/rns-vpn
```

Once running, reach peers at their configured IP:
```bash
ssh 10.20.0.2   # reaches peer over RNS, regardless of physical transport
```

## Key insight

Both tools sit at the network layer — the application (SSH, curl, etc.) sees a normal network
interface. All the Reticulum routing, encryption, and transport negotiation is invisible.

## Exercises

1. Run rns-tun-rs server+client, ping across the tunnel
2. SSH through the tunnel to the server machine
3. Set up rns-vpn-rs between two machines — confirm IP reachability
4. Swap the underlying RNS transport (TCP → serial → LoRa) — IP traffic continues unchanged

## Source references

`sources/rns-tun-rs/`
`sources/rns-vpn-rs/`
