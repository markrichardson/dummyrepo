"""DummyPy Analytics Library - A demonstration package for data analytics."""

from .payoffs import call_payoff, put_payoff
from .things import Grid

__all__ = ["Grid", "call_payoff", "put_payoff"]
