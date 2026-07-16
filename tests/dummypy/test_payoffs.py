"""Unit tests for the vanilla option payoff functions.

``payoffs`` exposes plain functions (no classes), so these tests are plain
``test_*`` functions to keep the test layout mirroring the source 1:1.
"""

import math

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from dummypy import call_payoff, put_payoff

# Finite, non-negative strikes/spots for property-based tests.
_prices = st.floats(min_value=0.0, max_value=1e6, allow_nan=False, allow_infinity=False)


def test_call_in_the_money():
    """Call pays spot minus strike when in the money."""
    assert call_payoff(120.0, 100.0) == pytest.approx(20.0)


def test_call_out_of_the_money_floors_at_zero():
    """Call payoff never goes negative."""
    assert call_payoff(80.0, 100.0) == pytest.approx(0.0)


def test_call_at_the_money():
    """Call is worthless at the strike."""
    assert call_payoff(100.0, 100.0) == pytest.approx(0.0)


def test_call_vectorized():
    """Call payoff is computed element-wise over an array of spots."""
    result = call_payoff([80.0, 100.0, 130.0], 100.0)
    np.testing.assert_allclose(result, [0.0, 0.0, 30.0])


def test_call_returns_float_array():
    """Integer inputs are promoted to a float array."""
    result = call_payoff([120, 90], 100)
    assert result.dtype == np.float64


def test_put_in_the_money():
    """Put pays strike minus spot when in the money."""
    assert put_payoff(80.0, 100.0) == pytest.approx(20.0)


def test_put_out_of_the_money_floors_at_zero():
    """Put payoff never goes negative."""
    assert put_payoff(120.0, 100.0) == pytest.approx(0.0)


def test_put_at_the_money():
    """Put is worthless at the strike."""
    assert put_payoff(100.0, 100.0) == pytest.approx(0.0)


def test_put_vectorized():
    """Put payoff is computed element-wise over an array of spots."""
    result = put_payoff([70.0, 100.0, 130.0], 100.0)
    np.testing.assert_allclose(result, [30.0, 0.0, 0.0])


def test_put_call_parity_at_expiry():
    """Call - put = spot - strike for every spot at expiry."""
    spots = [60.0, 100.0, 140.0]
    strike = 100.0
    parity = call_payoff(spots, strike) - put_payoff(spots, strike)
    np.testing.assert_allclose(parity, np.asarray(spots) - strike)


# --- Strike validation -------------------------------------------------------


def test_call_negative_strike_raises():
    """A negative strike is rejected with a clear ValueError."""
    with pytest.raises(ValueError, match="non-negative"):
        call_payoff(100.0, -1.0)


def test_put_negative_strike_raises():
    """A negative strike is rejected with a clear ValueError."""
    with pytest.raises(ValueError, match="non-negative"):
        put_payoff(100.0, -1.0)


def test_call_nan_strike_raises():
    """A NaN strike is rejected with a clear ValueError."""
    with pytest.raises(ValueError, match="NaN"):
        call_payoff(100.0, math.nan)


def test_put_nan_strike_raises():
    """A NaN strike is rejected with a clear ValueError."""
    with pytest.raises(ValueError, match="NaN"):
        put_payoff(100.0, math.nan)


# --- Property-based invariants -----------------------------------------------


@given(spot=_prices, strike=_prices)
def test_call_payoff_is_non_negative(spot, strike):
    """A call payoff is never negative for any valid spot/strike."""
    assert call_payoff(spot, strike) >= 0.0


@given(spot=_prices, strike=_prices)
def test_put_payoff_is_non_negative(spot, strike):
    """A put payoff is never negative for any valid spot/strike."""
    assert put_payoff(spot, strike) >= 0.0


@given(spot_low=_prices, delta=_prices, strike=_prices)
def test_call_payoff_non_decreasing_in_spot(spot_low, delta, strike):
    """Raising the spot never lowers the call payoff (monotone non-decreasing)."""
    assert call_payoff(spot_low + delta, strike) >= call_payoff(spot_low, strike)


@given(spot_low=_prices, delta=_prices, strike=_prices)
def test_put_payoff_non_increasing_in_spot(spot_low, delta, strike):
    """Raising the spot never raises the put payoff (monotone non-increasing)."""
    assert put_payoff(spot_low + delta, strike) <= put_payoff(spot_low, strike)
