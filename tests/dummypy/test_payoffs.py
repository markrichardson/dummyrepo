"""Unit tests for the vanilla option payoff functions.

``payoffs`` exposes plain functions (no classes), so these tests are plain
``test_*`` functions to keep the test layout mirroring the source 1:1.
"""

import numpy as np
import pytest

from dummypy import call_payoff, put_payoff


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
