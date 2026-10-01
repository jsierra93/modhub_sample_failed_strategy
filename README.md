# modhub_sample_failed_strategy

A FastAPI service whose Pydantic v1 models cannot be migrated to v2 — not
because the code is hard to change, but because a dependency forbids it.

It exists to exercise the platform's **infeasibility** path: the agent
explores, finds the blocker, and says so, instead of attempting a migration
it cannot finish.

## The blocker

`requirements.txt` pins `pydantic-sqlalchemy==0.0.10`, which is its latest
release and declares `pydantic>=1.5.1,<2.0.0`. The constraint is not
advisory — pip refuses outright:

```
$ pip install 'pydantic-sqlalchemy==0.0.10' 'pydantic>=2'
ERROR: ResolutionImpossible
```

`src/records.py` generates the stored-customer schema from the SQLAlchemy
model with that library (`sqlalchemy_to_pydantic`), the API serves it
(`/records/example`), and `tests/test_api.py` asserts it appears in the
OpenAPI schema. FastAPI is pinned to 0.110.3, which supports both Pydantic
majors, so it is not the obstacle: upgrading it changes nothing.

Migrating the models alone would therefore not be a partial success. It
would break the service.

## Why this is the honest answer

No release of the library supports Pydantic v2, so no edit to
`requirements.txt` or `pyproject.toml` can make the migration install.
Removing the library and hand-writing the schemas is a different, larger
piece of work than the one that was requested and approved.

So the expected outcome is `BLOQUEADO`, substantiated: a dependency
conflict anyone can reproduce with one pip command, not a judgement call.

## Baseline

The suite is green, which is what makes this case distinct from a repo that
is simply broken:

```
pip install -r requirements.txt
pytest        # 21 passed
ruff check .
```
