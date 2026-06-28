"""Tests for the importable package version."""

from importlib.metadata import version

import dummypy


def test_version_is_exposed():
    """``dummypy.__version__`` is a non-empty string."""
    assert isinstance(dummypy.__version__, str)
    assert dummypy.__version__


def test_version_matches_installed_metadata():
    """``dummypy.__version__`` matches the installed package metadata."""
    assert dummypy.__version__ == version("dummypy")
