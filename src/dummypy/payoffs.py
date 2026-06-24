"""Payoff functions for vanilla European option contracts."""

import numpy as np
import numpy.typing as npt


def call_payoff(spot: npt.ArrayLike, strike: float) -> npt.NDArray[np.float64]:
    """Return the expiry payoff of a European call option.

    Args:
        spot: Underlying spot price(s) at expiry. Scalars and array-likes
            are both accepted.
        strike: Strike price of the option.

    Returns:
        Element-wise payoff ``max(spot - strike, 0)`` as a float array.
    """
    return np.maximum(np.asarray(spot, dtype=np.float64) - strike, 0.0)


def put_payoff(spot: npt.ArrayLike, strike: float) -> npt.NDArray[np.float64]:
    """Return the expiry payoff of a European put option.

    Args:
        spot: Underlying spot price(s) at expiry. Scalars and array-likes
            are both accepted.
        strike: Strike price of the option.

    Returns:
        Element-wise payoff ``max(strike - spot, 0)`` as a float array.
    """
    return np.maximum(strike - np.asarray(spot, dtype=np.float64), 0.0)
