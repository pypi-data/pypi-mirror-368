knot0-types (Python)

Prebuilt Pydantic models generated from the monorepo JSON Schemas.

Note: The generator writes modules under `knot0-src/packages-v2/types-py/knot0_types_v2/`.
You can import models directly after running the generator.

Build
```bash
node knot0-src/schemas-v2/scripts/build.mjs
python3 knot0-src/scripts/generate-pydantic-models.py
```

