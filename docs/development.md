# Development

## Repository Layout

```text
Iyrin/
├── app.py
├── config.py
├── world.py
├── sources.py
├── history.py
├── tools.py
├── pipelines.py
├── embedders.py
├── processors.py
├── loaders.py
├── fetchers.py
├── generators.py
├── maps.py
├── geocode.py
├── places.py
├── distances.py
├── timezones.py
├── staticmaps.py
├── caches.py
├── excel.py
├── stores/
├── resources/
├── docs/
└── mkdocs.yml
```

## Documentation Commands

```powershell
mkdocs serve
```

```powershell
mkdocs build --strict
```

## Conventions

- Material for MkDocs with the slate scheme.
- Dark-blue theme overrides in `docs/assets/css/iyrin.css`.
- Progressive enhancements in `docs/assets/js/iyrin.js`.
- Tables for finite capability and configuration matrices.
- mkdocstrings for selected import-safe modules.
- Implemented repository behavior takes precedence over planned functionality.
