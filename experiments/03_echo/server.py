#!/usr/bin/env python3
"""
Module 03 — Packet Echo Server

Receives packets from clients and automatically sends proofs back.
Prints RSSI and SNR if available (works when connected to a shared rnsd instance
or when receiving from a radio interface).

Usage: pixi run python experiments/03_echo/server.py
"""

import os
import sys
import time
import RNS

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "rns_config")
APP_NAME = "playground"

reticulum = None


def server():
    global reticulum
    reticulum = RNS.Reticulum(CONFIG_PATH)

    identity = RNS.Identity()
    destination = RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        "echo",
        "request",
    )

    # PROVE_ALL means RNS auto-generates a proof for every received packet,
    # sending it back to the originating client
    destination.set_proof_strategy(RNS.Destination.PROVE_ALL)
    destination.set_packet_callback(on_packet)

    print(f"Echo server running")
    print(f"  Destination : {RNS.prettyhexrep(destination.hash)}")
    print()
    print("Press Enter to re-announce. Ctrl-C to quit.")
    print()

    while True:
        input()
        destination.announce()
        print(f"Announced {RNS.prettyhexrep(destination.hash)}")


def on_packet(message, packet):
    stats = build_signal_stats(packet)
    print(f"Received echo request{stats} — proof sent automatically")


def build_signal_stats(packet):
    stats = ""
    if reticulum and reticulum.is_connected_to_shared_instance:
        rssi = reticulum.get_packet_rssi(packet.packet_hash)
        snr = reticulum.get_packet_snr(packet.packet_hash)
        if rssi is not None:
            stats += f" [RSSI {rssi} dBm]"
        if snr is not None:
            stats += f" [SNR {snr} dB]"
    else:
        if packet.rssi is not None:
            stats += f" [RSSI {packet.rssi} dBm]"
        if packet.snr is not None:
            stats += f" [SNR {packet.snr} dB]"
    return stats


if __name__ == "__main__":
    try:
        server()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
