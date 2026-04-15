# Reticulum thin-client hello world for Pico 2W.
#
# What this does:
#   1. Connects to WiFi
#   2. Loads (or generates) a persistent identity from flash
#   3. Announces itself on the local network (the T-Beam router picks this up
#      and propagates the path over LoRa to the rest of the network)
#   4. Listens for incoming messages and prints them
#   5. Every 30s, sends "Hello from Pico!" to every known destination
#
# Drop the lib/ directory onto the Pico filesystem alongside this file.

import network
import time
import sys
import ubinascii

WIFI_SSID     = "your_ssid"
WIFI_PASSWORD = "your_password"

APP_NAME = "pico"
ASPECT   = "hello"

IDENTITY_PATH = "/rns_identity.key"
HELLO_INTERVAL = 30   # seconds between outgoing hello messages


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        print("WiFi: already connected", wlan.ifconfig())
        return True
    print("WiFi: connecting to", WIFI_SSID)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(30):
        if wlan.isconnected():
            print("WiFi: connected", wlan.ifconfig())
            return True
        time.sleep(1)
    print("WiFi: connection failed")
    return False


def main():
    if not connect_wifi():
        sys.exit(1)

    # Import here so crypto modules only load after WiFi is up
    from rns import Identity, Node

    identity = Identity.load_or_create(IDENTITY_PATH)
    node     = Node(identity, APP_NAME, ASPECT, app_data=b"pico-hello-world")

    @node.on_message
    def on_message(plaintext):
        try:
            print("MSG:", plaintext.decode())
        except Exception:
            print("MSG (binary):", ubinascii.hexlify(plaintext).decode())

    node.announce()

    last_hello = 0
    while True:
        node.tick()

        now = time.time()
        if now - last_hello > HELLO_INTERVAL and node.known:
            for dest_hash in list(node.known):
                node.send(dest_hash, b"Hello from Pico!")
            last_hello = now


main()
