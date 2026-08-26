# CLAUDE.md

Guidance for working in this repository.

## Rhiza-vs-local ownership split

This repo syncs its development infrastructure from the
[`jebel-quant/rhiza`](https://github.com/jebel-quant/rhiza) template, currently
at **v1.7.0**. Some files are **owned upstream** (regenerated on every sync —
edit them in Rhiza, not here) and some are **locally owned** (this repo controls
them). Editing a synced file locally will be reverted by the next `rhiza` sync,
which rewrites the file from the template.

A local gate does catch such an edit first: pre-commit's `check-managed-files`
(rhiza-hooks, run by `make fmt` and on every commit) refuses a commit touching
any path in `.rhiza/template.lock`'s `files:` block. It is why `/rhiza:update`
commits the sync with `SKIP=check-managed-files` — that one commit legitimately
rewrites the whole managed set. What the gate does *not* do is compare content:
the lock records a template `sha` for the payload as a whole, not per-file
hashes, so a synced file edited before the hook was adopted is invisible to it.
`/rhiza:status --check` is what reports that drift; `check-rhiza-config`
validates `.rhiza/template.yml` itself, not the synced files it selects. There
is still no `validate` target — `make` forwards to `rhiza-task`, whose task list
has none, so `make validate` dies with an unknown-task error.

### Rhiza-synced — fix upstream, don't edit here

- `Makefile` — the shim forwarding to `rhiza-task` (see below). **Template-owned
  again at v1.7.0**, and in the lock's `files:` block.
- `.github/workflows/*` — reusable CI/CD workflows
- `.pre-commit-config.yaml` — pre-commit hooks
- `ruff.toml` — lint/format config
- `pytest.ini` — test/coverage config
- `.python-version`
- `.rhiza/` — the template payload (semgrep rules, community docs, config)
- `.devcontainer/` — the devcontainer image and its bootstrap script
- `docker/Dockerfile` and `docker/Dockerfile.dockerignore` — moved out of the
  repo root by the v1.7.0 sync
- `docs/index.md`, `docs/mkdocs-base.yml`, `docs/development/DOCKER.md`,
  `docs/development/rhiza.md`
- `tests/test_rhiza_packaging.py` — the one test the template puts *inside*
  `tests/`
- other template-managed root files (`SECURITY.md`, `LICENSE`, `cliff.toml`,
  `.editorconfig`, `.gitignore`, `.bandit`, …)

The authoritative, machine-generated list of synced files lives in
[`.rhiza/template.lock`](.rhiza/template.lock) under its `files:` block, with
what this repo has taken back under `exclude:`. When in doubt, check there — and
note that the lock, not `CLAUDE.md`, is what the sync obeys. `Makefile` is the
cautionary tale twice over. At v1.3.4 this file called it locally owned while
the lock still listed it under `files:`, and the sync duly wrote conflict
markers across the shim. At v1.4.2 core shipped none and it was genuinely
repo-owned. At v1.7.0 core ships one again, so the answer flipped back — with
`RHIZA_TASK` inside it, which is the whole point (below).

### Locally owned — edit freely

- `src/` — the `dummypy` package (`grid.py`, `payoffs.py`, `__init__.py`)
- `tests/` — the local suite (mirrors `src/` 1:1), plus `tests/rhiza/` (see
  below). Everything except `tests/test_rhiza_packaging.py`.
- `pyproject.toml` — project metadata, dependencies, and `[tool.rhiza-task]`
- `mkdocs.yml` — `site_name`, `nav` and the mkdocstrings plugin config. It
  `INHERIT:`s the synced `docs/mkdocs-base.yml`, so theme and markdown
  extensions come from upstream and only the project-specific half lives here.
- `.github/rulesets/*.json` — taken back at v1.7.0. The template ships a generic
  branch/tag pair; the rules that actually apply here (required checks, tag
  patterns) are a per-repo decision.
- `.hadolint.yaml` — one setting, with the whole story in its header
- `local-setup.sh` — the native-dependency provisioning hook (below). Repo-owned
  content at a CLI-fixed name and location.
- `README.md` — project documentation
- `CHANGELOG.md` — public API surface across releases
- `CLAUDE.md` — this file
- `.rhiza/template.yml` — selects the template version, profile, and bundles,
  and lists what the sync must not deliver

`tests/fuzz/fuzz_grid.py` is an orphan rather than owned: nothing runs it, the
fuzzing workflow having been retired.
`.rhiza/scripts/customisations/build-extras.sh` was the other one and is gone —
`local-setup.sh` replaces it (below).

## The developer tasks come from a package, not from make

`make test`, `make fmt`, `make book` and the rest still work, and are the
*human* front door. They are **not** what CI invokes: no workflow in this
repository runs `make` at all. All but one delegate to a `jebel-quant/rhiza`
reusable workflow at `@v1.7.0`, which pins its own CLI (`rhiza_ci.yml` and
`rhiza_book.yml` both set `RHIZA_TASK: rhiza-task@1.4.0`) and calls it directly,
`uvx "$RHIZA_TASK" test`. The exception is `rhiza_release.yml`, which is a
self-contained workflow and invokes neither.

`Makefile` does not *contain* the targets either: it is a catch-all forwarding
every target to [`rhiza-task`](https://github.com/jebel-quant/rhiza-task) on
PyPI, pinned by the one `RHIZA_TASK` variable at the top. That replaced
`.rhiza/rhiza.mk` plus ten fragments under `.rhiza/make.d/` — 1030 synced lines
— at v1.4.0.

Consequences worth knowing:

- **The version contract moved.** Local `make` and CI used to be pinned
  separately, on the reasoning that "the gates a build runs must not move under
  it"; the local `RHIZA_TASK` was a hand edit `/rhiza:update` could not make, so
  every consumer silently lagged. Since the shim is synced again, `RHIZA_TASK`
  travels with the template ref and both sides read `rhiza-task@1.4.0` from
  v1.7.0 by construction. **Bump the task layer with `/rhiza:update`, not by
  editing the `Makefile`** — an edit there is drift the next sync reverts.
- **Configuration lives in `[tool.rhiza-task]` in `pyproject.toml`**, not in
  make variables. `coverage_fail_under = 100`, `mkdocs-extra-packages` and
  `ci-os-matrix` are each commented in situ with why they are not a restated
  default; `typechecker = "both"` is set because `rhiza-task`'s default is `ty`
  alone and this project is written for `mypy --strict`.
- **`.rhiza/.env` is gone**, and `[tool.rhiza-task]` is the only place this repo
  configures the task layer.
- **`make <task> --flag` does not work.** The shim forwards a target name, not
  flags; call `uvx rhiza-task <task> --flag` (e.g. `--strict`) directly.
- **`uvx rhiza-task list` is the current answer**, not a list in this file.
  1.4.0 adds, among others, `book-nav`, `complexity`, `docs-examples`, `todos`,
  `doctor` and the `paper`/`presentation`/`lfs-*` families, and has dropped
  `mutation` and `fuzz` entirely.
- **`book-nav` is a CI gate.** `rhiza_book.yml@v1.7.0` runs it after `book`, so
  a `nav:` entry in `mkdocs.yml` pointing at a file the sync deleted fails the
  build — which is exactly what the v1.5.1 → v1.7.0 bump would have done to the
  three `docs/development/` pages it replaced with `rhiza.md`.
- **The docker tasks and the docker workflow are no longer no-ops.** Both
  resolve `docker/Dockerfile` — the CLI via `docker_folder`, which defaults to
  `docker`; `rhiza_docker.yml` by a literal `[ -f docker/Dockerfile ]` probe —
  and v1.7.0 moved the Dockerfile there from the repo root. The workflow had
  been printing a skip notice for as long as the path was wrong, so v1.7.0 is
  the first time it has actually linted and built. See `.hadolint.yaml` for
  what that surfaced.
- **Native dependencies go in `local-setup.sh`**, the repository root hook that
  `rhiza-task`'s `setup` task runs. `setup` is a prerequisite of `install`, and
  `install` of essentially every gate, so one file covers local `make test`, CI
  and the devcontainer with no workflow edit. It provisions graphviz, which
  `loman` shells out to for the plot in
  `book/marimo/notebooks/notebook-extras.py`. This is the sanctioned successor
  to `.rhiza/scripts/customisations/build-extras.sh`, and to the advice to
  shadow `install` in `local.mk` — which never worked, because `install` is a
  prerequisite inside the CLI and never reaches a make rule of that name.
  Requires `rhiza-task` >= the version that ships `setup`; 1.1.0 has no such
  task, 1.4.0 does.
- The `gh` wrappers (`view-prs`, `view-issues`, `whoami`, `failed-workflows`,
  `latest-release`, `workflow-status`) remain thin — `gh pr list` is shorter
  than `make view-prs`.

## Conventions

- Tests mirror sources 1:1: `src/dummypy/<mod>.py` ↔
  `tests/dummypy/test_<mod>.py`, and each source `class A` has a matching
  `TestA` (enforced by the test-layout checker; `tests/rhiza/` is exempted in
  `[tool.check_test_layout]`).
- Coverage gate is 100% on `src/`.
- The rhiza conformance checks are **not** synced into `.rhiza/tests/`. Core
  ships no such folder, so it needs no `exclude:` entry and has none; the checks
  come from the `pytest-rhiza` distribution declared in `pyproject.toml` and are
  re-exported by `tests/rhiza/` so `make test` collects them. Consumer-side
  pilot of
  [jebel-quant/rhiza#1540](https://github.com/jebel-quant/rhiza/issues/1540).
  The re-export's own docstring says it exists because CI ran `make test` and
  never `make rhiza-test`; **that is no longer true** — `rhiza_ci.yml@v1.7.0`
  has a dedicated `rhiza-test` job. The re-export is now belt-and-braces rather
  than the only path.
- **The two `pytest-rhiza` pins have drifted.** The `test` dependency group
  floors it at `>=0.4.0` (a dependabot bump), while `[tool.rhiza-task]
  pytest-rhiza` still pins `==0.2.1` for what `make rhiza-test` provisions on
  the fly. The comment beside the latter says to keep the two in step, and they
  are not. Resolve deliberately — the CLI's own default still names a git tag at
  v0.2.0, so simply deleting the setting would not follow the group.
- Bump the template with the `/rhiza:update` flow; don't hand-edit synced files.

## Measurement caveats

- **radon's maintainability index drops when you document the code.** Nothing
  here runs radon — it is not a gate, a hook or a workflow — but a quality
  review that reaches for it will find `grid.py` at MI 34.44 and `payoffs.py` at
  31.78, down about 24 points from 58.56 and 61.25 before the #231 merge
  (`f61d135` → `c5f1d8f`). Not one executable line changed across that merge:
  `LLOC` stayed 36 and 20, `SLOC` 27 and 16, average cyclomatic complexity 1.875
  (A) over the same 8 blocks with none ranking worse than A. Only `Multi` —
  docstring lines — grew, 53 → 90 and 36 → 75, when #231 added 19 doctests.
  radon's MI takes docstrings as length but credits only `#` lines in its
  comment term, so documentation is pure penalty; with 59% of their lines
  docstring or comment, both modules sit near the worst case for that formula.
  Both are still rank A (threshold 20), ~12 points of headroom. Track `LLOC` or
  CC for a trend line, and do not delete docstrings to move this number.
  ([#234](https://github.com/markrichardson/dummyrepo/issues/234))

## Known broken, and not this repo's doing

- **`make mutation` no longer exists.** It used to fail because both the retired
  `test.mk` and early `rhiza-task` called `mutmut run --paths-to-mutate=…` and
  `mutmut html`, neither of which mutmut 3.x still has. `rhiza-task@1.4.0` has
  dropped the task — `make mutation` is now an unknown-task error — and no
  mutation or fuzzing workflow is synced any more. `tests/fuzz/fuzz_grid.py` is
  what is left of it.
- **The marimo notebooks are still not exercised by CI, but it is now one
  knob.** The notebooks are in `book/marimo/notebooks/`; `rhiza-task` resolves
  `marimo_folder` to its `docs/notebooks` default. Both readers finally agree —
  the `.rhiza/.env` probe in `rhiza_marimo.yml` is gone
  ([Jebel-Quant/rhiza#1553](https://github.com/Jebel-Quant/rhiza/pull/1553)
  landed), and the workflow now asks the CLI for the same setting. So
  `marimo-folder = "book/marimo/notebooks"` in `[tool.rhiza-task]` would fix the
  CLI half and the workflow half at once. It is left unset on purpose: doing it
  would newly run those notebooks in CI, which is a change of behaviour rather
  than of configuration. Do it deliberately.
- **`rhiza_docker.yml`'s hadolint step is stricter than it says.** Its comment
  reads "fail on any error-level findings (default behavior)", but
  hadolint-action leaves `failure-threshold` unset and hadolint's own default is
  `info` — so the two info-level `DL3066` findings in the template's own
  Dockerfile fail the job. Worked around locally by `.hadolint.yaml`; the fix is
  upstream, either pinning `failure-threshold: error` on the step or giving the
  Dockerfile a numeric UID. The same job then reports a second, cascading
  failure — `upload-sarif` runs under `if: always()` and errors with "Path does
  not exist: trivy-results.sarif", because the trivy step never ran. That noise
  disappears with the first fix.
- ~~**The devcontainer bootstrap is broken under `rhiza-task` 0.1.2.**~~ Fixed
  in #252 by the 0.3.1 bump. 0.1.2 read `UV_SYNC_ARGS="--group test"` as a
  string and splatted it character by character; `_coerce` handles it from 0.3.1
  on. CI was never affected — the devcontainer workflow builds the image without
  running lifecycle commands.
