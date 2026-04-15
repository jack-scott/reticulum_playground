# Listen for Reticulum announcements on the local network.
# Runs under MicroPython unix port — no WiFi setup needed, laptop is already on the network.
#
#   pixi run listen

import sys
import socket
import ubinascii

sys.path.insert(0, 'lib')

from rns.identity import Identity
from rns.packet import parse, PKT_ANNOUNCE, PKT_DATA

UDP_PORT = 4242

def _hex(b):
    return ubinascii.hexlify(b).decode()


identity = Identity()
print("RNS: our dest_hash =", _hex(identity.hash))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
bind_addr = socket.getaddrinfo('0.0.0.0', UDP_PORT)[0][-1]
sock.bind(bind_addr)
sock.settimeout(1.0)

print("Listening on UDP :4242 — press Ctrl+C to stop\n")

while True:
    try:
        raw, addr = sock.recvfrom(2048)
    except OSError:
        continue

    pkt = parse(raw)
    if pkt is None:
        print("RAW (%d bytes from %s): %s" % (len(raw), addr[0], _hex(raw[:32])))
        continue

    if pkt['pkt_type'] == PKT_ANNOUNCE:
        data = pkt['data']
        dest = _hex(pkt['dest_hash'])
        if len(data) >= 64 + 10 + 10 + 64:
            app_data = data[64 + 10 + 10 + 64:]
            app_str = ""
            if app_data:
                try:
                    app_str = "  app_data=" + app_data.decode()
                except Exception:
                    app_str = "  app_data=" + _hex(app_data)
            print("ANNOUNCE dest=%s from=%s%s" % (dest, addr[0], app_str))
        else:
            print("ANNOUNCE dest=%s from=%s (short data: %d bytes)" % (dest, addr[0], len(data)))

    elif pkt['pkt_type'] == PKT_DATA:
        dest = _hex(pkt['dest_hash'])
        ours = pkt['dest_hash'] == identity.hash
        if ours:
            try:
                plaintext = identity.decrypt(pkt['data'])
                try:
                    print("DATA (for us) from=%s: %s" % (addr[0], plaintext.decode()))
                except Exception:
                    print("DATA (for us) from=%s: %s" % (addr[0], _hex(plaintext)))
            except Exception as e:
                print("DATA (for us, decrypt failed) from=%s: %s" % (addr[0], e))
        else:
            print("DATA dest=%s from=%s (%d bytes)" % (dest, addr[0], len(pkt['data'])))

    else:
        print("PKT type=%d dest=%s from=%s" % (pkt['pkt_type'], _hex(pkt['dest_hash']), addr[0]))
