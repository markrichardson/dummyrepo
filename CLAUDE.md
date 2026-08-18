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
- `.pre-commit-config.yaml` — pre-commit hooks
- `ruff.toml` — lint/format config
- `pytest.ini` — test/coverage config
- `.rhiza/` — the template payload (semgrep rules, scripts, config)
- `.devcontainer/` — the devcontainer image and its bootstrap script
- other template-managed root files (`Dockerfile`, `SECURITY.md`, `LICENSE`,
  `cliff.toml`, `.editorconfig`, …)

The authoritative, machine-generated list of synced files lives in
[`.rhiza/template.lock`](.rhiza/template.lock) under its `files:` block. When
in doubt, check there. (The lock records the *last sync*, so it still lists the
make layer this repo has since excluded; `/rhiza:update` regenerates it.)

### Locally owned — edit freely

- `src/` — the `dummypy` package (`grid.py`, `payoffs.py`, `__init__.py`)
- `tests/` — the local test suite (mirrors `src/` 1:1), plus `tests/rhiza/`
  (see below)
- `pyproject.toml` — project metadata, dependencies, and `[tool.rhiza-task]`
- `Makefile` — a shim forwarding to `rhiza-task` (see below)
- `.rhiza/rhiza.mk` — twenty repo-owned lines, *not* the template's file of that
  name (see below)
- `README.md` — project documentation
- `CHANGELOG.md` — public API surface across releases
- `CLAUDE.md` — this file
- `.rhiza/template.yml` — selects the template version, profile, and bundles,
  and lists what the sync must not deliver

## The developer tasks come from a package, not from make

`make test`, `make fmt`, `make book` and the rest still work, and are still what
CI invokes. But `Makefile` no longer *contains* them: it is a catch-all that
forwards every target to
[`rhiza-task`](https://github.com/jebel-quant/rhiza-task) on PyPI, pinned by the
one `RHIZA_TASK` variable at the top. That replaced `.rhiza/rhiza.mk` plus ten
fragments under `.rhiza/make.d/` — 1030 synced lines, at a template tag, all of
them excluded in `.rhiza/template.yml` now.

Consequences worth knowing:

- **Configuration lives in `[tool.rhiza-task]` in `pyproject.toml`**, not in
  make variables and not in a shadowed target. `coverage_fail_under = 100` and
  the mkdocstrings plugin used to be assignments in the root `Makefile`;
  `typechecker = "both"` is set explicitly because `rhiza-task`'s default is
  `ty` alone while the retired `python.mk` ran both, and this project is written
  for `mypy --strict`.
- **`.rhiza/.env` is still read**, by the CLI directly, and stays the place to
  set `SOURCE_FOLDER`, `MARIMO_FOLDER` and `RHIZA_CI_OS_MATRIX`.
- **`make rhiza-test` is a real gate again.** It used to hit quality.mk's "no
  `.rhiza/tests` directory" branch, print a warning and exit 0 — a green gate
  measuring nothing. The CLI runs the `pytest-rhiza` checks with `--pyargs`, so
  there is no silent-pass branch. `make test-pyproject` works again for the same
  reason.
- **`make <task> --flag` does not work.** The shim forwards a target name, not
  flags; call `uvx rhiza-task <task> --flag` (e.g. `--strict`) directly.
- **Repo-specific targets** go in the `Makefile` itself or in an uncommitted
  `local.mk`; an explicit rule beats the catch-all.
- Two things the make layer had are gone without replacement: `github.mk`'s
  seven `gh` wrappers (`gh pr list` is shorter than `make view-prs`) and
  `docker-build`/`docker-run`/`docker-clean`, which looked for `docker/Dockerfile`
  while this repo's Dockerfile is at the root — they were already no-ops, as is
  the `(RHIZA) DOCKER` workflow, which probes the same path.

### The two make bridges, and when they go

Both exist only because this repo pins the reusable workflows at `@v1.3.3`,
which still speaks make in two places. Both are commented in situ.

1. `Makefile` installs uv into `./bin` when it cannot find it, because
   `rhiza_ci.yml`'s `pre-commit` job runs `make fmt` with no `setup-uv` step.
2. `.rhiza/rhiza.mk` keeps a single `ci-os-matrix` target, because
   `rhiza_ci.yml`'s `generate-matrix` job runs
   `make -f .rhiza/rhiza.mk -s ci-os-matrix` — also with no uv — and because
   `rhiza_marimo.yml` reads `MARIMO_FOLDER` out of make's variable namespace,
   which is why `Makefile` includes `.rhiza/.env`.

`@v1.3.4` drops the `rhiza.mk` caller ([jebel-quant/rhiza#1546](https://github.com/jebel-quant/rhiza/issues/1546));
delete the file when this repo's workflows pin it.

## Conventions

- Tests mirror sources 1:1: `src/dummypy/<mod>.py` ↔ `tests/dummypy/test_<mod>.py`,
  and each source `class A` has a matching `TestA` (enforced by the
  test-layout checker).
- Coverage gate is 100% on `src/`.
- The rhiza conformance checks are **not** synced into `.rhiza/tests/`. That
  folder is listed under `exclude:` in `.rhiza/template.yml`; the checks come
  from the `pytest-rhiza` distribution declared in `pyproject.toml` and are
  re-exported by `tests/rhiza/` so `make test` collects them. That re-export is
  what puts them in CI: the reusable workflow runs `make test`, never
  `make rhiza-test`. Consumer-side pilot of
  [jebel-quant/rhiza#1540](https://github.com/jebel-quant/rhiza/issues/1540).
- Bump the template with the `/rhiza:update` flow; don't hand-edit synced files.
- Bump the task layer by editing `RHIZA_TASK` in the `Makefile` — that is the
  whole version contract.

## Known broken, and not this repo's doing

- **`make mutation`** fails, and did before the task migration: both the retired
  `test.mk` and `rhiza-task` call `mutmut run --paths-to-mutate=... ` and
  `mutmut html`, neither of which mutmut 3.x still has. The `(RHIZA) MUTATION`
  workflow does not run on pull requests, so nothing is gated on it.
- **The marimo notebooks are not exercised by CI.** `.rhiza/.env` points
  `MARIMO_FOLDER` at `docs/notebooks`, which does not exist — the notebooks are
  in `book/marimo/notebooks/`. So `rhiza_marimo.yml` finds nothing to run,
  `make marimo-validate` skips, and the book exports no notebooks. Fixing the
  path would newly run those notebooks in CI, which is a change of behaviour
  rather than a change of configuration; do it deliberately.
- **The devcontainer bootstrap is broken under `rhiza-task` 0.1.2.**
  `.devcontainer/bootstrap.sh` exports `UV_SYNC_ARGS="--group test"` and runs
  `make install`; `rhiza-task` reads that setting as a *string* and splats it
  character by character into `uv sync - - g r o u p ...`. Only whitespace-free
  or `;`-separated values survive. CI is unaffected — the devcontainer workflow
  builds the image without running lifecycle commands — but a human opening the
  container hits it. The fix belongs in `rhiza-task`'s `_coerce`.
