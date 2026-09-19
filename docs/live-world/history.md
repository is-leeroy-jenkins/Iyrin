# Historical Replay

Historical Replay persists normalized Live World observations to SQLite.

## Persistence

- Explicit persistence enablement.
- Configurable retention.
- Per-source row limits.
- No new snapshot for partial/provider-failed refreshes.

## Deduplication

Unchanged state is deduplicated for Earthquakes, Fires, Infrastructure, Cameras, and Map Features. Moving Aircraft, Military Aircraft, Satellites, and Vessels continue to persist so trajectories can be reconstructed.

## Replay

Replay supports configurable windows, entity filters, record limits, and selected snapshots. Bounded queries select the newest records through the selected snapshot and return the bounded result chronologically.
