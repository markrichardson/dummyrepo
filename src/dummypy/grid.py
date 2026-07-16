"""The :class:`Grid` value type for the dummypy analytics library.

Responsibility split:

- :func:`_build_grids` owns the *data-generation* concern — turning a size
  ``n`` into the two coordinate DataFrames. It is a pure function of ``n``.
- :class:`Grid` owns the *model* concern — validating ``n``, holding the
  generated ``x``/``y`` frames, and exposing behaviour (:meth:`Grid.diff`).

Keeping generation in a standalone function keeps ``Grid`` a thin, testable
value type rather than a class that both stores and manufactures its data.
"""

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


def _build_grids(n: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build the ``(x, y)`` coordinate frames for a grid of size ``n``.

    This is the data-generation concern, kept separate from the :class:`Grid`
    model. ``y`` has each row equal to ``0..n``; ``x`` is its transpose. Both
    are square with side ``n + 1`` and share string coordinate labels.

    Args:
        n: Non-negative grid size (already validated by the caller).

    Returns:
        An ``(x, y)`` tuple of DataFrames, where ``x == y.T``.
    """
    nn = np.arange(n + 1)
    cols = [str(i) for i in nn]
    data = np.tile(nn, (n + 1, 1))
    y = pd.DataFrame(data, index=pd.Index(cols), columns=pd.Index(cols))
    return y.T, y


@attrs.define
class Grid:
    """A grid representing data points for analytics calculations.

    Holds two coordinate DataFrames, ``x`` and ``y`` (with ``x == y.T``),
    generated from the grid size ``n`` by :func:`_build_grids`.

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
        """Populate the x and y coordinate frames from ``n``."""
        self.x, self.y = _build_grids(self.n)

    def diff(self) -> pd.DataFrame:
        """Returns a grid of differences.

        Returns:
            A fresh DataFrame of element-wise differences (x - y), computed
            anew on each call.
        """
        return self.x - self.y
