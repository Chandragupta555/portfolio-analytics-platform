from typing import Dict
import pandas as pd


def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate simple daily percentage returns for each asset column.

    Formula: R_t = (P_t - P_{t-1}) / P_{t-1}
    Initial NaN values from price change calculation are dropped.
    """
    return prices.pct_change().dropna()


def cumulative_returns(daily_rets: pd.DataFrame) -> pd.DataFrame:
    """Calculate cumulative returns over time for each asset column.

    Formula: CR_t = \\prod_{i=1}^t (1 + R_i) - 1
    """
    return (1.0 + daily_rets).cumprod() - 1.0


def portfolio_returns(
    daily_rets: pd.DataFrame, weights: Dict[str, float]
) -> pd.Series:
    """Calculate the weighted portfolio daily return series.

    Formula: R_{p,t} = \\sum_{i} w_i \\cdot R_{i,t}
    Raises ValueError if tickers in daily_rets columns and weights keys do not match.
    """
    ret_cols = set(daily_rets.columns)
    weight_keys = set(weights.keys())

    if ret_cols != weight_keys:
        missing_in_weights = ret_cols - weight_keys
        missing_in_rets = weight_keys - ret_cols
        msg = "Mismatch between daily_rets columns and weights keys."
        if missing_in_weights:
            msg += f" Missing in weights: {missing_in_weights}."
        if missing_in_rets:
            msg += f" Missing in daily_rets: {missing_in_rets}."
        raise ValueError(msg)

    weight_series = pd.Series({col: weights[col] for col in daily_rets.columns})
    portfolio_ret = daily_rets.dot(weight_series)
    portfolio_ret.name = "portfolio_return"
    return portfolio_ret
