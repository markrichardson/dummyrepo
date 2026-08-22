## Makefile (repo-owned) -- from `uvx rhiza-task shim > Makefile`, plus the uv block below
#
# This replaces `.rhiza/rhiza.mk` and the ten fragments in `.rhiza/make.d/`: 1030 synced
# lines, at a template tag, for one pinned package version. v1.4.0 retired that layer
# upstream as well -- core ships no Makefile and no `.rhiza/rhiza.mk` any more -- so this
# file is repo-owned in the strong sense: nothing regenerates it, and nothing upstream
# expects it to exist. (The v1.3.4 -> v1.4.2 sync still *deleted* it, because the delete
# pass acts on what the old ref shipped and does not consult `exclude:`. It was restored
# byte-identical; see .rhiza/template.yml.)
#
# What changed at v1.4.2: `make` is no longer what CI types. The reusable workflows used to
# run `make test`, `make fmt`, `make book`, `make benchmark`, `make semgrep`; they now call
# `uvx rhiza-task@0.3.1 <task>` directly -- rhiza_ci.yml, rhiza_book.yml,
# rhiza_benchmark.yml, rhiza_marimo.yml and rhiza_weekly.yml all pin the CLI themselves --
# because a consumer that syncs v1.4.x without keeping a shim has no make targets left and
# every gate dies with `No rule to make target 'test'`. So `make` here is now the *human*
# front door only: what a stranger types in an unfamiliar repository, and what a decade of
# muscle memory reaches for. Nothing in CI depends on this file any more, with the one
# unwanted exception noted at the catch-all rule below.
#
# RHIZA_TASK is still the entire version contract, but it governs local `make` alone: every
# workflow pins its own rhiza-task and none of them reads this variable. The two have
# drifted -- CI is on 0.3.1, this is on 0.1.2 -- so a local `make test` and CI's `test` are
# no longer the same code. 0.1.2 is also the version whose string-splatting `_coerce` breaks
# `.devcontainer/bootstrap.sh` (see CLAUDE.md). Bumping it is a deliberate change with its
# own blast radius, not a tidy-up.
#
# Everything this repo used to say in make variables now lives in `[tool.rhiza-task]` in
# pyproject.toml -- COVERAGE_FAIL_UNDER as `coverage_fail_under`, while
# MKDOCS_EXTRA_PACKAGES turned out to restate the CLI's own default and was dropped at the
# v1.4.2 bump. See CLAUDE.md.
RHIZA_TASK ?= rhiza-task@0.1.2

# --- The uv bootstrap: no longer a CI bridge, kept as a local convenience ------------------
#
# `uvx rhiza-task` presupposes uv, which is the point: the retired make layer had to curl
# `astral.sh/uv/install.sh` into `./bin` because make cannot assume it.
#
# This block was written for exactly one caller, with a delete-condition attached:
# rhiza_ci.yml@v1.3.4's `pre-commit` job ran `make fmt` on a bare runner with no
# `astral-sh/setup-uv` step, relying on this bootstrap while every other job installed uv
# first. That condition is now met. @v1.4.2 adds setup-uv to that job and runs the CLI
# directly, and rhiza#1546 added the same step to `generate-matrix` and to marimo's
# `list-notebooks` for the same reason.
#
# It is kept anyway, with its job changed: it is what makes `make test` work on a laptop
# that has never installed uv. Deleting it would now be safe for CI and would cost a
# stranger a `uvx: command not found`.
#
# So: resolve uvx once, and only when it cannot be found make the install a prerequisite of
# every target. Once installed the file exists, so the recipe runs at most once. `./bin` is
# gitignored, and `PATH` is extended for that case alone so that the task process finds the
# matching `uv` beside it.
#
# The recipes call `$(UVX)` by path rather than by name because make execs a single-command
# recipe itself, without a shell, and that lookup uses the PATH make started with -- so an
# exported PATH reaches the child process but not the command make is trying to run.
UVX := $(shell command -v uvx 2>/dev/null)
ifeq ($(UVX),)
UVX := $(CURDIR)/bin/uvx
UVX_BOOTSTRAP := $(UVX)
export PATH := $(CURDIR)/bin:$(PATH)
endif

$(CURDIR)/bin/uvx:
	@printf '[INFO] uvx not found -- installing uv into ./bin\n'
	@mkdir -p bin
	@curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR="$(CURDIR)/bin" UV_NO_MODIFY_PATH=1 sh

