import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path.cwd() / 'knot0-src' / 'schemas-v2' / 'json'

def load_schema(kind: str) -> dict:
    path = ROOT / f'{kind}.json'
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)

_SCHEMA_CACHE = {}
_VALIDATORS = {}

def _get_validator(kind: str):
    if kind not in _VALIDATORS:
        schema = load_schema(kind)
        _SCHEMA_CACHE[schema.get('$id', kind)] = schema
        _VALIDATORS[kind] = Draft202012Validator(schema)
    return _VALIDATORS[kind]

def validate(kind: str, data: dict):
    v = _get_validator(kind)
    errors = sorted(v.iter_errors(data), key=lambda e: e.path)
    return (len(errors) == 0, [e.message for e in errors])

