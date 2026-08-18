# CLAUDE.md

Guidance for working in this repository.

## Rhiza-vs-local ownership split

This repo syncs its development infrastructure from the
[`jebel-quant/rhiza`](https://github.com/jebel-quant/rhiza) template. Some files
are **owned upstream** (regenerated on every sync — edit them in Rhiza, not
here) and some are **locally owned** (this repo controls them). Editing a
synced file locally will be reverted by the next `rhiza` sync and will fail the
`make validate` / template-fidelity checks.

### Rhiza-synced — fix upstream, don't edit here

- `.github/workflows/*` — reusable CI/CD workflows
- `Makefile` and `.rhiza/make.d/*.mk` — build/quality targets
- `.pre-commit-config.yaml` — pre-commit hooks
- `ruff.toml` — lint/format config
- `pytest.ini` — test/coverage config
- `.rhiza/` — the template payload (completions, config, assets)
- other template-managed root files (`Dockerfile`, `SECURITY.md`, `LICENSE`,
  `cliff.toml`, `.editorconfig`, …)

The authoritative, machine-generated list of synced files lives in
[`.rhiza/template.lock`](.rhiza/template.lock) under its `files:` block. When
in doubt, check there.

### Locally owned — edit freely

- `src/` — the `dummypy` package (`grid.py`, `payoffs.py`, `__init__.py`)
- `tests/` — the local test suite (mirrors `src/` 1:1), plus `tests/rhiza/`
  (see below)
- `pyproject.toml` — project metadata and dependencies
- `README.md` — project documentation
- `CHANGELOG.md` — public API surface across releases
- `CLAUDE.md` — this file
- `.rhiza/template.yml` — selects the template version, profile, and bundles
  (this is the one file *inside* `.rhiza/` that this repo owns)

## Conventions

- Tests mirror sources 1:1: `src/dummypy/<mod>.py` ↔ `tests/dummypy/test_<mod>.py`,
  and each source `class A` has a matching `TestA` (enforced by the
  test-layout checker).
- Coverage gate is 100% on `src/`.
- The rhiza conformance checks are **not** synced into `.rhiza/tests/`. That
  folder is listed under `exclude:` in `.rhiza/template.yml`; the checks come
  from the `pytest-rhiza` distribution pinned in `pyproject.toml` and are
  re-exported by `tests/rhiza/` so `make test` collects them. Consequences:
  `make rhiza-test` is now a warning no-op, and `make test-pyproject` is broken
  (it names `.rhiza/tests/test_pyproject.py`); run
  `uv run pytest tests/rhiza/test_pyproject.py -v` instead. Both targets live in
  synced make fragments, so neither can be fixed here — this is a consumer-side
  pilot of [jebel-quant/rhiza#1540](https://github.com/jebel-quant/rhiza/issues/1540)
  and unwinds when the template ships the plugin recipe itself.
- Bump the template with the `/rhiza:update` flow; don't hand-edit synced files.
