![Tests](https://github.com/strangeworks/strangeworks-azure/actions/workflows/cron_test.yml/badge.svg)

# Strangeworks Azure Extension

Strangeworks Python SDK extension for Azure.

For more information on using the SDK check out the
[Strangeworks documentation](https://docs.strangeworks.com/).

## Dev Installation

Install using `poetry`. The `poetry install` manages all the dependencies and
dev-dependencies. The `pip install` is a workaround because poetry has a hard time with
the submodule install.

```
poetry install
poetry run pip install .
```

## Tests

Test using pytest

```
poetry run pytest tests/test_serialize.py
```

## Lint

Lint with black

```
poetry run black .
```

## Bump version

Bump version with [poetry](https://python-poetry.org/docs/cli/#version).

```
poetry version [patch, minor, major]
```
