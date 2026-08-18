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


@attrs.frozen
class Grid:
    """A grid representing data points for analytics calculations.

    Holds two coordinate DataFrames, ``x`` and ``y`` (with ``x == y.T``),
    generated from the grid size ``n`` by :func:`_build_grids`.

    Instances are **immutable**. ``x`` and ``y`` are derived from ``n``, so
    letting any of the three be reassigned would break the invariants the
    validator and :func:`_build_grids` establish at construction: a new ``x``
    need not be ``y.T``, and a new ``n`` would not rebuild the frames it is
    supposed to describe. Build a new :class:`Grid` instead.

    Args:
        n: Maximum size for the grid (default: 10). Must be a non-negative
            integer.

    Raises:
        TypeError: If ``n`` is not an integer (e.g. a float or a bool).
        ValueError: If ``n`` is negative.

    Examples:
        Both frames are square with side ``n + 1``, and ``x`` is the transpose
        of ``y``:

        >>> grid = Grid(n=3)
        >>> grid.x.shape
        (4, 4)
        >>> bool((grid.x == grid.y.T).all().all())
        True

        Only ``n`` is part of the repr, since ``x`` and ``y`` are derived:

        >>> grid
        Grid(n=3)

        A negative size is rejected, and so is a float or a bool:

        >>> Grid(n=-1)
        Traceback (most recent call last):
            ...
        ValueError: Grid size n must be non-negative, got -1

        >>> Grid(n=2.0)
        Traceback (most recent call last):
            ...
        TypeError: Grid size n must be an integer, got float

        Instances are immutable — build a new grid rather than reassigning:

        >>> grid.n = 5
        Traceback (most recent call last):
            ...
        attr.exceptions.FrozenInstanceError
    """

    n: int = attrs.field(init=True, repr=True, default=10, validator=_check_n)
    x: pd.DataFrame = attrs.field(repr=False, init=False)
    y: pd.DataFrame = attrs.field(repr=False, init=False)

    def __attrs_post_init__(self) -> None:
        """Populate the x and y coordinate frames from ``n``.

        Uses :func:`object.__setattr__` because the class is frozen — the
        standard attrs idiom for a derived attribute on an immutable class.
        Keeping the single :func:`_build_grids` call here preserves the
        generation-vs-model split described in the module docstring.
        """
        x, y = _build_grids(self.n)
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)

    def diff(self) -> pd.DataFrame:
        """Returns a grid of differences.

        Returns:
            A fresh DataFrame of element-wise differences (x - y), computed
            anew on each call.

        Examples:
            The value at ``(i, j)`` is ``i - j``, so the frame is antisymmetric
            and its diagonal is zero:

            >>> grid = Grid(n=3)
            >>> grid.diff().loc["2", "1"]
            np.int64(1)
            >>> grid.diff().loc["1", "2"]
            np.int64(-1)

            Each call returns a fresh frame, so mutating one cannot corrupt the
            grid it came from:

            >>> grid.diff() is grid.diff()
            False
        """
        return self.x - self.y
