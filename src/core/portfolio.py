from typing import Dict, Optional
import pandas as pd

from src.analytics.returns import daily_returns, portfolio_returns
from src.analytics.risk import correlation_matrix, max_drawdown, sharpe_ratio, volatility
from src.config.config_loader import PortfolioConfig
from src.data.market_data import MarketDataService


class Portfolio:
    """Orchestrates portfolio analytics by combining configuration, market data,
    and returns/risk calculation modules.
    """

    def __init__(
        self, config: PortfolioConfig, market_data_service: MarketDataService
    ) -> None:
        self.config = config
        self.market_data_service = market_data_service
        self._price_history: Optional[pd.DataFrame] = None

    def get_weights(self) -> Dict[str, float]:
        """Return portfolio asset weights as a dictionary of {ticker: weight}."""
        return {h.ticker: h.weight for h in self.config.holdings}

    def get_price_history(self) -> pd.DataFrame:
        """Fetch and cache asset price history from the market data service."""
        if self._price_history is None:
            tickers = [h.ticker for h in self.config.holdings]
            self._price_history = self.market_data_service.fetch_prices(
                tickers=tickers,
                start_date=self.config.start_date,
                end_date=self.config.end_date,
            )
        return self._price_history

    def get_daily_returns(self) -> pd.DataFrame:
        """Return daily returns for each asset in the portfolio."""
        return daily_returns(self.get_price_history())

    def get_portfolio_returns(self) -> pd.Series:
        """Return the weighted daily returns of the portfolio."""
        return portfolio_returns(self.get_daily_returns(), self.get_weights())

    def get_risk_metrics(self) -> Dict[str, float]:
        """Return a dictionary of key portfolio risk metrics:
        volatility, sharpe_ratio, and max_drawdown.
        """
        port_returns = self.get_portfolio_returns()
        rf = self.config.risk_free_rate
        return {
            "volatility": volatility(port_returns),
            "sharpe_ratio": sharpe_ratio(port_returns, risk_free_rate=rf),
            "max_drawdown": max_drawdown(port_returns),
        }

    def get_correlation_matrix(self) -> pd.DataFrame:
        """Return the correlation matrix of daily asset returns."""
        return correlation_matrix(self.get_daily_returns())
