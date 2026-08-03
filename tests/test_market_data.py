from pathlib import Path
from unittest.mock import patch
import pandas as pd
import pytest

from src.data.market_data import MarketDataService


@pytest.fixture
def mock_stock_data() -> pd.DataFrame:
    dates = pd.date_range(start="2023-01-01", end="2023-01-05", freq="D")
    return pd.DataFrame(
        {
            "Open": [100.0, 101.0, 102.0, 103.0, 104.0],
            "High": [105.0, 106.0, 107.0, 108.0, 109.0],
            "Low": [99.0, 100.0, 101.0, 102.0, 103.0],
            "Close": [104.0, 105.0, 106.0, 107.0, 108.0],
            "Adj Close": [104.0, 105.0, 106.0, 107.0, 108.0],
            "Volume": [1000, 1100, 1200, 1300, 1400],
        },
        index=dates,
    )


def test_fetch_prices_returns_dataframe_with_correct_columns(
    tmp_path: Path, mock_stock_data: pd.DataFrame
) -> None:
    service = MarketDataService(cache_dir=str(tmp_path))

    with patch("yfinance.download", return_value=mock_stock_data) as mock_download:
        df = service.fetch_prices(
            tickers=["AAPL", "MSFT"], start_date="2023-01-01", end_date="2023-01-05"
        )

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["AAPL", "MSFT"]
        assert len(df) == 5
        assert mock_download.call_count == 2


def test_cached_data_is_used_on_second_call(
    tmp_path: Path, mock_stock_data: pd.DataFrame
) -> None:
    service = MarketDataService(cache_dir=str(tmp_path))

    with patch("yfinance.download", return_value=mock_stock_data) as mock_download:
        df1 = service.fetch_prices(
            tickers=["AAPL"], start_date="2023-01-01", end_date="2023-01-05"
        )
        assert mock_download.call_count == 1

        df2 = service.fetch_prices(
            tickers=["AAPL"], start_date="2023-01-01", end_date="2023-01-05"
        )
        assert mock_download.call_count == 1
        pd.testing.assert_frame_equal(df1, df2)


def test_failing_ticker_skipped_with_warning(
    tmp_path: Path, mock_stock_data: pd.DataFrame, caplog: pytest.LogCaptureFixture
) -> None:
    service = MarketDataService(cache_dir=str(tmp_path))

    def side_effect(ticker: str, **kwargs):
        if ticker == "FAIL":
            return pd.DataFrame()
        return mock_stock_data

    with patch("yfinance.download", side_effect=side_effect):
        df = service.fetch_prices(
            tickers=["AAPL", "FAIL"], start_date="2023-01-01", end_date="2023-01-05"
        )

        assert list(df.columns) == ["AAPL"]
        assert "FAIL" not in df.columns
        assert "Failed to fetch data for ticker 'FAIL'" in caplog.text


def test_all_tickers_fail_raises_runtime_error(tmp_path: Path) -> None:
    service = MarketDataService(cache_dir=str(tmp_path))

    with patch("yfinance.download", return_value=pd.DataFrame()):
        with pytest.raises(RuntimeError, match="All tickers failed to fetch price data"):
            service.fetch_prices(
                tickers=["FAIL1", "FAIL2"],
                start_date="2023-01-01",
                end_date="2023-01-05",
            )


def test_empty_tickers_list_raises_value_error(tmp_path: Path) -> None:
    service = MarketDataService(cache_dir=str(tmp_path))
    with pytest.raises(ValueError, match="Tickers list cannot be empty"):
        service.fetch_prices(
            tickers=[], start_date="2023-01-01", end_date="2023-01-05"
        )


def test_invalid_date_range_raises_value_error(tmp_path: Path) -> None:
    service = MarketDataService(cache_dir=str(tmp_path))
    with pytest.raises(ValueError, match="cannot be before start_date"):
        service.fetch_prices(
            tickers=["AAPL"], start_date="2023-01-05", end_date="2023-01-01"
        )
