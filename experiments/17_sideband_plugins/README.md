# Module 17 — Sideband Plugin Development

## Goal

Write custom plugins for Sideband — add your own sensors, commands, and services.

## Plugin types

| Type | File pattern | Triggered by | Returns |
|---|---|---|---|
| Telemetry | `class TelemetryPlugin` | Periodic timer or on-demand | Dict of sensor values |
| Command | `class CommandPlugin` | Incoming LXMF message matching prefix | LXMF reply string |
| Service | `class ServicePlugin` | Sideband lifecycle events | — |

## Minimal telemetry plugin

```python
class TelemetryPlugin:
    plugin_type = "telemetry"
    plugin_name = "cpu_temp"

    def start(self):
        pass

    def stop(self):
        pass

    def update_telemetry(self, telemetry):
        import subprocess
        raw = subprocess.check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"])
        temp_c = int(raw.strip()) / 1000.0
        telemetry.add_sensor("cpu_temp_c", temp_c)
```

Place plugin files in Sideband's plugin directory (shown in Settings → Plugins).

## Reference plugins to study

| Plugin | What it demonstrates |
|---|---|
| `bme280_telemetry.py` | I2C sensor, periodic reading |
| `basic.py` | Minimal command plugin template |
| `service.py` | Minimal service plugin template |
| `gpsd_location.py` | GPS via system daemon |
| `lxmd_telemetry.py` | Reading stats from another process |

Source: `sources/Sideband/docs/example_plugins/`

## Exercises

1. Write a CPU/memory telemetry plugin
2. Write a command plugin that responds to `/ping` with system uptime
3. Write a service plugin that logs all received messages to a file
4. View telemetry on another device running Sideband
