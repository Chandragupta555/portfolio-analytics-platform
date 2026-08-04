# Portfolio Analytics Platform

A modular Python command-line tool for loading portfolio configurations, fetching market data, computing risk and return analytics, and generating report artifacts.

## Features

- **Config-driven portfolios**: Define holdings, dates, and risk-free benchmark rates via validated JSON configuration files.
- **Cached market data**: Retrieve price history via Yahoo Finance (`yfinance`) with automatic local CSV caching to minimize API requests and network latency.
- **Quantitative analytics**: Compute daily percentage returns, cumulative returns, portfolio-weighted returns, annualized volatility, compound-correct Sharpe ratio, maximum drawdown, and asset correlation matrices.
- **Automated reporting**: Generate formatted text summaries and visualization charts (cumulative returns performance chart and portfolio allocation pie chart).

## Architecture

The project employs a layered architecture separating concerns between configuration loading, data retrieval, core orchestration, analytical computations, and report generation:

```text
src/
├── core/portfolio.py       — Portfolio orchestrator class
├── data/market_data.py     — MarketDataService (yfinance fetch + CSV cache)
├── analytics/returns.py    — daily/cumulative/portfolio-weighted returns
├── analytics/risk.py       — volatility, Sharpe ratio, max drawdown, correlation
├── analytics/report.py     — ReportGenerator (text summary + charts)
├── models/holding.py       — Holding dataclass
├── config/config_loader.py — PortfolioConfig loader with validation
└── main.py                 — CLI entry point
```

Data flows sequentially through the system: `config_loader` parses and validates input JSON into a `PortfolioConfig`, `MarketDataService` fetches or retrieves cached price history, `Portfolio` orchestrates analytics calculations via `returns` and `risk` modules, and `ReportGenerator` outputs the final text and image artifacts.

## Installation

1. Clone the repository and navigate to the project directory.
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the platform using the `main.py` entry point by providing a valid portfolio configuration JSON:

```bash
python main.py --config config/sample_portfolio.json --output output
```

### Configuration Format

Portfolios are defined in JSON format with holding weights summing to 1.0 (100%):

```json
{
  "name": "Sample Tech Portfolio",
  "start_date": "2023-01-01",
  "end_date": "2024-12-31",
  "risk_free_rate": 0.02,
  "holdings": [
    { "ticker": "AAPL", "weight": 0.40 },
    { "ticker": "MSFT", "weight": 0.35 },
    { "ticker": "GOOGL", "weight": 0.25 }
  ]
}
```

## Sample Output

Execution creates the designated `--output` directory containing:

- `summary.txt`: A plain-text summary containing portfolio metadata, asset allocation breakdown, and key risk metrics (annualized volatility, Sharpe ratio, and maximum drawdown).
- `cumulative_returns.png`: A line chart displaying the compounded percentage growth of the portfolio over the specified timeframe.
- `allocation_pie.png`: A pie chart illustrating asset allocation weights.

## Testing

The test suite contains 38 unit tests covering all core modules, validation rules, risk calculations, and report generation routines. Market data calls are mocked using `unittest.mock` to ensure offline execution speed and reliability.

To run the full test suite:

```bash
python -m pytest
```

## Design Decisions

- **Pure functions for analytics**: Calculation routines in `returns.py` and `risk.py` are implemented as stateless, pure functions acting on pandas DataFrames and Series. This maximizes testability and prevents unexpected state mutation.
- **Local CSV caching**: Price data downloads are cached locally in `src/data/cache/` by ticker and date range. Subsequent runs read from local CSVs, eliminating unnecessary external network calls and protecting against API rate limiting.
- **Compound-correct risk-free rate conversion**: The daily risk-free rate for Sharpe ratio calculation is converted using the exact compounding formula \(r_{\text{daily}} = (1 + r_{\text{annual}})^{1/252} - 1\), avoiding the simplistic \(r_{\text{annual}} / 252\) approximation.

## Roadmap

- **V1 (Current)**: Core portfolio analysis, risk/return analytics, local caching, and automated text/chart report generation.
- **V2**: Markowitz Mean-Variance portfolio optimization and efficient frontier visualization.
- **V3**: Interactive web dashboard interface and support for alternative data providers.
