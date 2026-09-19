# Agent Tools

`tools.py` exposes provider-neutral functions over normalized Live World state.

## Operations

- Operational status.
- Entity listing.
- Entity search.
- Nearest-entity queries.
- Great-circle distance.
- Bearing.
- Provider status and stale/error diagnostics.
- Cross-Layer Analysis status.
- Geofence status.
- Tracking status.
- Historical Replay status.
- Bounded persisted-history retrieval.

The functions return JSON-serializable dictionaries and lists and are intentionally decoupled from a specific agent SDK.
