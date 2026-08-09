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


def call_payoff(spot: npt.ArrayLike, strike: float) -> npt.NDArray[np.float64]:
    """Return the expiry payoff of a European call option.

    Args:
        spot: Underlying spot price(s) at expiry. Scalars and array-likes
            are both accepted.
        strike: Strike price of the option. Must be a finite, non-negative
            real number.

    Returns:
        Element-wise payoff ``max(spot - strike, 0)`` as a float array.

    Raises:
        ValueError: If ``strike`` is not finite (NaN or infinite), or is
            negative.
    """
    _check_strike(strike)
    return np.maximum(np.asarray(spot, dtype=np.float64) - strike, 0.0)


def put_payoff(spot: npt.ArrayLike, strike: float) -> npt.NDArray[np.float64]:
    """Return the expiry payoff of a European put option.

    Args:
        spot: Underlying spot price(s) at expiry. Scalars and array-likes
            are both accepted.
        strike: Strike price of the option. Must be a finite, non-negative
            real number.

    Returns:
        Element-wise payoff ``max(strike - spot, 0)`` as a float array.

    Raises:
        ValueError: If ``strike`` is not finite (NaN or infinite), or is
            negative.
    """
    _check_strike(strike)
    return np.maximum(strike - np.asarray(spot, dtype=np.float64), 0.0)
