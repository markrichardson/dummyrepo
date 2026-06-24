"""Unit tests for the vanilla option payoff functions."""

import numpy as np
import pytest

from dummypy import call_payoff, put_payoff


class TestCallPayoff:
    """Tests for :func:`dummypy.call_payoff`."""

    def test_in_the_money(self):
        """Call pays spot minus strike when in the money."""
        assert call_payoff(120.0, 100.0) == pytest.approx(20.0)

    def test_out_of_the_money_floors_at_zero(self):
        """Call payoff never goes negative."""
        assert call_payoff(80.0, 100.0) == pytest.approx(0.0)

    def test_at_the_money(self):
        """Call is worthless at the strike."""
        assert call_payoff(100.0, 100.0) == pytest.approx(0.0)

    def test_vectorized(self):
        """Call payoff is computed element-wise over an array of spots."""
        result = call_payoff([80.0, 100.0, 130.0], 100.0)
        np.testing.assert_allclose(result, [0.0, 0.0, 30.0])

    def test_returns_float_array(self):
        """Integer inputs are promoted to a float array."""
        result = call_payoff([120, 90], 100)
        assert result.dtype == np.float64


class TestPutPayoff:
    """Tests for :func:`dummypy.put_payoff`."""

    def test_in_the_money(self):
        """Put pays strike minus spot when in the money."""
        assert put_payoff(80.0, 100.0) == pytest.approx(20.0)

    def test_out_of_the_money_floors_at_zero(self):
        """Put payoff never goes negative."""
        assert put_payoff(120.0, 100.0) == pytest.approx(0.0)

    def test_at_the_money(self):
        """Put is worthless at the strike."""
        assert put_payoff(100.0, 100.0) == pytest.approx(0.0)

    def test_vectorized(self):
        """Put payoff is computed element-wise over an array of spots."""
        result = put_payoff([70.0, 100.0, 130.0], 100.0)
        np.testing.assert_allclose(result, [30.0, 0.0, 0.0])


def test_put_call_parity_at_expiry():
    """Call - put = spot - strike for every spot at expiry."""
    spots = [60.0, 100.0, 140.0]
    strike = 100.0
    parity = call_payoff(spots, strike) - put_payoff(spots, strike)
    np.testing.assert_allclose(parity, np.asarray(spots) - strike)
