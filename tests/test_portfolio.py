from unittest.mock import MagicMock
import pandas as pd
import pytest

from src.config.config_loader import PortfolioConfig
from src.core.portfolio import Portfolio
from src.data.market_data import MarketDataService
from src.models.holding import Holding


@pytest.fixture
def sample_config() -> PortfolioConfig:
    return PortfolioConfig(
        name="Test Portfolio",
        start_date="2023-01-01",
        end_date="2023-01-05",
        risk_free_rate=0.02,
        holdings=[
            Holding(ticker="AAPL", weight=0.6),
            Holding(ticker="MSFT", weight=0.4),
        ],
    )


@pytest.fixture
def mock_prices_df() -> pd.DataFrame:
    dates = pd.date_range("2023-01-01", periods=5, freq="D")
    return pd.DataFrame(
        {
            "AAPL": [100.0, 102.0, 101.0, 103.0, 105.0],
            "MSFT": [200.0, 202.0, 204.0, 203.0, 206.0],
        },
        index=dates,
    )


@pytest.fixture
def mock_market_data_service(mock_prices_df: pd.DataFrame) -> MagicMock:
    service = MagicMock(spec=MarketDataService)
    service.fetch_prices.return_value = mock_prices_df
    return service


def test_get_weights(
    sample_config: PortfolioConfig, mock_market_data_service: MagicMock
) -> None:
    portfolio = Portfolio(sample_config, mock_market_data_service)
    weights = portfolio.get_weights()

    assert isinstance(weights, dict)
    assert weights == {"AAPL": 0.6, "MSFT": 0.4}


def test_get_price_history_calls_fetch_prices_correctly(
    sample_config: PortfolioConfig,
    mock_market_data_service: MagicMock,
    mock_prices_df: pd.DataFrame,
) -> None:
    portfolio = Portfolio(sample_config, mock_market_data_service)
    df = portfolio.get_price_history()

    pd.testing.assert_frame_equal(df, mock_prices_df)
    mock_market_data_service.fetch_prices.assert_called_once_with(
        tickers=["AAPL", "MSFT"],
        start_date="2023-01-01",
        end_date="2023-01-05",
    )


def test_get_price_history_caching(
    sample_config: PortfolioConfig, mock_market_data_service: MagicMock
) -> None:
    portfolio = Portfolio(sample_config, mock_market_data_service)

    df1 = portfolio.get_price_history()
    df2 = portfolio.get_price_history()

    assert df1 is df2
    assert mock_market_data_service.fetch_prices.call_count == 1


def test_get_portfolio_returns_produces_series(
    sample_config: PortfolioConfig, mock_market_data_service: MagicMock
) -> None:
    portfolio = Portfolio(sample_config, mock_market_data_service)
    returns_series = portfolio.get_portfolio_returns()

    assert isinstance(returns_series, pd.Series)
    assert len(returns_series) == 4


def test_get_risk_metrics_structure(
    sample_config: PortfolioConfig, mock_market_data_service: MagicMock
) -> None:
    portfolio = Portfolio(sample_config, mock_market_data_service)
    risk_metrics = portfolio.get_risk_metrics()

    assert isinstance(risk_metrics, dict)
    assert set(risk_metrics.keys()) == {"volatility", "sharpe_ratio", "max_drawdown"}
    assert isinstance(risk_metrics["volatility"], float)
    assert isinstance(risk_metrics["sharpe_ratio"], float)
    assert isinstance(risk_metrics["max_drawdown"], float)


def test_get_correlation_matrix_structure(
    sample_config: PortfolioConfig, mock_market_data_service: MagicMock
) -> None:
    portfolio = Portfolio(sample_config, mock_market_data_service)
    corr_df = portfolio.get_correlation_matrix()

    assert isinstance(corr_df, pd.DataFrame)
    assert list(corr_df.columns) == ["AAPL", "MSFT"]
    assert list(corr_df.index) == ["AAPL", "MSFT"]


def test_get_risk_metrics_uses_config_risk_free_rate(
    mock_market_data_service: MagicMock,
) -> None:
    holdings = [
        Holding(ticker="AAPL", weight=0.6),
        Holding(ticker="MSFT", weight=0.4),
    ]
    config1 = PortfolioConfig(
        name="Portfolio RF 0.01",
        start_date="2023-01-01",
        end_date="2023-01-05",
        risk_free_rate=0.01,
        holdings=holdings,
    )
    config2 = PortfolioConfig(
        name="Portfolio RF 0.10",
        start_date="2023-01-01",
        end_date="2023-01-05",
        risk_free_rate=0.10,
        holdings=holdings,
    )

    portfolio1 = Portfolio(config1, mock_market_data_service)
    portfolio2 = Portfolio(config2, mock_market_data_service)

    metrics1 = portfolio1.get_risk_metrics()
    metrics2 = portfolio2.get_risk_metrics()

    assert metrics1["sharpe_ratio"] != metrics2["sharpe_ratio"]

