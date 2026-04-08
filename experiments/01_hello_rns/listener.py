#!/usr/bin/env python3
"""
Module 01 — Hello RNS: Announces (listener side)

Listens for announces from playground.hello destinations.
Run this alongside announcer.py in another terminal.

Usage: pixi run python experiments/01_hello_rns/listener.py
"""

import os
import sys
import time
import RNS

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "rns_config")
APP_NAME = "playground"


class HelloAnnounceHandler:
    # Only receive announces matching this aspect
    aspect_filter = f"{APP_NAME}.hello"

    def received_announce(self, destination_hash, announced_identity, app_data):
        hash_str = RNS.prettyhexrep(destination_hash)
        print(f"Heard announce from {hash_str}")

        if app_data:
            print(f"  app_data : {app_data.decode('utf-8')}")

        # The identity's public key is now known — we could recall it later
        print(f"  identity : {RNS.prettyhexrep(announced_identity.hash)}")
        print()


def main():
    rns = RNS.Reticulum(CONFIG_PATH)

    handler = HelloAnnounceHandler()
    RNS.Transport.register_announce_handler(handler)

    print(f"Listening for announces on '{HelloAnnounceHandler.aspect_filter}'")
    print("Start announcer.py in another terminal. Ctrl-C to quit.")
    print()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
