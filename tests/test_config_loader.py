import json
from pathlib import Path
import pytest

from src.config.config_loader import load_config, PortfolioConfig
from src.models.holding import Holding


def test_valid_config_loads_and_uppercases_ticker(tmp_path: Path) -> None:
    config_file = tmp_path / "portfolio.json"
    data = {
        "name": "Test Portfolio",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "risk_free_rate": 0.02,
        "holdings": [
            {"ticker": "aapl", "weight": 0.6},
            {"ticker": "Msft", "weight": 0.4},
        ],
    }
    config_file.write_text(json.dumps(data), encoding="utf-8")

    config = load_config(str(config_file))
    assert isinstance(config, PortfolioConfig)
    assert config.name == "Test Portfolio"
    assert len(config.holdings) == 2
    assert config.holdings[0].ticker == "AAPL"
    assert config.holdings[1].ticker == "MSFT"


def test_sample_portfolio_json_file_loads() -> None:
    config = load_config("config/sample_portfolio.json")
    assert config.name == "Sample Tech Portfolio"
    assert len(config.holdings) == 3
    assert [h.ticker for h in config.holdings] == ["AAPL", "MSFT", "GOOGL"]
    assert pytest.approx(sum(h.weight for h in config.holdings)) == 1.0


def test_weights_not_summing_to_one_raises_value_error(tmp_path: Path) -> None:
    config_file = tmp_path / "invalid_weights.json"
    data = {
        "name": "Invalid Weights Portfolio",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "risk_free_rate": 0.02,
        "holdings": [
            {"ticker": "AAPL", "weight": 0.5},
            {"ticker": "MSFT", "weight": 0.2},
        ],
    }
    config_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="must sum to 1.0"):
        load_config(str(config_file))


def test_missing_file_raises_value_error() -> None:
    missing_path = "non_existent_file_12345.json"
    with pytest.raises(ValueError, match=f"Config file not found: {missing_path}"):
        load_config(missing_path)


def test_empty_holdings_raises_value_error(tmp_path: Path) -> None:
    config_file = tmp_path / "empty_holdings.json"
    data = {
        "name": "Empty Holdings Portfolio",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "holdings": [],
    }
    config_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="holdings list cannot be empty"):
        load_config(str(config_file))


def test_malformed_json_raises_value_error(tmp_path: Path) -> None:
    config_file = tmp_path / "malformed.json"
    config_file.write_text("{ invalid json }", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON format"):
        load_config(str(config_file))


def test_holding_invalid_weight() -> None:
    with pytest.raises(ValueError, match="greater than 0"):
        Holding(ticker="AAPL", weight=0.0)


def test_holding_with_invalid_weight_in_config_raises_error(tmp_path: Path) -> None:
    config_file = tmp_path / "invalid_holding_weight.json"
    data = {
        "name": "Invalid Holding Weight Portfolio",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "holdings": [
            {"ticker": "AAPL", "weight": 0.0},
            {"ticker": "MSFT", "weight": 1.0},
        ],
    }
    config_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="greater than 0"):
        load_config(str(config_file))

