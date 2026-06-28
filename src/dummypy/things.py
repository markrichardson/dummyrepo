"""Core data structures for the dummypy analytics library."""

import attrs
import numpy as np
import pandas as pd


def _check_n(_instance: object, _attribute: "attrs.Attribute[int]", value: object) -> None:
    """Reject non-integer or negative grid sizes with a clear error.

    Args:
        _instance: The Grid instance being validated (unused).
        _attribute: The attrs attribute being validated (unused).
        value: The proposed value for ``n``.

    Raises:
        TypeError: If ``value`` is not an integer (bool is rejected too).
        ValueError: If ``value`` is negative.
    """
    # bool is a subclass of int; reject it to avoid Grid(n=True) surprises.
    if not isinstance(value, int) or isinstance(value, bool):
        msg = f"Grid size n must be an integer, got {type(value).__name__}"
        raise TypeError(msg)
    if value < 0:
        msg = f"Grid size n must be non-negative, got {value}"
        raise ValueError(msg)


@attrs.define
class Grid:
    """A grid representing data points for analytics calculations.

    Creates two DataFrames (x and y) with goal-like structure for data analysis.

    Args:
        n: Maximum size for the grid (default: 10). Must be a non-negative
            integer.

    Raises:
        TypeError: If ``n`` is not an integer (e.g. a float or a bool).
        ValueError: If ``n`` is negative.
    """

    n: int = attrs.field(init=True, repr=True, default=10, validator=_check_n)
    x: pd.DataFrame = attrs.field(repr=False, init=False)
    y: pd.DataFrame = attrs.field(repr=False, init=False)

    def __attrs_post_init__(self) -> None:
        """Initialize the x and y data matrices after object creation."""
        nn = np.arange(self.n + 1)
        cols = [str(n) for n in nn]
        data = np.tile(nn, (self.n + 1, 1))
        self.y = pd.DataFrame(data, index=pd.Index(cols), columns=pd.Index(cols))
        self.x = self.y.T

    def diff(self) -> pd.DataFrame:
        """Returns a grid of differences.

        Returns:
            DataFrame of element-wise differences (x - y).
        """
        return self.x - self.y
