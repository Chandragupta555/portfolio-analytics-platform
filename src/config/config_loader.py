from dataclasses import dataclass
import json
import os
from typing import List

from src.models.holding import Holding


@dataclass
class PortfolioConfig:
    name: str
    holdings: List[Holding]
    start_date: str
    end_date: str
    risk_free_rate: float = 0.02


def load_config(path: str) -> PortfolioConfig:
    if not os.path.exists(path):
        raise ValueError(f"Config file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in config file '{path}': {e.msg}") from e

    if not isinstance(data, dict):
        raise ValueError(f"Invalid config format in '{path}': expected JSON object at root")

    name = data.get("name")
    if not name or not isinstance(name, str):
        raise ValueError(f"Missing or invalid 'name' field in config file '{path}'")

    start_date = data.get("start_date")
    if not start_date or not isinstance(start_date, str):
        raise ValueError(f"Missing or invalid 'start_date' field in config file '{path}'")

    end_date = data.get("end_date")
    if not end_date or not isinstance(end_date, str):
        raise ValueError(f"Missing or invalid 'end_date' field in config file '{path}'")

    risk_free_rate = data.get("risk_free_rate", 0.02)
    if not isinstance(risk_free_rate, (int, float)):
        raise ValueError(f"Invalid 'risk_free_rate' in config file '{path}': expected numeric value")

    raw_holdings = data.get("holdings")
    if raw_holdings is None or not isinstance(raw_holdings, list) or len(raw_holdings) == 0:
        raise ValueError(f"Portfolio holdings list cannot be empty in config file '{path}'")

    holdings: List[Holding] = []
    for idx, item in enumerate(raw_holdings):
        if not isinstance(item, dict):
            raise ValueError(f"Holding entry at index {idx} in '{path}' must be a JSON object")
        ticker = item.get("ticker")
        weight = item.get("weight")
        shares = item.get("shares")
        if ticker is None or weight is None:
            raise ValueError(f"Holding entry at index {idx} in '{path}' missing required fields 'ticker' or 'weight'")
        holdings.append(
            Holding(
                ticker=str(ticker),
                weight=float(weight),
                shares=float(shares) if shares is not None else None,
            )
        )

    total_weight = sum(h.weight for h in holdings)
    if abs(total_weight - 1.0) > 0.01:
        raise ValueError(f"Holding weights must sum to 1.0 (got {total_weight:.4f}) in config file '{path}'")

    return PortfolioConfig(
        name=name,
        holdings=holdings,
        start_date=start_date,
        end_date=end_date,
        risk_free_rate=float(risk_free_rate),
    )
