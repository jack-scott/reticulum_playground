# Project A — Home Assistant Integration

## Goal

Build a sensor telemetry + command/control system using LXMF over Reticulum.

## Architecture

```
Sensor Node (Pi Zero / ESP32)
  - Reads sensors (temp, humidity, etc.)
  - Sends LXMF messages with Fields dict to Collector
  - Responds to LXMF command messages

Collector Node (home server / Pi)
  - Receives telemetry LXMF messages
  - Stores to SQLite
  - Serves data via REST API or NomadNet page
  - Can send command messages to sensor nodes

(Optional) Home Assistant Bridge
  - Polls Collector REST API
  - Or: HA webhook triggered by Collector
```

## LXMF Telemetry Pattern

```python
# Telemetry message using Fields dict
msg = LXMF.LXMessage(
    collector_dest,
    my_source,
    "",   # empty content
    fields={
        "type": "telemetry",
        "sensor": "bme280",
        "temp_c": 22.4,
        "humidity_pct": 58.2,
        "pressure_hpa": 1013.1,
        "timestamp": time.time(),
        "node_id": "garden_shed"
    }
)
```

## Command/Control Pattern

```python
# Command message
msg = LXMF.LXMessage(
    sensor_node_dest,
    my_source,
    "",
    fields={
        "type": "command",
        "cmd": "relay_on",
        "relay_id": 1
    }
)
```

## Files to Build

- `sensor_node.py` — reads sensors, sends LXMF telemetry, handles commands
- `collector.py` — receives telemetry, stores to SQLite, exposes REST API
- `tools/read_serial.py` — helper for reading sensor data from serial

## Reference

Sideband's telemetry plugin system:
`../reticulum_sources/Sideband/docs/example_plugins/bme280_telemetry.py`
`../reticulum_sources/Sideband/docs/example_plugins/telemetry.py`
