# Module 03 — Packet Echo

## Goal

Send a packet to a server and get a proof back. Measure round-trip time. See RSSI/SNR from radio interfaces.

## Run It

**Terminal 1 — server:**
```bash
pixi run python experiments/03_echo/server.py
```
Copy the destination hash from the output.

**Terminal 2 — client:**
```bash
pixi run python experiments/03_echo/client.py <destination_hash>
```

Press Enter in the client terminal to send an echo. You'll see the RTT printed.

## What's Happening

### Path lookup

Before the client can send, it needs to know the path. The server announces itself — once that announce arrives, `RNS.Transport.has_path()` returns True and `RNS.Identity.recall()` returns the server's public key.

If no path is known yet, the client requests one (`request_path`) and waits for the server to announce.

### Packet proofs

`destination.set_proof_strategy(RNS.Destination.PROVE_ALL)` means RNS automatically sends a proof packet back to the sender for every received packet. The proof is an Ed25519 signature over the packet hash — it's unforgeable, so the client knows the server genuinely received it.

### RSSI / SNR

Signal stats only appear when receiving from a radio interface (RNode LoRa, or a shared `rnsd` instance that bridges radio). Over loopback TCP/UDP, these will be None.

## Experiments

1. Run both scripts and confirm echo/RTT works.
2. Add a `--timeout` argument to `client.py` and test what happens when the server is stopped.
3. Start the server, stop it, then try to send from the client — what does the client print?
4. Open a third terminal and run another server — can you have two echo servers running simultaneously with different destination hashes?
