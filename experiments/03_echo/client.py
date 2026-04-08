#!/usr/bin/env python3
"""
Module 03 — Packet Echo Client

Sends packets to the echo server and measures round-trip time.

Usage: pixi run python experiments/03_echo/client.py <destination_hash>

Get the destination hash from the server output.
"""

import os
import sys
import time
import RNS

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "rns_config")
APP_NAME = "playground"

reticulum = None


def client(destination_hexhash, timeout=5.0):
    global reticulum

    dest_len = (RNS.Reticulum.TRUNCATED_HASHLENGTH // 8) * 2
    if len(destination_hexhash) != dest_len:
        print(f"Error: destination hash must be {dest_len} hex characters")
        sys.exit(1)

    destination_hash = bytes.fromhex(destination_hexhash)

    reticulum = RNS.Reticulum(CONFIG_PATH)
    if RNS.loglevel < RNS.LOG_INFO:
        RNS.loglevel = RNS.LOG_INFO

    print(f"Echo client ready")
    print(f"  Target : {destination_hexhash}")
    print()
    print("Press Enter to send an echo. Ctrl-C to quit.")
    print()

    while True:
        input()
        send_echo(destination_hash, timeout)


def send_echo(destination_hash, timeout):
    if not RNS.Transport.has_path(destination_hash):
        print("No path known — requesting path... (wait for server to announce)")
        RNS.Transport.request_path(destination_hash)
        return

    server_identity = RNS.Identity.recall(destination_hash)
    request_destination = RNS.Destination(
        server_identity,
        RNS.Destination.OUT,
        RNS.Destination.SINGLE,
        APP_NAME,
        "echo",
        "request",
    )

    packet = RNS.Packet(request_destination, RNS.Identity.get_random_hash())
    receipt = packet.send()

    receipt.set_timeout(timeout)
    receipt.set_delivery_callback(on_delivered)
    receipt.set_timeout_callback(on_timeout)

    print(f"Sent echo to {RNS.prettyhexrep(request_destination.hash)}")


def on_delivered(receipt):
    global reticulum
    if receipt.status != RNS.PacketReceipt.DELIVERED:
        return

    rtt = receipt.get_rtt()
    rtt_str = f"{rtt * 1000:.1f} ms" if rtt < 1 else f"{rtt:.3f} s"

    stats = ""
    if reticulum and reticulum.is_connected_to_shared_instance:
        if receipt.proof_packet:
            rssi = reticulum.get_packet_rssi(receipt.proof_packet.packet_hash)
            snr = reticulum.get_packet_snr(receipt.proof_packet.packet_hash)
            if rssi is not None:
                stats += f" [RSSI {rssi} dBm]"
            if snr is not None:
                stats += f" [SNR {snr} dB]"
    else:
        if receipt.proof_packet:
            if receipt.proof_packet.rssi is not None:
                stats += f" [RSSI {receipt.proof_packet.rssi} dBm]"
            if receipt.proof_packet.snr is not None:
                stats += f" [SNR {receipt.proof_packet.snr} dB]"

    print(f"Reply received — RTT: {rtt_str}{stats}")


def on_timeout(receipt):
    print(f"Packet {RNS.prettyhexrep(receipt.hash)} timed out")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client.py <destination_hash>")
        print("       Get the hash from the server terminal output.")
        sys.exit(1)

    try:
        client(sys.argv[1])
    except KeyboardInterrupt:
        print()
        sys.exit(0)
