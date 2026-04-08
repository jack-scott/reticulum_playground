# Module 07 — Resources & File Transfer

## Goal

Transfer files and large data over an RNS link using the Resource mechanism. Measure throughput.

## What to Build

- `resource_server.py` — accepts incoming links, accepts resources, saves to disk
- `resource_client.py` — establishes a link, sends a file as a Resource

## Key Resource API

```python
# Send a file
with open("myfile.bin", "rb") as f:
    data = f.read()

resource = RNS.Resource(data, link, callback=on_sent, progress_callback=on_progress)

# Receive
def on_resource(resource):
    resource.set_callback(on_received)
    return True  # accept it

link.set_resource_callback(on_resource)
link.set_resource_strategy(RNS.Link.ACCEPT_ALL)

def on_received(resource):
    with open("received_file.bin", "wb") as f:
        f.write(resource.data)
    print(f"Received {len(resource.data)} bytes")
```

## Try `rncp` (built-in file transfer)

```bash
# On receiving machine — note identity hash
pixi run rnsd  # must be running

# On sending machine
pixi run rncp --to <destination_hash> ./somefile.txt
```

## Reference

`../reticulum_sources/Reticulum/Examples/Resource.py`
`../reticulum_sources/Reticulum/Examples/Filetransfer.py`

## Throughput Notes

Over loopback TCP/UDP on the same machine, you should see hundreds of KB/s.
Over LoRa at SF8 125kHz (~3kbps), a 1KB file takes ~3 seconds.
Resources compress data automatically — text compresses well.
