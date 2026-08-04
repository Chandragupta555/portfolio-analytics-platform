import math
import pandas as pd
import pytest

from src.analytics.risk import (
    correlation_matrix,
    max_drawdown,
    sharpe_ratio,
    volatility,
)


# ---------------------------------------------------------------------------
# volatility
# ---------------------------------------------------------------------------
def test_volatility_known_values() -> None:
    """Hand-calculated annualized volatility for [0.01, -0.01, 0.02, -0.02].

    Sample std (ddof=1):
        mean = (0.01 + (-0.01) + 0.02 + (-0.02)) / 4 = 0.0
        sum_sq = 0.01^2 + 0.01^2 + 0.02^2 + 0.02^2 = 0.001
        var = 0.001 / (4 - 1) = 0.001 / 3
        std = sqrt(0.001 / 3) = sqrt(1/3000)

    Annualized = std * sqrt(252)
    """
    rets = pd.Series([0.01, -0.01, 0.02, -0.02])

    expected_daily_std = math.sqrt(0.001 / 3)
    expected_annual = expected_daily_std * math.sqrt(252)

    assert volatility(rets, annualize=False) == pytest.approx(expected_daily_std)
    assert volatility(rets, annualize=True) == pytest.approx(expected_annual)


# ---------------------------------------------------------------------------
# sharpe_ratio
# ---------------------------------------------------------------------------
def test_sharpe_ratio_known_values() -> None:
    """Hand-calculated Sharpe for [0.01, -0.01, 0.02, -0.02] with rf=0.02.

    daily_rf = (1.02)^(1/252) - 1
    excess  = [0.01 - daily_rf, -0.01 - daily_rf, 0.02 - daily_rf, -0.02 - daily_rf]
    mean(excess) = mean(rets) - daily_rf = 0.0 - daily_rf = -daily_rf
    std(rets, ddof=1) = sqrt(0.001/3)   (from volatility test above)
    sharpe_daily = -daily_rf / sqrt(0.001/3)
    sharpe_annual = sharpe_daily * sqrt(252)
    """
    rets = pd.Series([0.01, -0.01, 0.02, -0.02])
    rf = 0.02

    # Compound-correct daily risk-free rate
    daily_rf = (1.0 + rf) ** (1.0 / 252) - 1.0

    daily_std = math.sqrt(0.001 / 3)
    expected_sharpe_daily = -daily_rf / daily_std
    expected_sharpe_annual = expected_sharpe_daily * math.sqrt(252)

    assert sharpe_ratio(rets, risk_free_rate=rf, annualize=False) == pytest.approx(
        expected_sharpe_daily
    )
    assert sharpe_ratio(rets, risk_free_rate=rf, annualize=True) == pytest.approx(
        expected_sharpe_annual
    )


def test_sharpe_ratio_zero_volatility() -> None:
    """Constant returns => zero volatility => should return 0.0, not crash."""
    rets = pd.Series([0.01, 0.01, 0.01, 0.01])
    result = sharpe_ratio(rets, risk_free_rate=0.02)
    assert result == 0.0


# ---------------------------------------------------------------------------
# max_drawdown
# ---------------------------------------------------------------------------
def test_max_drawdown_known_path() -> None:
    """Construct a path: +10%, +5%, -20%, +3%.

    wealth: 1.10, 1.155, 0.924, 0.95172
    peak:   1.10, 1.155, 1.155, 1.155
    dd:     0.0,  0.0,   (0.924-1.155)/1.155, (0.95172-1.155)/1.155
                          = -0.2 ,               = -0.17600...

    Max drawdown = -0.2
    """
    rets = pd.Series([0.10, 0.05, -0.20, 0.03])

    # wealth[2] = 1.10 * 1.05 * 0.80 = 0.924
    # peak[2]   = 1.155
    # dd[2]     = (0.924 - 1.155) / 1.155 = -0.231 / 1.155 = -0.2
    expected = -0.2

    assert max_drawdown(rets) == pytest.approx(expected)


# ---------------------------------------------------------------------------
# correlation_matrix
# ---------------------------------------------------------------------------
def test_correlation_perfect_positive() -> None:
    """Identical return series should have correlation 1.0."""
    rets = pd.DataFrame(
        {"A": [0.01, -0.02, 0.03, -0.01], "B": [0.01, -0.02, 0.03, -0.01]}
    )
    corr = correlation_matrix(rets)
    assert corr.loc["A", "B"] == pytest.approx(1.0)
    assert corr.loc["B", "A"] == pytest.approx(1.0)


def test_correlation_perfect_negative() -> None:
    """Perfectly inversely correlated series should have correlation -1.0."""
    rets = pd.DataFrame(
        {"A": [0.01, -0.02, 0.03, -0.01], "B": [-0.01, 0.02, -0.03, 0.01]}
    )
    corr = correlation_matrix(rets)
    assert corr.loc["A", "B"] == pytest.approx(-1.0)
    assert corr.loc["B", "A"] == pytest.approx(-1.0)
    # Diagonal always 1.0
    assert corr.loc["A", "A"] == pytest.approx(1.0)
    assert corr.loc["B", "B"] == pytest.approx(1.0)
