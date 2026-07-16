"""DummyPy Analytics Library - A demonstration package for data analytics."""

from importlib.metadata import PackageNotFoundError, version

from .grid import Grid
from .payoffs import call_payoff, put_payoff

try:
    __version__ = version("dummypy")
except PackageNotFoundError:  # pragma: no cover - package not installed
    __version__ = "0.0.0"

__all__ = ["Grid", "__version__", "call_payoff", "put_payoff"]
