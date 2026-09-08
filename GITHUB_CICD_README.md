# CI/CD and Development Infrastructure

How this repository is built, tested, documented and released — and, just as
importantly, *where each of those decisions actually lives*, because almost none of it
lives in this repository.

> **Scope and ownership.** This file is **locally owned** (see `CLAUDE.md`), but nearly
> everything it describes is **template-owned**: synced from
> [`jebel-quant/rhiza`](https://github.com/jebel-quant/rhiza), currently at **v1.7.2**,
> and regenerated on every `/rhiza:update`. Fix a workflow *upstream*, not here — a local
> edit to a synced file is reverted by the next sync, and pre-commit's
> `check-managed-files` hook refuses the commit in the meantime. The authoritative list of
> synced paths is the `files:` block of [`.rhiza/template.lock`](.rhiza/template.lock).

## The one thing to know first

**CI does not run `make`.** No workflow in this repository invokes it. The workflows are
thin stubs that delegate to reusable workflows in `jebel-quant/rhiza@v1.7.2`, which pin
their own copy of the task runner (`RHIZA_TASK: rhiza-task@1.5.0`) and call it directly:

```yaml
run: uvx "$RHIZA_TASK" test
```

`make` is the *human* front door to the same tasks. The root `Makefile` is a catch-all
shim that forwards every target to [`rhiza-task`](https://github.com/jebel-quant/rhiza-task)
on PyPI, pinned by the single `RHIZA_TASK` variable at its top — also `rhiza-task@1.5.0`,
because the shim is itself synced, so both sides move together with the template ref.

The practical consequence: local and CI run the *same task definitions from the same CLI
version*, but they are two independent pins that agree by construction rather than by
mechanism. Bump them with `/rhiza:update`, never by editing the `Makefile`.

## Where the pieces live

```text
.github/
├── workflows/               # 10 workflow stubs, all template-owned except rhiza_book.yml
│   ├── rhiza_ci.yml         #   → tests, typecheck, deptry, hooks, security, license
│   ├── rhiza_book.yml       #   → docs site; LOCALLY OWNED (adds Cloudflare Pages deploy)
│   ├── rhiza_release.yml    #   → tag-driven release; self-contained, not a stub
│   ├── rhiza_marimo.yml     #   → executes every Marimo notebook
│   ├── rhiza_benchmark.yml  #   → performance baseline on main
│   ├── rhiza_docker.yml     #   → hadolint + build + Trivy
│   ├── rhiza_devcontainer.yml
│   ├── rhiza_codeql.yml
│   ├── rhiza_scorecard.yml
│   └── rhiza_weekly.yml
├── dependabot.yml           # dependency updates (NOT Renovate — see below)
├── release.yml              # release-notes categorisation by PR label
└── secret_scanning.yml      # paths-ignore for GitHub secret scanning

.pre-commit-config.yaml      # 21 hooks, run by `make fmt` and on commit
pyproject.toml               # deps, and [tool.rhiza-task] — where CI/gate config lives
Makefile                     # the shim; contains no targets of its own
local-setup.sh               # native-dependency hook, run by rhiza-task's `setup`
.rhiza/                      # template payload (semgrep rules, community docs, lock)
.devcontainer/               # devcontainer image + bootstrap.sh
```

There is **no** `.rhiza/.env` and **no** `.rhiza/make.d/` — the ten make fragments and the
dotenv were retired at v1.4.0. Configuration that used to be a make variable is now a key
in `[tool.rhiza-task]` in `pyproject.toml`.

## Workflows

| Workflow | Trigger | What it does |
| --- | --- | --- |
| **CI** | every push, every PR | The main gate. Jobs detailed below. |
| **Book** | every push, any branch | Builds the docs site with zensical; deploys to GitHub Pages from the default branch, plus a repo-owned Cloudflare Pages job. Other branches build an artifact only. |
| **Marimo** | push/PR to `main` | Runs every notebook in parallel, `fail-fast: false`. |
| **Benchmark** | push to `main` | Performance baseline over time. |
| **Docker** | push/PR to `main` | Lints `docker/Dockerfile` with hadolint, builds it, scans with Trivy. |
| **Devcontainer** | push/PR touching `.devcontainer/**` | Builds the image (`push: never`); runs no lifecycle commands. |
| **CodeQL** | push/PR to `main`, weekly (Mon 01:27) | Code scanning for Python and Actions. |
| **Scorecard** | weekly (Tue 02:34), push to `main`, branch-protection changes, dispatch | OSSF supply-chain score. |
| **Weekly** | weekly (Mon 08:00 UTC), dispatch | `dep-compat-test` resolves dependencies fresh, ignoring the lockfile, and runs the suite; `link-check` verifies README links. |
| **Release** | push of a `v*` tag | See [Release pipeline](#release-pipeline). |

### The CI workflow's jobs

Every gate step is `uvx "$RHIZA_TASK" <task>`, so each one has an exact local equivalent.

| Job | Runs | Local equivalent |
| --- | --- | --- |
| `generate-matrix` | Derives the Python matrix from the `Programming Language :: Python :: 3.x` classifiers in `pyproject.toml`, and the OS matrix from `ci-os-matrix` | `uvx rhiza-task ci-os-matrix` |
| `test` | The suite across the full matrix, then verifies a clean working tree | `make test` |
| `typecheck` | `ty` **and** `mypy --strict` (`typechecker = "both"`) | `make typecheck` |
| `lowest-deps` | The suite under `--resolution lowest-direct` | — |
| `deptry` | Unused/missing dependency scan over `src` and `docs/notebooks` | `make deps` |
| `rhiza-test` | The `pytest-rhiza` repository-conformance checks | `make rhiza-test` |
| `pre-commit` | All hooks via prek, with `~/.cache/prek` cached | `make fmt` |
| `docs-coverage` | Docstring coverage via interrogate | `make docs-coverage` |
| `security` | bandit | `make security` |
| `license` | Copyleft licence scan | `make license` |
| `ci-gate` | Roll-up: aggregates `test`, `typecheck`, `lowest-deps` and `rhiza-test` into one status check | — |

**`ci-gate` is the context branch protection should require**, not the individual matrix
legs — that is the whole point of the roll-up: the matrix can change without editing the
ruleset.

The matrix is currently 3.11–3.14 × `ubuntu-latest`, `macos-latest`, `windows-latest`
(12 test legs). Both halves are data, not workflow edits: add a classifier to change the
Python axis, edit `ci-os-matrix` in `[tool.rhiza-task]` to change the OS axis. Note that
`ci-os-matrix` is **not** an optional restatement of a default — the CLI's default is
`["ubuntu-latest"]` alone, and CI would go green while quietly testing one OS if the key
were removed.

## Local development

```bash
make fmt      # Run every pre-commit hook over all files (ruff lint + format, and the rest)
make install  # Create the venv, sync dependencies, install the git hooks
make test     # Run the suite with the coverage gate
make all      # Every gate, as CI does: fmt, deps, test, docs-coverage, security,
              #   license, typecheck, rhiza-test
make help     # The authoritative target list, straight from the CLI
```

`uvx rhiza-task list` is the real inventory — 46 tasks at `rhiza-task@1.5.0`, including `book`,
`book-nav`, `serve`, `marimo`, `complexity`, `todos`, `doctor`, `coverage`,
`docs-examples` and the `paper`/`presentation`/`lfs-*` families. Do not expect this file
to stay in step with it.

Things people reach for that **do not exist**:

- **`make lint`, `make format`** — `rhiza-task` ships no such task. Linting *and*
  formatting both live behind `make fmt`, which runs the `ruff` and `ruff-format` hooks
  (among the other nineteen) through prek.
- **`make pre-commit`, `make install-hooks`** — running the hooks is `make fmt`; installing
  them is folded into `make install`, which calls `install_hooks` after the sync.
- **`make validate`** — never existed.
- **`make mutation`, `make fuzz`** — dropped from the CLI at 1.4.0; no mutation or fuzzing
  workflow is synced any more.

Because the shim forwards *every* unknown target to the CLI, each of those dies with an
unknown-task error rather than a make error.

**`make <task> --flag` does not work** — the shim forwards a target name, not flags. Call
`uvx rhiza-task <task> --flag` directly.

**Native dependencies go in `local-setup.sh`**, the repo-root hook that the CLI's `setup`
task runs. `setup` is a prerequisite of `install`, and `install` of essentially every gate,
so that one file covers local `make test`, CI and the devcontainer with no workflow edit.
It currently provisions graphviz, which `loman` shells out to for a notebook plot.

## Pre-commit hooks

Enforced locally on commit and in CI's `pre-commit` job. Run with `make fmt`
(which uses [prek](https://github.com/j178/prek), a Rust reimplementation reading the same
config); `.pre-commit-config.yaml` is template-owned.

| Source | Hooks |
| --- | --- |
| `pre-commit-hooks` | `check-toml`, `check-yaml` |
| `ruff-pre-commit` | `ruff` (`--fix --exit-non-zero-on-fix --unsafe-fixes`), `ruff-format` |
| `markdownlint-cli` | `markdownlint` (MD013 disabled) |
| `check-jsonschema` | `check-renovate`, `check-github-workflows` |
| `actionlint` | `actionlint` |
| `validate-pyproject` | `validate-pyproject` |
| `bandit` | `bandit` (scope in `.bandit`, not in the hook args) |
| `betterleaks` | hardcoded-secret detection |
| `uv-pre-commit` | `uv-lock` — fails if `uv.lock` is out of step with `pyproject.toml` |
| `interrogate` | docstring coverage over `src/` |
| `rhiza-hooks` | `check-rhiza-workflow-names`, `update-readme-help`, `check-rhiza-config`, `check-managed-files`, `check-makefile-targets`, `check-python-version-consistency` |
| local | `no-python-cache-files`, `no-rej-files` |

Two are worth understanding rather than just listing:

- **`check-managed-files`** refuses any commit touching a path in `.rhiza/template.lock`'s
  `files:` block. It is why `/rhiza:update` commits its sync with
  `SKIP=check-managed-files`. It compares *paths, not content*, so a synced file edited
  before the hook existed is invisible to it — `/rhiza:status --check` is what reports that
  drift.
- **`ruff` appears here and nowhere else.** The version that lints this code is the
  `rev:` pin in `.pre-commit-config.yaml`, which prek provisions in its own isolated
  environment. Ruff is deliberately **not** a declared project dependency: nothing reads
  such a group, and a pin there would only drift against the one that runs. Use
  `uvx ruff …` for ad-hoc runs.

Hook rules and formatter settings are configured in `ruff.toml` (template-owned) and
`pytest.ini`; project-side gate settings are in `[tool.rhiza-task]`.

## Dependency updates

**Dependabot, not Renovate.** [`.github/dependabot.yml`](.github/dependabot.yml) configures
two ecosystems:

- **`uv`** — Python dependencies, weekly (Tuesday 09:00 Asia/Dubai), patch and minor
  grouped into a single `python-dependencies` PR, major updates ignored entirely.
- **`github-actions`** — same schedule and grouping. The Docker ecosystem block is
  commented out.

Commits are prefixed `chore(deps)` / `chore(deps-dev)`. Nothing auto-merges: every update
goes through CI like any other PR.

The `check-renovate` hook is present because it ships in the template's hook set, but there
is no `renovate.json`, so it always skips. Pre-commit hook `rev:`s are therefore **not**
bumped by a bot here — they move when the template does.

## Release pipeline

`rhiza_release.yml` is the one workflow that is **not** a stub, and its header explains why:
PyPI Trusted Publishing validates the exact workflow path and repository that invokes
`pypa/gh-action-pypi-publish`, so delegating would make PyPI see rhiza as the publisher.
It is therefore synced whole, and invokes no `rhiza-task` at all.

Triggered by pushing a `v*` tag. Jobs, in order: `tag` (validate the tag, ensure it is
reachable from a branch, and that the version is newer than the latest published) →
`build` (Hatch build, CycloneDX SBOM, SLSA provenance attestations) → `draft-release`
(notes via git-cliff, per `cliff.toml`) → `pypi` → `conda` → `devcontainer` →
`finalise-release`.

**This package does not publish to PyPI.** The `pypi` job greps `pyproject.toml` for the
`Private :: Do Not Upload` classifier and skips when it finds it. Removing that classifier
starts real uploads.

Versioning: `bump-my-version` reads and rewrites PEP 621 `[project].version` natively.
`[tool.bumpversion]` keeps `commit` and `tag` false because the release flow makes both
itself, and one `[[tool.bumpversion.files]]` entry keeps the README footer's version in
step. `CHANGELOG.md` is folded into the version-bump commit *before* the tag is pushed, so
the tagged commit already carries it.

## Devcontainer and Codespaces

[`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json) is template-owned.

- **Image:** `mcr.microsoft.com/devcontainers/python:3.14`, minimum 4 CPUs, `~/.ssh` bind-mounted.
- **Features:** GitHub CLI, Copilot CLI, Node, docker-in-docker.
- **Extensions:** Python + Pylance, Marimo, Ruff, Even Better TOML, Makefile Tools,
  Copilot, Claude Code.
- **Ports forwarded:** 8080 and 2718 (Marimo's default).
- **Setup:** `onCreateCommand` runs `.devcontainer/bootstrap.sh`, which reads
  `.python-version`, installs `uv`/`uvx` into `/home/vscode/.local/bin`, and runs
  `make install` with `UV_SYNC_ARGS="--group test"` — a deliberately lightweight set, since
  prek and `uvx` provision every linter on the fly. Override `UV_SYNC_ARGS` for more.
- No Marimo server auto-starts; run `make marimo` yourself.

Note that local `make install` syncs `--all-extras --all-groups` (the CLI default), so a
devcontainer's environment is intentionally *narrower* than a laptop's, not identical.
The Devcontainer CI workflow builds the image but runs no lifecycle commands, so a broken
`bootstrap.sh` can pass CI — that has bitten this repo before.

## Caveats and known-broken

`CLAUDE.md` is the maintained record of these; the short version:

- **`rhiza_docker.yml`'s hadolint step is stricter than its comment claims** — it leaves
  `failure-threshold` unset, and hadolint's own default is `info`, so info-level findings
  fail the job. Worked around by `.hadolint.yaml`; the fix is upstream. Its `upload-sarif`
  step then reports a cascading "Path does not exist: trivy-results.sarif".
- **`book-nav` is a CI gate.** A `nav:` entry in `mkdocs.yml` pointing at a file a sync
  deleted fails the book build.
- **`.github/rulesets/` is listed under `exclude:` in `.rhiza/template.yml` but is not
  present in the tree** — the directory was deleted in `ecf91c9`. Branch and tag protection
  are whatever is configured in the GitHub UI; there is no checked-in ruleset to read.
- **The two `pytest-rhiza` pins disagree.** The `test` dependency group floors it at
  `>=0.5.0`; `[tool.rhiza-task] pytest-rhiza` pins `==0.2.1` for what `make rhiza-test`
  provisions on the fly. Resolve deliberately — the CLI's own default names an even older
  git tag.
- **Radon's maintainability index drops when you document code.** Nothing here runs radon.
  Do not delete docstrings to move that number.
