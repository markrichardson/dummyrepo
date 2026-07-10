## Makefile (repo-owned)
# Keep this file small. It can be edited without breaking template sync.

LOGO_FILE=.rhiza/assets/rhiza-logo.svg

# Override template default: include mkdocstrings plugin for API docs
MKDOCS_EXTRA_PACKAGES = --with 'mkdocstrings[python]'

# Lock the coverage gate at 100% (src/ is fully covered). Set here in the
# repo-owned Makefile (not the non-committed local.mk) so a regression below
# 100% fails `make test` for everyone. Beats the template's `?= 90` default
# because this assignment precedes the `include` below.
COVERAGE_FAIL_UNDER = 100

# Always include the Rhiza API (template-managed)
include .rhiza/rhiza.mk

# Optional: developer-local extensions (not committed)
-include local.mk
