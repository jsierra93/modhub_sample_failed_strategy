# modhub_sample_failed_strategy

A FastAPI service whose Pydantic v1 models cannot be migrated to v2 — not
because the code is hard to change, but because a dependency forbids it.

It exists to exercise the platform's **infeasibility** path: the agent
explores, finds the blocker, and says so, instead of attempting a migration
it cannot finish.

## The blocker

`requirements.txt` pins `fastapi==0.99.1`, the last release before FastAPI
supported Pydantic v2. That version requires `pydantic>=1.6.2,<2.0.0`, and
the constraint is not advisory — pip refuses outright:

```
$ pip install 'fastapi==0.99.1' 'pydantic>=2.9'
ERROR: Cannot install fastapi==0.99.1 and pydantic>=2.9 because these
package versions have conflicting dependencies.
ERROR: ResolutionImpossible
```

FastAPI 0.99 reads the models directly to build request validation and the
OpenAPI schema, so the framework and the models have to agree on which
major version of Pydantic is in play. `tests/test_api.py` pins that
coupling: it asserts the framework rejects an invalid body with 422 and
that `Customer` appears in the generated OpenAPI schema.

Migrating the models alone would therefore not be a partial success. It
would break the service.

## Why this is the honest answer

The blocker is outside anything the agent is allowed to change. It can edit
Python files and `requirements.txt`, but it cannot make a released version
of FastAPI support a Pydantic it never supported. The real fix — upgrading
FastAPI to 0.100+ as well — is a different, larger piece of work than the
one that was requested and approved.

So the expected outcome is `BLOQUEADO`, substantiated: a dependency
conflict anyone can reproduce with one pip command, not a judgement call.

## Baseline

The suite is green, which is what makes this case distinct from a repo that
is simply broken:

```
pip install -r requirements.txt
pytest        # 19 passed
ruff check .
```
