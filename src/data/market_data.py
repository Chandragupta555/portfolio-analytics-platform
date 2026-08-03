import logging
from pathlib import Path
from typing import List, Union
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class MarketDataService:
    def __init__(self, cache_dir: Union[str, Path] = "src/data/cache") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_prices(
        self, tickers: List[str], start_date: str, end_date: str
    ) -> pd.DataFrame:
        if not tickers:
            raise ValueError("Tickers list cannot be empty")

        if pd.to_datetime(end_date) < pd.to_datetime(start_date):
            raise ValueError(
                f"end_date ({end_date}) cannot be before start_date ({start_date})"
            )

        ticker_prices = {}

        for ticker in tickers:
            cache_file = self.cache_dir / f"{ticker}_{start_date}_{end_date}.csv"
            try:
                if cache_file.exists():
                    with open(cache_file, "r", encoding="utf-8") as f:
                        line1 = f.readline()
                        line2 = f.readline()
                    if "Ticker" in line2 or "Price" in line1:
                        df = pd.read_csv(
                            cache_file, index_col=0, parse_dates=True, header=[0, 1]
                        )
                    else:
                        df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                else:
                    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
                    if df is None or df.empty:
                        logger.warning(
                            f"Failed to fetch data for ticker '{ticker}': empty response"
                        )
                        continue
                    df.to_csv(cache_file)

                if isinstance(df.columns, pd.MultiIndex):
                    if ("Close", ticker) in df.columns:
                        series = df[("Close", ticker)]
                    elif ("Adj Close", ticker) in df.columns:
                        series = df[("Adj Close", ticker)]
                    elif "Close" in df.columns.get_level_values(0):
                        sub = df["Close"]
                        if ticker in sub.columns:
                            series = sub[ticker]
                        elif isinstance(sub, pd.Series):
                            series = sub
                        else:
                            series = sub.iloc[:, 0]
                    elif "Adj Close" in df.columns.get_level_values(0):
                        sub = df["Adj Close"]
                        if ticker in sub.columns:
                            series = sub[ticker]
                        elif isinstance(sub, pd.Series):
                            series = sub
                        else:
                            series = sub.iloc[:, 0]
                    else:
                        logger.warning(
                            f"No valid price column found for ticker '{ticker}'"
                        )
                        continue
                else:
                    if "Adj Close" in df.columns:
                        series = df["Adj Close"]
                    elif "Close" in df.columns:
                        series = df["Close"]
                    elif len(df.columns) == 1:
                        series = df.iloc[:, 0]
                    else:
                        logger.warning(
                            f"No valid price column found for ticker '{ticker}'"
                        )
                        continue


                if isinstance(series, pd.DataFrame):
                    series = series.squeeze()

                ticker_prices[ticker] = series
            except Exception as e:
                logger.warning(f"Error fetching data for ticker '{ticker}': {e}")
                continue

        if not ticker_prices:
            raise RuntimeError("All tickers failed to fetch price data")

        result_df = pd.DataFrame(ticker_prices)
        result_df.index = pd.to_datetime(result_df.index.values)
        return result_df

