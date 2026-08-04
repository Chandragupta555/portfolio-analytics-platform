from pathlib import Path
from unittest.mock import MagicMock
import pandas as pd
import pytest

from src.analytics.report import ReportGenerator
from src.config.config_loader import PortfolioConfig
from src.core.portfolio import Portfolio
from src.data.market_data import MarketDataService
from src.models.holding import Holding


@pytest.fixture
def sample_portfolio() -> Portfolio:
    config = PortfolioConfig(
        name="Report Test Portfolio",
        start_date="2023-01-01",
        end_date="2023-01-05",
        risk_free_rate=0.02,
        holdings=[
            Holding(ticker="AAPL", weight=0.6),
            Holding(ticker="MSFT", weight=0.4),
        ],
    )
    dates = pd.date_range("2023-01-01", periods=5, freq="D")
    prices_df = pd.DataFrame(
        {
            "AAPL": [100.0, 102.0, 101.0, 103.0, 105.0],
            "MSFT": [200.0, 202.0, 204.0, 203.0, 206.0],
        },
        index=dates,
    )
    mock_service = MagicMock(spec=MarketDataService)
    mock_service.fetch_prices.return_value = prices_df
    return Portfolio(config, mock_service)


def test_generate_text_summary(sample_portfolio: Portfolio) -> None:
    generator = ReportGenerator(sample_portfolio)
    summary = generator.generate_text_summary()

    assert isinstance(summary, str)
    assert "Report Test Portfolio" in summary
    assert "Volatility" in summary
    assert "Sharpe Ratio" in summary
    assert "Max Drawdown" in summary


def test_save_text_summary(sample_portfolio: Portfolio, tmp_path: Path) -> None:
    generator = ReportGenerator(sample_portfolio, output_dir=tmp_path)
    file_path_str = generator.save_text_summary()

    file_path = Path(file_path_str)
    assert file_path.exists()
    assert file_path.stat().st_size > 0
    content = file_path.read_text(encoding="utf-8")
    assert "Report Test Portfolio" in content


def test_plot_cumulative_returns(sample_portfolio: Portfolio, tmp_path: Path) -> None:
    generator = ReportGenerator(sample_portfolio, output_dir=tmp_path)
    chart_path_str = generator.plot_cumulative_returns()

    chart_path = Path(chart_path_str)
    assert chart_path.exists()
    assert chart_path.name == "cumulative_returns.png"
    assert chart_path.stat().st_size > 0


def test_plot_allocation_pie(sample_portfolio: Portfolio, tmp_path: Path) -> None:
    generator = ReportGenerator(sample_portfolio, output_dir=tmp_path)
    chart_path_str = generator.plot_allocation_pie()

    chart_path = Path(chart_path_str)
    assert chart_path.exists()
    assert chart_path.name == "allocation_pie.png"
    assert chart_path.stat().st_size > 0


def test_generate_full_report(sample_portfolio: Portfolio, tmp_path: Path) -> None:
    generator = ReportGenerator(sample_portfolio, output_dir=tmp_path)
    report_dict = generator.generate_full_report()

    assert set(report_dict.keys()) == {
        "summary",
        "cumulative_returns_chart",
        "allocation_chart",
    }
    for path_str in report_dict.values():
        path = Path(path_str)
        assert path.exists()
        assert path.stat().st_size > 0
