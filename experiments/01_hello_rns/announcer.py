#!/usr/bin/env python3
"""
Module 01 — Hello RNS: Announces (sender side)

Creates a destination and announces it on the network.
Run this alongside listener.py in a second terminal.

Usage: pixi run python experiments/01_hello_rns/announcer.py
"""

import os
import sys
import time
import RNS

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "rns_config")
APP_NAME = "playground"


def main():
    rns = RNS.Reticulum(CONFIG_PATH)

    identity = RNS.Identity()
    print(f"My identity hash : {RNS.prettyhexrep(identity.hash)}")

    destination = RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        "hello",
    )

    print(f"My destination   : {RNS.prettyhexrep(destination.hash)}")
    print()
    print("Press Enter to announce. Ctrl-C to quit.")

    count = 0
    while True:
        input()
        count += 1
        app_data = f"announce #{count}".encode("utf-8")
        destination.announce(app_data=app_data)
        print(f"Sent announce #{count} from {RNS.prettyhexrep(destination.hash)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
