# Module 23 — Custom Interface Plugin

## Goal

Understand how RNS attaches to physical layers by writing your own interface plugin.
Every interface type (TCP, serial, LoRa, I2P) is just a class with the same two methods.

## What an interface must implement

```python
class MyInterface(RNS.Interfaces.Interface):
    # Required attributes
    name = "MyInterface"
    online = False
    bitrate = 1_000_000    # bits per second
    ifac_size = None       # IFAC auth frame size, None = disabled

    def __init__(self, owner, name, ...):
        super().__init__()
        self.owner = owner  # the RNS.Reticulum instance
        self.online = True

    def process_outbound(self, data):
        # Called by RNS when a packet needs to leave via this interface.
        # 'data' is raw bytes — apply your framing here, then transmit.
        pass

    def process_incoming(self, data):
        # Call THIS when data arrives on this interface.
        # RNS handles the rest — routing, decryption, delivery.
        self.owner.inbound(data, self)
```

That's it. RNS doesn't care what's below — copper, radio, light, sound, paper QR codes.

## Framing note

Most physical layers need framing (HDLC, KISS, etc.) to delimit packets. TCP streams need
HDLC or length-prefixing. RNS's built-in TCPClientInterface uses HDLC (flag byte `0x7E`,
escape byte `0x7D`). If you're writing a serial or audio modem interface, you need to handle
this in `process_outbound` and strip it before calling `process_incoming`.

## Source to study

`sources/Reticulum/Examples/ExampleInterface.py`

Also worth reading the built-in interfaces for real-world patterns:
- `sources/Reticulum/RNS/Interfaces/TCPInterface.py`
- `sources/Reticulum/RNS/Interfaces/SerialInterface.py`

## Exercises

1. Read ExampleInterface.py end to end — identify each lifecycle method
2. Write a `LoopbackInterface` that connects two in-process RNS instances directly (no TCP)
   — useful for fast unit tests without network overhead
3. Write a `FileInterface` that reads/writes packets to a directory of files
   (simulates a store-and-forward sneakernet)
4. Attach your interface to a real RNS instance — send an announce through it
