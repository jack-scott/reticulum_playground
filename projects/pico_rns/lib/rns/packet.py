# Reticulum wire packet construction and parsing.
#
# Wire format (Header Type 1 — single address, no IFAC):
#   [flags 1B] [hops 1B] [dest_hash 16B] [context 1B] [data ...]
#
# flags byte:
#   bit 7:   IFAC flag      (0 = open interface, no access code)
#   bit 6:   header type    (0 = HEADER_1, one address field)
#   bit 5:   context flag   (0 = FLAG_UNSET)
#   bit 4:   propagation    (0 = broadcast)
#   bits 3-2: dest type     (00 = single)
#   bits 1-0: packet type   (00=data, 01=announce, 10=link_req, 11=proof)

import os
import time
import uhashlib

PKT_DATA     = 0x00
PKT_ANNOUNCE = 0x01
PKT_LINKREQ  = 0x02
PKT_PROOF    = 0x03

CONTEXT_NONE = 0x00

_NAME_HASH = 10   # bytes


def _flags(pkt_type):
    # IFAC=0, HEADER_1=0, ctx_flag=0, broadcast=0, single=0
    return pkt_type & 0x03


def build_announce(dest_hash, identity, app_name, *aspects, app_data=None):
    """
    Build a Reticulum announce packet.

    announce data layout (inside the packet data field):
      pub_key(64) + name_hash(10) + random_hash(10) + signature(64) [+ app_data]

    The signature covers: dest_hash + pub_key + name_hash + random_hash [+ app_data]
    """
    name = app_name
    for a in aspects:
        name += "." + a
    name_hash   = uhashlib.sha256(name.encode()).digest()[:_NAME_HASH]
    random_hash = os.urandom(5) + (int(time.time()) & 0xFFFFFFFFFF).to_bytes(5, 'big')

    pub_key     = identity.get_public_key()   # 64 bytes
    signed_data = dest_hash + pub_key + name_hash + random_hash
    if app_data:
        signed_data += app_data

    signature     = identity.sign(signed_data)  # 64 bytes — slow on Pico
    announce_data = pub_key + name_hash + random_hash + signature
    if app_data:
        announce_data += app_data

    return bytes([_flags(PKT_ANNOUNCE), 0x00]) + dest_hash + bytes([CONTEXT_NONE]) + announce_data


def build_data(dest_hash, ciphertext_token):
    """Build a Reticulum data packet wrapping an already-encrypted token."""
    return bytes([_flags(PKT_DATA), 0x00]) + dest_hash + bytes([CONTEXT_NONE]) + ciphertext_token


def parse(raw):
    """
    Parse a raw UDP payload into a packet dict, or return None if malformed.

    Returned dict keys: flags, hops, header_type, transport_type, dest_type,
                        pkt_type, dest_hash (bytes), context, data (bytes)
    """
    if len(raw) < 20:   # 2 header + 16 dest + 1 context minimum
        return None

    flags = raw[0]
    hops  = raw[1]

    ifac_flag    = (flags >> 7) & 1
    header_type  = (flags >> 6) & 1
    context_flag = (flags >> 5) & 1
    transport    = (flags >> 4) & 1
    dest_type    = (flags >> 2) & 3
    pkt_type     = flags & 3

    offset = 2

    # Skip IFAC field if present (variable length — we don't use authenticated
    # interfaces in the thin client, so this packet isn't for us anyway).
    if ifac_flag:
        return None

    if header_type == 1:
        # HEADER_2: transport_id(16) precedes dest_hash(16)
        if len(raw) < offset + 32 + 1:
            return None
        offset += 16  # skip transport_id

    if len(raw) < offset + 16 + 1:
        return None

    dest_hash = bytes(raw[offset:offset + 16])
    offset   += 16
    context   = raw[offset]
    offset   += 1
    data      = bytes(raw[offset:])

    return {
        'flags':          flags,
        'hops':           hops,
        'header_type':    header_type,
        'transport_type': transport,
        'dest_type':      dest_type,
        'pkt_type':       pkt_type,
        'dest_hash':      dest_hash,
        'context':        context,
        'data':           data,
    }
