"""Payoff functions for vanilla European option contracts."""

import math

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
        ValueError: If ``strike`` is not finite (NaN or infinite), or is
            negative.
    """
    if not math.isfinite(strike):
        msg = f"strike must be a finite real number, got {strike}"
        raise ValueError(msg)
    if strike < 0:
        msg = f"strike must be non-negative, got {strike}"
        raise ValueError(msg)


def call_payoff(spot: npt.ArrayLike, strike: float) -> np.float64 | npt.NDArray[np.float64]:
    """Return the expiry payoff of a European call option.

    The return type follows :func:`numpy.maximum`, which this delegates to: a
    scalar ``spot`` yields a :class:`numpy.float64`, an array-like yields an
    array. The two are deliberately *not* normalised to an array — doing so
    would make ``call_payoff(120.0, 100.0)`` return ``array([20.])`` and
    surprise every caller who passed a single number.

    Args:
        spot: Underlying spot price(s) at expiry. Scalars and array-likes
            are both accepted.
        strike: Strike price of the option. Must be a finite, non-negative
            real number.

    Returns:
        Element-wise payoff ``max(spot - strike, 0)``: a :class:`numpy.float64`
        for scalar ``spot``, or a ``float64`` array for array-like ``spot``.

    Raises:
        ValueError: If ``strike`` is not finite (NaN or infinite), or is
            negative.

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
    return np.maximum(np.asarray(spot, dtype=np.float64) - strike, 0.0)


def put_payoff(spot: npt.ArrayLike, strike: float) -> np.float64 | npt.NDArray[np.float64]:
    """Return the expiry payoff of a European put option.

    Mirrors :func:`call_payoff`, including its return-type convention: scalar in,
    scalar out; array-like in, array out.

    Args:
        spot: Underlying spot price(s) at expiry. Scalars and array-likes
            are both accepted.
        strike: Strike price of the option. Must be a finite, non-negative
            real number.

    Returns:
        Element-wise payoff ``max(strike - spot, 0)``: a :class:`numpy.float64`
        for scalar ``spot``, or a ``float64`` array for array-like ``spot``.

    Raises:
        ValueError: If ``strike`` is not finite (NaN or infinite), or is
            negative.

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

        A non-finite strike is rejected alongside a negative one:

        >>> put_payoff(80.0, strike=float("nan"))
        Traceback (most recent call last):
            ...
        ValueError: strike must be a finite real number, got nan
    """
    _check_strike(strike)
    return np.maximum(strike - np.asarray(spot, dtype=np.float64), 0.0)
