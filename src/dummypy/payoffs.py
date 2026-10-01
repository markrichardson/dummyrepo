"""Payoff functions for vanilla European option contracts."""

import math
import numbers

import numpy as np
import numpy.typing as npt


def _check_strike(strike: float) -> None:
    """Reject a nonsensical strike with a clear error.

    Mirrors the validation style of :func:`dummypy.grid._check_n`: fail fast
    with an actionable message rather than silently producing a meaningless
    payoff. Infinities are rejected alongside NaN: an unchecked infinite
    strike does not fail, it silently yields an infinite put payoff, which
    is exactly the meaningless result this validator exists to prevent.

    Args:
        strike: The proposed strike price.

    Raises:
        TypeError: If ``strike`` is not a real number (bool is rejected too).
        ValueError: If ``strike`` is not finite (NaN or infinite), or is
            negative.
    """
    # bool is a subclass of int; reject it as _check_n does, rather than
    # silently pricing a strike of 1.0.
    if not isinstance(strike, numbers.Real) or isinstance(strike, bool):
        msg = f"strike must be a real number, got {type(strike).__name__}"
        raise TypeError(msg)
    if not math.isfinite(strike):
        msg = f"strike must be a finite real number, got {strike}"
        raise ValueError(msg)
    if strike < 0:
        msg = f"strike must be non-negative, got {strike}"
        raise ValueError(msg)


def _as_spot(spot: npt.ArrayLike) -> npt.NDArray[np.float64]:
    """Convert ``spot`` to a float64 array, rejecting unusable prices.

    The counterpart of :func:`_check_strike` for the other argument, with one
    deliberate difference: NaN is *not* rejected. ``spot`` is routinely an
    array, and a missing price in one entry should yield a NaN payoff in that
    entry rather than refuse the whole batch -- which is also what numpy does
    with it anyway. ``+inf`` is allowed for the same reason, and gives the
    limiting payoffs (``inf`` for a call, ``0`` for a put).

    Args:
        spot: The proposed spot price(s), scalar or array-like.

    Returns:
        ``spot`` as a ``float64`` array (0-d for a scalar).

    Raises:
        TypeError: If ``spot`` is not real-valued -- a bool, a string (even a
            numeric one, as for ``strike``), a complex number, ``None``, or a
            ragged nested sequence.
        ValueError: If any entry of ``spot`` is negative, ``-inf`` included.
    """
    try:
        raw = np.asarray(spot)
    except ValueError:  # a ragged nested sequence
        raw = None
    # Integer and float kinds only: the same set _check_strike admits.
    if raw is None or raw.dtype.kind not in "iuf":
        msg = f"spot must be real-valued, got {type(spot).__name__}"
        raise TypeError(msg)
    values = raw.astype(np.float64, copy=False)
    # NaN compares False here, so it passes through by design (see above).
    if np.any(values < 0):
        # Name the first offender rather than echoing the input, which may be
        # an array of any size.
        index = np.argwhere(values < 0)[0]
        where = "" if values.ndim == 0 else f" at index {', '.join(map(str, index))}"
        msg = f"spot must be non-negative, got {values[tuple(index)]}{where}"
        raise ValueError(msg)
    return values


def call_payoff(spot: npt.ArrayLike, strike: float) -> np.float64 | npt.NDArray[np.float64]:
    """Return the expiry payoff of a European call option.

    The return type follows :func:`numpy.maximum`, which this delegates to: a
    scalar ``spot`` yields a :class:`numpy.float64`, an array-like yields an
    array. The two are deliberately *not* normalised to an array — doing so
    would make ``call_payoff(120.0, 100.0)`` return ``array([20.])`` and
    surprise every caller who passed a single number.

    Args:
        spot: Underlying spot price(s) at expiry. Scalars and array-likes
            are both accepted. Must be non-negative; a NaN entry is allowed
            and yields a NaN payoff in that position.
        strike: Strike price of the option. Must be a finite, non-negative
            real number.

    Returns:
        Element-wise payoff ``max(spot - strike, 0)``: a :class:`numpy.float64`
        for scalar ``spot``, or a ``float64`` array for array-like ``spot``.

    Raises:
        TypeError: If ``strike`` is not a real number (e.g. a bool or a str),
            or ``spot`` is not real-valued.
        ValueError: If ``strike`` is not finite (NaN or infinite), or is
            negative, or if any entry of ``spot`` is negative.

    Examples:
        A scalar spot gives a scalar payoff:

        >>> call_payoff(120.0, strike=100.0)
        np.float64(20.0)

        Out of the money the payoff floors at zero rather than going negative:

        >>> call_payoff(80.0, strike=100.0)
        np.float64(0.0)

        An array-like spot is evaluated element-wise:

        >>> call_payoff([80.0, 100.0, 130.0], strike=100.0)
        array([ 0.,  0., 30.])

        An unusable strike fails fast:

        >>> call_payoff(120.0, strike=-1.0)
        Traceback (most recent call last):
            ...
        ValueError: strike must be non-negative, got -1.0
    """
    _check_strike(strike)
    return np.maximum(_as_spot(spot) - strike, 0.0)


def put_payoff(spot: npt.ArrayLike, strike: float) -> np.float64 | npt.NDArray[np.float64]:
    """Return the expiry payoff of a European put option.

    Mirrors :func:`call_payoff`, including its return-type convention: scalar in,
    scalar out; array-like in, array out.

    Args:
        spot: Underlying spot price(s) at expiry. Scalars and array-likes
            are both accepted. Must be non-negative; a NaN entry is allowed
            and yields a NaN payoff in that position.
        strike: Strike price of the option. Must be a finite, non-negative
            real number.

    Returns:
        Element-wise payoff ``max(strike - spot, 0)``: a :class:`numpy.float64`
        for scalar ``spot``, or a ``float64`` array for array-like ``spot``.

    Raises:
        TypeError: If ``strike`` is not a real number (e.g. a bool or a str),
            or ``spot`` is not real-valued.
        ValueError: If ``strike`` is not finite (NaN or infinite), or is
            negative, or if any entry of ``spot`` is negative.

    Examples:
        A scalar spot gives a scalar payoff:

        >>> put_payoff(80.0, strike=100.0)
        np.float64(20.0)

        Out of the money the payoff floors at zero:

        >>> put_payoff(120.0, strike=100.0)
        np.float64(0.0)

        An array-like spot is evaluated element-wise:

        >>> put_payoff([70.0, 100.0, 130.0], strike=100.0)
        array([30.,  0.,  0.])

        A missing spot propagates as NaN rather than rejecting the batch:

        >>> put_payoff([70.0, float("nan")], strike=100.0)
        array([30., nan])

        A non-finite strike is rejected alongside a negative one:

        >>> put_payoff(80.0, strike=float("nan"))
        Traceback (most recent call last):
            ...
        ValueError: strike must be a finite real number, got nan
    """
    _check_strike(strike)
    return np.maximum(strike - _as_spot(spot), 0.0)
