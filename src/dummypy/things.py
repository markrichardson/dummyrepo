"""Core data structures for the dummypy analytics library."""

import attrs
import numpy as np
import pandas as pd


@attrs.define
class Grid:
    """A grid representing data points for analytics calculations.

    Creates two DataFrames (x and y) with goal-like structure for data analysis.

    Args:
        n: Maximum size for the grid (default: 10)
    """

    n: int = attrs.field(init=True, repr=True, default=10)
    x: pd.DataFrame = attrs.field(repr=False, init=False)
    y: pd.DataFrame = attrs.field(repr=False, init=False)

    def __attrs_post_init__(self) -> None:
        """Initialize the x and y data matrices after object creation."""
        nn = np.arange(self.n + 1)
        cols = [str(n) for n in nn]
        data = np.tile(nn, (self.n + 1, 1))
        self.y = pd.DataFrame(data, index=cols, columns=cols)
        self.x = self.y.T

    def diff(self) -> pd.DataFrame:
        """Returns a grid of differences."""
        return self.x - self.y
