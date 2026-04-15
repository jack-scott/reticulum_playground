#!/usr/bin/env python3
"""
Module 06 — LXMF Messaging: receiver side

Starts an LXMF router, announces its address, and prints incoming messages.
Works with any LXMF sender — including Sideband on Android.

Usage: pixi run python experiments/06_lxmf/receive_messages.py
"""

import os
import sys
import time
import RNS
import LXMF

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "rns_config")
IDENTITY_PATH = os.path.join(os.path.dirname(__file__), "identity")
STORAGE_PATH = os.path.join(os.path.dirname(__file__), "lxmf_storage")


def on_message(message):
    source = RNS.prettyhexrep(message.source_hash)
    print(f"\n--- message received ---")
    print(f"  from    : {source}")
    print(f"  title   : {message.title_as_string()}")
    print(f"  content : {message.content_as_string()}")
    if message.fields:
        print(f"  fields  : {message.fields}")
    print()


def main():
    rns = RNS.Reticulum(CONFIG_PATH)

    if os.path.exists(IDENTITY_PATH):
        identity = RNS.Identity.from_file(IDENTITY_PATH)
        print("Loaded existing identity")
    else:
        identity = RNS.Identity()
        identity.to_file(IDENTITY_PATH)
        print("Generated new identity")

    router = LXMF.LXMRouter(storagepath=STORAGE_PATH)
    destination = router.register_delivery_identity(identity, display_name="RNS Playground")
    router.register_delivery_callback(on_message)

    address = RNS.prettyhexrep(destination.hash)
    print(f"LXMF address : {address}")
    print(f"Add this address to Sideband contacts, then send a message.")
    print(f"Ctrl-C to quit.\n")

    destination.announce()
    print("Announced. Waiting for messages...")

    while True:
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
