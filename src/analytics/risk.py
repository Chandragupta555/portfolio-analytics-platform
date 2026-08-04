import math
import pandas as pd


# Annualization constant: 252 trading days per year
TRADING_DAYS_PER_YEAR: int = 252


def volatility(daily_rets: pd.Series, annualize: bool = True) -> float:
    """Compute the volatility (standard deviation) of daily returns.

    Uses sample standard deviation (ddof=1), i.e. divides by (n - 1).

    Formula:
        vol_daily = std(daily_rets, ddof=1)
        vol_annual = vol_daily * sqrt(252)   (if annualize=True)

    Args:
        daily_rets: Series of daily returns.
        annualize: If True, scale by sqrt(252) to annualize.

    Returns:
        Volatility as a float.
    """
    # Sample standard deviation (ddof=1): sqrt(sum((r - mean)^2) / (n - 1))
    vol = daily_rets.std(ddof=1)

    if annualize:
        # Annualize: vol_annual = vol_daily * sqrt(trading_days_per_year)
        vol *= math.sqrt(TRADING_DAYS_PER_YEAR)

    return float(vol)


def sharpe_ratio(
    daily_rets: pd.Series,
    risk_free_rate: float = 0.02,
    annualize: bool = True,
) -> float:
    """Compute the Sharpe ratio of daily returns.

    The risk_free_rate is an ANNUAL rate (e.g. 0.02 = 2%). It is converted
    to a daily rate using the compounding-correct formula:
        daily_rf = (1 + annual_rf)^(1/252) - 1

    NOT the common approximation annual_rf / 252.

    Formula:
        excess_daily = daily_rets - daily_rf
        sharpe_daily = mean(excess_daily) / std(daily_rets, ddof=1)
        sharpe_annual = sharpe_daily * sqrt(252)   (if annualize=True)

    Zero-volatility edge case: If std(daily_rets) == 0, returns 0.0 rather
    than allowing division by zero. Rationale: constant returns carry no risk,
    and an infinite Sharpe is misleading; 0.0 signals "not meaningful."

    Args:
        daily_rets: Series of daily returns.
        risk_free_rate: Annual risk-free rate (e.g. 0.02 for 2%).
        annualize: If True, scale by sqrt(252) to annualize.

    Returns:
        Sharpe ratio as a float.
    """
    # Compound-correct daily risk-free rate conversion:
    # daily_rf = (1 + annual_rf)^(1/252) - 1
    daily_rf: float = (1.0 + risk_free_rate) ** (1.0 / TRADING_DAYS_PER_YEAR) - 1.0

    # Daily excess returns
    excess_daily = daily_rets - daily_rf

    # Sample standard deviation of daily returns (ddof=1)
    vol = daily_rets.std(ddof=1)

    # Guard against zero volatility to avoid inf/nan
    if vol == 0.0:
        return 0.0

    # Sharpe = mean(excess) / std(daily_rets, ddof=1)
    sharpe = excess_daily.mean() / vol

    if annualize:
        # Annualize: sharpe_annual = sharpe_daily * sqrt(252)
        sharpe *= math.sqrt(TRADING_DAYS_PER_YEAR)

    return float(sharpe)


def max_drawdown(daily_rets: pd.Series) -> float:
    """Compute the maximum drawdown from a series of daily returns.

    Formula:
        wealth = cumprod(1 + daily_rets)          # cumulative wealth index
        running_peak = cummax(wealth)             # running maximum wealth
        drawdown = (wealth - running_peak) / running_peak   # fractional decline
        max_drawdown = min(drawdown)              # worst peak-to-trough

    Returns a negative number representing the worst peak-to-trough decline.

    Args:
        daily_rets: Series of daily returns.

    Returns:
        Maximum drawdown as a negative float.
    """
    # Cumulative wealth index: W_t = prod(1 + r_i) for i=1..t
    wealth = (1.0 + daily_rets).cumprod()

    # Running peak: max wealth seen up to each point
    running_peak = wealth.cummax()

    # Drawdown at each point: (W_t - peak_t) / peak_t
    drawdown = (wealth - running_peak) / running_peak

    # Most negative drawdown
    return float(drawdown.min())


def correlation_matrix(daily_rets_df: pd.DataFrame) -> pd.DataFrame:
    """Compute the pairwise Pearson correlation matrix of daily returns.

    Uses pandas default Pearson correlation (standard formula).

    Args:
        daily_rets_df: DataFrame with one column per ticker of daily returns.

    Returns:
        DataFrame of pairwise correlations (symmetric, 1.0 on diagonal).
    """
    return daily_rets_df.corr(method="pearson")
