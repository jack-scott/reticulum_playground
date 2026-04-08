# Module 08 — Interface Configuration & Transports

## Goal

Configure different interface types. Understand client vs transport mode. Inspect routing.

## Config Files in This Directory

| File | What it sets up |
|---|---|
| `wifi_auto.config` | AutoInterface (WiFi LAN — zero config) |
| `tcp_server.config` | TCP server on port 4242 |
| `tcp_client.config` | TCP client connecting to a server |
| `transport_node.config` | Transport mode + AutoInterface |
| `dual_interface.config` | AutoInterface + TCP client simultaneously |

## Usage

```bash
# Run rnsd with a specific config
pixi run rnsd --config experiments/08_transports/tcp_server.config -v

# Check what interfaces are up
pixi run rnstatus --config experiments/08_transports/tcp_server.config

# See routing table
pixi run python -m RNS.Tools.rnpath --config experiments/08_transports/tcp_server.config -t
```

## Two-Machine TCP Test

**Machine A:**
```bash
pixi run rnsd --config experiments/08_transports/tcp_server.config -v
```

**Machine B** (edit `tcp_client.config` to point at Machine A's IP):
```bash
pixi run rnsd --config experiments/08_transports/tcp_client.config -v
```

Then run announcer.py on A and listener.py on B — they should find each other.

## Transport Mode

Setting `enable_transport = yes` turns this node into a router that forwards packets for others. Test it:

1. Run three nodes: A (transport), B, C
2. B and C connect to A (but not to each other)
3. Can B reach C? With transport mode on A: yes. Without: no.

## Interface Modes

For `AutoInterface` and `TCPServerInterface`:

| Mode | What it means |
|---|---|
| `full` | Send and receive everything (default) |
| `access_point` | Announce to all interfaces, but don't forward between them |
| `roaming` | Don't send announces to other interfaces |
| `boundary` | Full transport but don't propagate beyond this interface |
| `gateway` | Special routing for gatewaying between networks |

## Config Templates

See the `.config` files in this directory for complete examples with comments.
