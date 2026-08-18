"""git tag reachability and version agreement, from ``pytest_rhiza.checks.test_release_tags``.

Star-imported rather than named one by one: pytest collects the ``test_*`` functions
and ``Test*`` classes this pulls into the module namespace, and a check added in a
later ``pytest-rhiza`` release then arrives with the version bump alone. See
``tests/rhiza/__init__.py`` for why the re-export exists at all.
"""

from pytest_rhiza.checks.test_release_tags import *  # noqa: F403