# The other bridge went with `.rhiza/.env`, and upstream has since retired the probe it fed.
#
# It was `-include .rhiza/.env`, so that rhiza_marimo.yml could read MARIMO_FOLDER out of
# make's variable namespace with
#
#   make -s -f Makefile -f - <<< 'print: ; @echo $(or $(MARIMO_FOLDER),marimo)' print
#
# @v1.3.4 still ran that probe. @v1.4.2 asks the CLI instead -- `uvx rhiza-task@0.3.1 print
# marimo_folder` -- so a root Makefile is no longer part of the reusable contract at all
# (Jebel-Quant/rhiza#1553, merged 2026-08-18). Nothing observable changes here under either
# answer: `marimo-folder` is deliberately unset in `[tool.rhiza-task]`, so the CLI returns
# its `docs/notebooks` default, and this repository's notebooks are in
# `book/marimo/notebooks/`. The workflow has therefore always found nothing. Pointing it at
# the real folder would newly run those notebooks in CI, which is a change of behaviour
# rather than of configuration -- see CLAUDE.md. Every other setting comes from
# `[tool.rhiza-task]` in pyproject.toml.

.DEFAULT_GOAL := help

help: $(UVX_BOOTSTRAP)
	@$(UVX) $(RHIZA_TASK) list

# The generated shim warns that "a *file* sharing a task's name would shadow it -- none
# do". In this repository two do, for different reasons, and both need the same treatment.
#
# `book/` holds the marimo notebooks and the minibook templates. make finds the directory,
# calls the target up to date and prints "make: `book' is up to date" instead of building
# anything. That used to break CI silently: rhiza_book.yml and rhiza_mutation.yml both ran
# `make book`. Neither does now -- @v1.4.2's book workflow calls `uvx rhiza-task book`, and
# rhiza_mutation.yml is excluded *and* deleted in this repo (see .rhiza/template.yml). What
# the rule still buys is the human case: `make book` producing silence instead of a book.
#
# `LICENSE` is the subtler one, because the names do not actually match: the task is
# `license` and the file is `LICENSE`. On a case-insensitive filesystem -- macOS APFS/HFS+
# and Windows, two of the three in `ci-os-matrix` -- make's stat for `license` finds
# `LICENSE` anyway and reports "make: `license' is up to date", so the copyleft scan never
# runs. Ubuntu is case-sensitive and unaffected, which is exactly what made this invisible:
# a gate reporting success while measuring nothing, in the one place CI cannot see it.
# Found by /rhiza:quality; see #245.
#
# Both lines are needed in each case, and neither alone is enough. `.PHONY` stops make
# consulting the filesystem -- but it also makes make *skip the implicit-rule search*, so
# the catch-all below stops matching and the target becomes "nothing to be done". The
# explicit rule supplies what the catch-all no longer can. This is what the retired book.mk
# did, minus the recipe.
#
# Any future task whose name collides with a root path -- case-insensitively -- needs an
# entry here too. `ls | tr A-Z a-z` against `uvx rhiza-task list` is how to check.
.PHONY: book license
book: $(UVX_BOOTSTRAP)
	@$(UVX) $(RHIZA_TASK) book

license: $(UVX_BOOTSTRAP)
	@$(UVX) $(RHIZA_TASK) license

# `%:` matches any target make cannot otherwise resolve. Two caveats, both survivable: a
# typo is routed here too (the CLI's "unknown task" error is the backstop), and a task
# needing flags wants `uvx rhiza-task <task> --flag` directly.
#
# One CI caller does still reach this rule, and it is an upstream bug rather than a use for
# the shim: rhiza_weekly.yml@v1.4.2's `gitlab-docker` job runs `make gitlab-docker-test`,
# ungated, in every consumer that calls the workflow -- this repo included, on the Monday
# 08:00 UTC schedule. That target is mother-repo-only: it lives in rhiza's own Makefile and
# is not a rhiza-task task (`uvx rhiza-task@0.3.1 list` does not list it), so here it lands
# on the catch-all and the job fails with an unknown-task error. The fix belongs upstream --
# do not answer it with a local rule.
%: $(UVX_BOOTSTRAP)
	@$(UVX) $(RHIZA_TASK) $@

# Repo-specific one-offs live here, where they always belonged, and win over the catch-all
# because an explicit rule beats a pattern rule. This is what `local.mk` was for.
-include local.mk

# An included makefile is also a target make tries to *remake* before running anything, and
# with a match-anything rule in scope that attempt is routed to the CLI -- so every
# invocation would begin with "unknown task: local.mk". An explicit rule with an empty
# recipe satisfies the remake attempt silently.
#
# `Makefile` needs one too, which the generated shim does not: make exempts an existing
# makefile from a match-anything rule only while that rule has no prerequisites, and the
# bootstrap above gives it one. Without this line `make help` tries to remake the Makefile
# by asking the CLI to build a task called "Makefile".
local.mk: ;
Makefile: ;
