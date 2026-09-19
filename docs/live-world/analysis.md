# Spatial Analysis & Geofencing

## Cross-Layer Analysis

Cross-Layer Analysis operates on normalized entity state without re-fetching providers when only analysis parameters change.

### Inputs

- Current location, custom point, or loaded entity.
- Radius.
- Entity types.
- Result limit.

### Outputs

- Great-circle distance.
- Initial bearing.
- Nearest entities.
- Nearest entity by type.
- Radius-map highlighting.

## Geofencing

Geofencing evaluates entities against a circular boundary.

- Configurable origin and radius.
- Entity-type filtering.
- Current membership.
- Entry/exit transition history.
- Baseline initialization without false entries.
- Bounded event history.
