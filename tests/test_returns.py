import pandas as pd
import pytest

from src.analytics.returns import cumulative_returns, daily_returns, portfolio_returns


def test_daily_returns_known_values() -> None:
    prices = pd.DataFrame(
        {"AAPL": [100.0, 110.0, 99.0]},
        index=pd.date_range("2023-01-01", periods=3, freq="D"),
    )
    rets = daily_returns(prices)

    assert len(rets) == 2
    assert list(rets.columns) == ["AAPL"]
    assert rets.loc[rets.index[0], "AAPL"] == pytest.approx(0.10)
    assert rets.loc[rets.index[1], "AAPL"] == pytest.approx(-0.10)


def test_daily_returns_multi_ticker() -> None:
    prices = pd.DataFrame(
        {
            "AAPL": [100.0, 105.0],
            "MSFT": [200.0, 190.0],
        },
        index=pd.date_range("2023-01-01", periods=2, freq="D"),
    )
    rets = daily_returns(prices)

    assert len(rets) == 1
    assert rets.loc[rets.index[0], "AAPL"] == pytest.approx(0.05)
    assert rets.loc[rets.index[0], "MSFT"] == pytest.approx(-0.05)


def test_daily_returns_single_row_edge_case() -> None:
    prices = pd.DataFrame(
        {"AAPL": [100.0]},
        index=pd.date_range("2023-01-01", periods=1, freq="D"),
    )
    rets = daily_returns(prices)

    assert isinstance(rets, pd.DataFrame)
    assert len(rets) == 0
    assert list(rets.columns) == ["AAPL"]


def test_cumulative_returns_compounding() -> None:
    daily_rets = pd.DataFrame(
        {"AAPL": [0.10, -0.10]},
        index=pd.date_range("2023-01-02", periods=2, freq="D"),
    )
    cum_rets = cumulative_returns(daily_rets)

    assert len(cum_rets) == 2
    assert cum_rets.iloc[0]["AAPL"] == pytest.approx(0.10)
    assert cum_rets.iloc[1]["AAPL"] == pytest.approx(-0.01)


def test_portfolio_returns_two_tickers() -> None:
    daily_rets = pd.DataFrame(
        {
            "AAPL": [0.10, 0.05],
            "MSFT": [0.02, -0.04],
        },
        index=pd.date_range("2023-01-02", periods=2, freq="D"),
    )
    weights = {"AAPL": 0.6, "MSFT": 0.4}

    port_rets = portfolio_returns(daily_rets, weights)

    assert isinstance(port_rets, pd.Series)
    assert len(port_rets) == 2
    assert port_rets.iloc[0] == pytest.approx(0.068)
    assert port_rets.iloc[1] == pytest.approx(0.014)


def test_portfolio_returns_raises_on_mismatched_tickers() -> None:
    daily_rets = pd.DataFrame(
        {"AAPL": [0.01, 0.02], "MSFT": [0.03, 0.04]},
        index=pd.date_range("2023-01-02", periods=2, freq="D"),
    )

    with pytest.raises(
        ValueError, match="Mismatch between daily_rets columns and weights keys"
    ):
        portfolio_returns(daily_rets, {"AAPL": 1.0})

    with pytest.raises(
        ValueError, match="Mismatch between daily_rets columns and weights keys"
    ):
        portfolio_returns(daily_rets, {"AAPL": 0.5, "MSFT": 0.5, "GOOGL": 0.0})
