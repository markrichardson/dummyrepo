"""The rhiza conformance checks, re-exported from the ``pytest-rhiza`` plugin.

These checks assert about *the repository* — that the README's fenced examples run,
that ``pyproject.toml`` carries the fields and the bump-my-version config the release
flow needs, that the newest tag matches the declared version, that every module carries
docstrings. They used to arrive as seven files copied into ``.rhiza/tests/`` by the
template sync, which meant every managed repo carried a frozen copy that aged
independently of the template it validates (jebel-quant/rhiza#1540).

They now arrive as an ordinary PyPI dependency, ``pytest-rhiza``, declared in the
``test`` dependency group. The plugin contributes the ``root``, ``logger`` and
``latest_tag`` fixtures through its ``pytest11`` entry point, so nothing here needs a
``conftest.py``.

The checks themselves are tests, which an entry point cannot contribute — pytest would
only find them via ``--pyargs``, and this repo's ``pytest.ini`` (template-owned) sets
``testpaths = tests``. So each module beside this one star-imports one check module into
a file pytest does collect; star-imported rather than named one by one so a check added
in a later ``pytest-rhiza`` release arrives with the version bump alone. That is
deliberately more coverage than the copied folder had: the reusable CI workflow runs
``make test`` but never ``make rhiza-test``, so the synced suite only ever ran on a
developer's ``make all``.
"""
