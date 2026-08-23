# CLAUDE.md

Guidance for working in this repository.

## Rhiza-vs-local ownership split

This repo syncs its development infrastructure from the
[`jebel-quant/rhiza`](https://github.com/jebel-quant/rhiza) template. Some files
are **owned upstream** (regenerated on every sync — edit them in Rhiza, not
here) and some are **locally owned** (this repo controls them). Editing a
synced file locally will be reverted by the next `rhiza` sync, which rewrites the
file from the template.

No local gate catches such an edit before then. There is no `validate` target —
`make` forwards to `rhiza-task`, whose task list has none, so `make validate`
dies with an unknown-task error — and `.rhiza/template.lock` records a template
`sha` for the payload as a whole, not per-file hashes anything could check
against. `/rhiza:status --check` is what reports the drift; pre-commit's
`check-rhiza-config` hook (run by `make fmt`) validates `.rhiza/template.yml`
itself, not the synced files it selects.

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
[`.rhiza/template.lock`](.rhiza/template.lock) under its `files:` block, with
what this repo has taken back under `exclude:`. When in doubt, check there —
and note that the lock, not `CLAUDE.md`, is what the sync obeys. The v1.3.4
sync is the cautionary tale: `Makefile` was called locally owned here while the
lock still listed it under `files:`, and the sync duly wrote conflict markers
across the shim.

### Locally owned — edit freely

- `src/` — the `dummypy` package (`grid.py`, `payoffs.py`, `__init__.py`)
- `tests/` — the local test suite (mirrors `src/` 1:1), plus `tests/rhiza/`
  (see below)
- `pyproject.toml` — project metadata, dependencies, and `[tool.rhiza-task]`
- `Makefile` — a shim forwarding to `rhiza-task` (see below). Repo-owned in the
  strong sense at v1.4.2: core ships no `Makefile`, and it does not appear in
  `.rhiza/template.lock`'s `files:` block, so nothing upstream regenerates it.
  It has no `exclude:` entry, and one would not protect it: the v1.3.4 → v1.4.2
  sync deleted it regardless, because the delete pass acts on what the *old* ref
  shipped and does not consult `exclude:`. It was restored byte-identical.
- `README.md` — project documentation
- `CHANGELOG.md` — public API surface across releases
- `CLAUDE.md` — this file
- `.rhiza/template.yml` — selects the template version, profile, and bundles,
  and lists what the sync must not deliver

## The developer tasks come from a package, not from make

`make test`, `make fmt`, `make book` and the rest still work, and are the *human*
front door. They are **not** what CI invokes: no workflow in this repository runs
`make` at all. Each one delegates to a `jebel-quant/rhiza` reusable workflow at
`@v1.4.2`, which pins its own CLI (`rhiza_ci.yml` sets
`RHIZA_TASK: rhiza-task@0.3.1`) and calls it directly, `uvx "$RHIZA_TASK" test`.
That pin is deliberately *not* read from this repo — "the gates a build runs must
not move under it" — so the local `RHIZA_TASK` governs local `make` alone. The
`Makefile` header carries the full story.

But `Makefile` no longer *contains* the targets either: it is a catch-all that
forwards every target to
[`rhiza-task`](https://github.com/jebel-quant/rhiza-task) on PyPI, pinned by the
one `RHIZA_TASK` variable at the top. That replaced `.rhiza/rhiza.mk` plus ten
fragments under `.rhiza/make.d/` — 1030 synced lines, at a template tag. None of
them needs an `exclude:` entry now, and none has one: v1.4.0 retired that layer
upstream, so core delivers no make layer at all, and nothing under
`.rhiza/make.d/` appears in the lock's `files:` block.

Consequences worth knowing:

- **Configuration lives in `[tool.rhiza-task]` in `pyproject.toml`**, not in
  make variables and not in a shadowed target. `coverage_fail_under = 100` and
  the mkdocstrings plugin used to be assignments in the root `Makefile`;
  `typechecker = "both"` is set explicitly because `rhiza-task`'s default is
  `ty` alone while the retired `python.mk` ran both, and this project is written
  for `mypy --strict`.
- **`.rhiza/.env` is gone**, and `[tool.rhiza-task]` is the only place this repo
  configures the task layer. `ci-os-matrix` is the one setting that had to move
  rather than simply disappear: `rhiza-task`'s default is `["ubuntu-latest"]`,
  and `rhiza_ci.yml` exports `RHIZA_CI_OS_MATRIX` empty for every consumer so
  that the consumer answers — so with nothing declared, CI would stay green
  while testing one OS instead of three. `SOURCE_FOLDER` and `MARIMO_FOLDER`
  were both restating a default and were dropped.
- **`make rhiza-test` is a real gate again.** It used to hit quality.mk's "no
  `.rhiza/tests` directory" branch, print a warning and exit 0 — a green gate
  measuring nothing. The CLI runs the `pytest-rhiza` checks with `--pyargs`, so
  there is no silent-pass branch. `make test-pyproject` works again for the same
  reason.
- **`make <task> --flag` does not work.** The shim forwards a target name, not
  flags; call `uvx rhiza-task <task> --flag` (e.g. `--strict`) directly.
- **Repo-specific targets** go in the `Makefile` itself or in an uncommitted
  `local.mk`; an explicit rule beats the catch-all.
- Two things the make layer had were missing at `rhiza-task` 0.1.2 and are back at
  0.3.1 (#252): `github.mk`'s `gh` wrappers — `view-prs`, `view-issues`, `whoami`,
  `failed-workflows`, `latest-release`, `workflow-status` — and
  `docker-build`/`docker-run`/`docker-clean`. 0.3.1 ships 35 tasks that 0.1.2 does
  not, these among them; `uvx rhiza-task list` is the current answer, not this
  list. Two caveats survive the bump. The `gh` wrappers remain thin — `gh pr list`
  is shorter than `make view-prs`. And the docker tasks were no-ops here because
  they looked for `docker/Dockerfile` while this repo's Dockerfile is at the root;
  whether 0.3.1 still does is **untested**, and the `(RHIZA) DOCKER` workflow
  probes the same path regardless.

### The one remaining make bridge

`Makefile` installs uv into `./bin` when it cannot find it, because
`rhiza_ci.yml@v1.3.4`'s `pre-commit` job runs `make fmt` with no
`astral-sh/setup-uv` step — every other job installs uv first. Delete the block
when the reusable workflow installs uv for that job too. It is commented in situ.

Two other bridges are gone. `.rhiza/rhiza.mk` held a single `ci-os-matrix`
target for `rhiza_ci.yml`'s `generate-matrix` job; `@v1.3.4` asks the CLI
instead ([jebel-quant/rhiza#1546](https://github.com/jebel-quant/rhiza/issues/1546)),
so the file and its `exclude:` entry both went. `Makefile` carried
`-include .rhiza/.env` so that `rhiza_marimo.yml` could read `MARIMO_FOLDER` out
of make's variable namespace; that probe still exists at `@v1.3.4`
([Jebel-Quant/rhiza#1553](https://github.com/Jebel-Quant/rhiza/pull/1553) is the
fix and is still open), so it now takes its `marimo` fallback — which changes
nothing observable, for the reason given under *Known broken* below.

## Conventions

- Tests mirror sources 1:1: `src/dummypy/<mod>.py` ↔ `tests/dummypy/test_<mod>.py`,
  and each source `class A` has a matching `TestA` (enforced by the
  test-layout checker).
- Coverage gate is 100% on `src/`.
- The rhiza conformance checks are **not** synced into `.rhiza/tests/`. v1.4.2
  core ships no such folder, so it needs no `exclude:` entry and has none; the
  checks come from the `pytest-rhiza` distribution declared in `pyproject.toml`
  and are re-exported by `tests/rhiza/` so `make test` collects them. That
  re-export is what puts them in CI: the reusable workflow runs `make test`, never
  `make rhiza-test`. Consumer-side pilot of
  [jebel-quant/rhiza#1540](https://github.com/jebel-quant/rhiza/issues/1540).
- Bump the template with the `/rhiza:update` flow; don't hand-edit synced files.
- Bump the task layer by editing `RHIZA_TASK` in the `Makefile` — that is the
  whole version contract.

## Measurement caveats

- **radon's maintainability index drops when you document the code.** Nothing
  here runs radon — it is not a gate, a hook or a workflow — but a quality
  review that reaches for it will find `grid.py` at MI 34.44 and `payoffs.py`
  at 31.78, down about 24 points from 58.56 and 61.25 before the #231 merge
  (`f61d135` → `c5f1d8f`). Not one executable line changed across that merge:
  `LLOC` stayed 36 and 20, `SLOC` 27 and 16, average cyclomatic complexity
  1.875 (A) over the same 8 blocks with none ranking worse than A. Only
  `Multi` — docstring lines — grew, 53 → 90 and 36 → 75, when #231 added 19
  doctests. radon's MI takes docstrings as length but credits only `#` lines
  in its comment term, so documentation is pure penalty; with 59% of their
  lines docstring or comment, both modules sit near the worst case for that
  formula. Both are still rank A (threshold 20), ~12 points of headroom. Track
  `LLOC` or CC for a trend line, and do not delete docstrings to move this
  number.
  ([#234](https://github.com/markrichardson/dummyrepo/issues/234))

## Known broken, and not this repo's doing

- **`make mutation`** fails, and did before the task migration: both the retired
  `test.mk` and `rhiza-task` call `mutmut run --paths-to-mutate=... ` and
  `mutmut html`, neither of which mutmut 3.x still has. The `(RHIZA) MUTATION`
  workflow does not run on pull requests, so nothing is gated on it.
- **The marimo notebooks are still not exercised by CI — but the local tasks now
  see them.** Both readers used to look in a folder that does not exist; the
  notebooks are in `book/marimo/notebooks/`. Half of that is fixed:
  `marimo-folder` is now set in `[tool.rhiza-task]`, so the CLI resolves it to
  the real folder instead of its `docs/notebooks` default, and `make marimo` /
  `make marimo-validate` genuinely run those notebooks rather than skipping.
  That was a change of behaviour, not of configuration — it is why the setting
  was left off for so long.
  The workflow half is unchanged. `rhiza_marimo.yml`'s make probe takes its
  `marimo` fallback (since `.rhiza/.env` is gone, nothing puts the variable in
  make's namespace) and it never reads `[tool.rhiza-task]`, so the workflow
  still finds nothing to run and the book still exports no notebooks. That needs
  [Jebel-Quant/rhiza#1553](https://github.com/Jebel-Quant/rhiza/pull/1553).
- ~~**The devcontainer bootstrap is broken under `rhiza-task` 0.1.2.**~~ Fixed by
  the 0.3.1 bump in #252. `.devcontainer/bootstrap.sh` exports
  `UV_SYNC_ARGS="--group test"` and runs `make install`; 0.1.2 read that setting
  as a *string* and splatted it character by character, so only whitespace-free
  or `;`-separated values survived. 0.3.1's `_coerce` handles it. Verified both
  ways rather than assumed:

  ```
  UV_SYNC_ARGS="--group test" uvx rhiza-task@0.1.2 install
    -> uv sync - - g r o u p   t e s t --inexact --frozen   (uv usage error)
  UV_SYNC_ARGS="--group test" uvx rhiza-task@0.3.1 install
    -> uv sync --group test --inexact --frozen
  ```

  CI was never affected — the devcontainer workflow builds the image without
  running lifecycle commands — so this only ever bit a human opening the
  container.
