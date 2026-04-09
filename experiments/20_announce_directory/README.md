# Module 20 — Network Analysis & Announce Directory

## Goal

Collect and analyse the announce traffic you hear on the mesh. Build a picture of what nodes
exist, what apps they run, and how the network topology looks.

## Tools

### rns_announce_view — real-time console
Prints every announce as it arrives: hash, app name, timestamp, hop count.

```bash
pixi run python ../sources/RNS-Tools/rns_announce_view/rns_announce_view.py
```

### rns_announce_directory — persistent database
Stores all heard announces in SQLite (or Postgres). Queryable. Can serve a NomadNet browse page.

```bash
pixi run python ../sources/RNS-Tools/rns_announce_directory/rns_announce_directory.py
```

Database columns: `destination_hash`, `app_name`, `aspect`, `announce_time`, `app_data`, `rssi`, `hop_count`

Example queries:
```sql
-- Most active apps on the mesh
SELECT app_name, aspect, COUNT(*) as count
FROM announces
GROUP BY app_name, aspect
ORDER BY count DESC;

-- Nodes heard in the last hour
SELECT destination_hash, app_name, app_data
FROM announces
WHERE announce_time > strftime('%s','now') - 3600;
```

### rns_announce_test — automated announce tester
Sends announces at configurable intervals and logs which nodes respond, at what RSSI, and
from how many hops. Good for verifying network coverage.

```bash
pixi run python ../sources/RNS-Tools/rns_announce_test/rns_announce_test.py
```

## Exercises

1. Run rns_announce_view while also running the announce experiment (Module 01) — watch your own announces appear
2. Run rns_announce_directory for 10 minutes on a mesh with other nodes
3. Query: how many unique destination hashes did you hear? How many per app?
4. Run rns_announce_test — measure how many of your announces are echoed back by other nodes

## Source reference

`sources/RNS-Tools/rns_announce_directory/`
`sources/RNS-Tools/rns_announce_view/`
`sources/RNS-Tools/rns_announce_test/`
