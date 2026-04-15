# Reticulum thin-client node.
#
# Responsibilities:
#   - Maintain a UDP socket on port 4242
#   - Broadcast an announce on startup and every ANNOUNCE_INTERVAL seconds
#   - Parse incoming UDP packets
#   - Learn peer destination hashes from incoming announces
#   - Decrypt incoming data packets addressed to us
#   - Send encrypted data packets to known destinations

import socket
import time
import ubinascii

def _hex(b):
    return ubinascii.hexlify(b).decode()

from .packet import (
    build_announce, build_data, parse,
    PKT_DATA, PKT_ANNOUNCE,
)
from .identity import truncated_hash

UDP_PORT          = 4242
ANNOUNCE_INTERVAL = 300   # seconds between automatic re-announces


class Node:
    def __init__(self, identity, app_name, *aspects, app_data=None):
        self.identity  = identity
        self.app_name  = app_name
        self.aspects   = aspects
        self.app_data  = app_data
        self.dest_hash = identity.dest_hash(app_name, *aspects)

        # dest_hash (bytes) → 64-byte public key
        self.known = {}

        self._on_message  = None
        self._last_ann    = 0

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        bind_addr = socket.getaddrinfo('0.0.0.0', UDP_PORT)[0][-1]
        self._sock.bind(bind_addr)
        self._sock.settimeout(0.1)

        print("RNS: node ready, dest =", _hex(self.dest_hash))

    # --- callbacks ---

    def on_message(self, fn):
        """Register fn(plaintext_bytes) called when a data packet arrives for us."""
        self._on_message = fn
        return fn   # allow use as decorator

    # --- outgoing ---

    def announce(self):
        """Broadcast an announce so the router learns our path."""
        print("RNS: signing announce (this may take a moment)...")
        pkt = build_announce(
            self.dest_hash,
            self.identity,
            self.app_name,
            *self.aspects,
            app_data=self.app_data,
        )
        self._sock.sendto(pkt, ('255.255.255.255', UDP_PORT))
        self._last_ann = time.time()
        print("RNS: announced", _hex(self.dest_hash))

    def send(self, dest_hash, plaintext):
        """
        Send encrypted data to a known destination.
        dest_hash must be bytes (16 bytes).
        Returns True if sent, False if destination unknown.
        """
        if dest_hash not in self.known:
            print("RNS: unknown destination", _hex(dest_hash))
            return False
        token = self.identity.encrypt_for(self.known[dest_hash], plaintext)
        pkt   = build_data(dest_hash, token)
        self._sock.sendto(pkt, ('255.255.255.255', UDP_PORT))
        print("RNS: sent", len(plaintext), "bytes to", _hex(dest_hash))
        return True

    # --- main loop ---

    def tick(self):
        """
        Call this regularly (e.g. in a while-True loop).
        Handles auto-re-announce and one pending UDP packet.
        """
        if time.time() - self._last_ann > ANNOUNCE_INTERVAL:
            self.announce()

        try:
            raw, _ = self._sock.recvfrom(2048)
        except OSError:
            return

        pkt = parse(raw)
        if pkt is None:
            return

        if pkt['pkt_type'] == PKT_ANNOUNCE:
            self._handle_announce(pkt)
        elif pkt['pkt_type'] == PKT_DATA:
            self._handle_data(pkt)

    def run(self):
        """Block forever processing packets (convenience wrapper)."""
        self.announce()
        while True:
            self.tick()

    # --- incoming handlers ---

    def _handle_announce(self, pkt):
        data = pkt['data']
        # data layout: pub_key(64) + name_hash(10) + random_hash(10) + sig(64) [+ app_data]
        if len(data) < 64 + 10 + 10 + 64:
            return
        pub_key   = data[:64]
        dest_hash = pkt['dest_hash']

        # Don't re-learn our own announce
        if dest_hash == self.dest_hash:
            return

        self.known[dest_hash] = pub_key
        app_data_bytes = data[64 + 10 + 10 + 64:]
        app_data_str   = ""
        if app_data_bytes:
            try:
                app_data_str = " app_data=" + app_data_bytes.decode()
            except Exception:
                app_data_str = " app_data=<binary>"
        print("RNS: learned", _hex(dest_hash) + app_data_str)

    def _handle_data(self, pkt):
        if pkt['dest_hash'] != self.dest_hash:
            return
        try:
            plaintext = self.identity.decrypt(pkt['data'])
        except Exception as e:
            print("RNS: decrypt error:", e)
            return
        print("RNS: received", len(plaintext), "bytes")
        if self._on_message:
            self._on_message(plaintext)
