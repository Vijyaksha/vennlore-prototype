# @repo/contracts

Single source of truth for the data contracts shared between the Python matching
engine and the TypeScript web app: `Talk`, `Recommendation`, and `Run`.

The zod schemas in `src/` are the source. `schema/*.json` (JSON Schema, draft
2020-12) is **generated** from them and must never be hand-edited — regenerate
with `npm run emit --workspace=@repo/contracts` after any schema change. The
`schemas.test.ts` drift test fails the build if the committed JSON Schema no
longer matches what the zod source would emit.

## Fixtures

`fixtures/valid/<kind>.json` are golden valid rows for `talk`, `recommendation`,
and `run`.

`fixtures/invalid/<kind>-<reason>.json` are golden invalid rows. The kind is the
filename up to the first hyphen (e.g. `talk-missing-title.json` → `talk`). Each
invalid fixture differs from its valid counterpart in exactly one stated way,
and the test asserts the parse fails for that specific reason (the failing
field path, or the offending key for an unrecognized-key rejection) — not just
that it fails.

## Consuming the JSON Schema from Python

```python
import json
from jsonschema.validators import Draft202012Validator

schema = json.load(open("schema/talk.schema.json"))
Draft202012Validator(schema).validate(row)
```

Note: Python's `re` module treats `$` as matching immediately before a trailing
`\n`, so a datetime string with a trailing newline can pass a Python-side
pattern check (e.g. via `jsonschema`'s `format` or a hand-rolled regex) even
though the same string fails zod's `z.iso.datetime()` validation on the
TypeScript side.
