# Module 01 — Hello RNS: Announces

## Goal

Send an announce and receive it. Understand what an announce is, how the aspect filter works, and what app_data can carry.

## Run It

Open two terminals:

**Terminal 1 — listener:**
```bash
pixi run python experiments/01_hello_rns/listener.py
```

**Terminal 2 — announcer:**
```bash
pixi run python experiments/01_hello_rns/announcer.py
```

Press Enter in the announcer terminal. The listener should print the received announce.

## What's Happening

### Destination naming

A destination's address is derived from:
```
hash(identity.public_key + "playground" + "hello")
```

The app name + aspects act as a namespace. Clients can filter for specific app/service combinations using `aspect_filter`.

### Aspect filter

`aspect_filter = "playground.hello"` means the handler only receives announces for that exact path. Set it to `None` to receive all announces on the network.

Try changing the filter to `"playground"` — does it still receive announces? (It won't — filters must match exactly, no wildcards.)

### app_data

The announce can carry up to ~2KB of arbitrary bytes. This is the only mechanism for carrying data in an announce — commonly used for display names, service descriptions, or version info.

## Experiments

1. Run both scripts. Send a few announces and observe the output.
2. Change `aspect_filter` to `None` in `listener.py` — you'll now see ALL announces on the network (try running other RNS apps nearby).
3. Encode something more interesting in `app_data` — a JSON dict with hostname and version.
4. What happens if you restart `announcer.py`? Does the destination hash change? Why?
