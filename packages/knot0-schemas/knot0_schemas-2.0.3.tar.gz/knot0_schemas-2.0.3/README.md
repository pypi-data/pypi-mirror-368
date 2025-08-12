knot0-schemas (Python)

Simple helpers to load Knot0 v2 JSON Schemas from the monorepo and validate manifests.

Usage
```bash
# Build schemas first
node knot0-src/schemas-v2/scripts/build.mjs
```

```python
from knot0_schemas import validator

ok, errors = validator.validate('Component', {
    'kind': 'Component',
    'schema_version': '2.0',
    'metadata': {'name': 'hello'},
    'contract': {},
    'body': {'execution': {'runner': 'python', 'run': 'print(1)'}}
})
print(ok, errors)
```

