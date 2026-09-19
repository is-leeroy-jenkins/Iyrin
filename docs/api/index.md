# API Reference

Iyrin modules are organized around geospatial services, acquisition, processing, persistence, and Live World operations.

| Group | Modules |
|---|---|
| Geospatial | `maps`, `geocode`, `places`, `distances`, `timezones`, `staticmaps`, `excel` |
| AI / Processing | `pipelines`, `embedders`, `stores.vector` |
| Live World | `world`, `sources`, `history`, `tools` |
| Supporting | `caches`, `rates`, `exceptions`, `config` |

Selected modules use mkdocstrings. Large acquisition/parser modules are described in the architecture and guides because importing them can initialize optional runtime dependencies.
