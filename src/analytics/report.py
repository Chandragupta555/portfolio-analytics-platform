from pathlib import Path
from typing import Dict, Union

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.analytics.returns import cumulative_returns
from src.core.portfolio import Portfolio


class ReportGenerator:
    """Generates text summaries and visual charts for a Portfolio instance."""

    def __init__(
        self, portfolio: Portfolio, output_dir: Union[str, Path] = "output"
    ) -> None:
        self.portfolio = portfolio
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_text_summary(self) -> str:
        """Build a formatted plain-text summary string containing portfolio details,
        holdings, and risk metrics.
        """
        config = self.portfolio.config
        weights = self.portfolio.get_weights()
        risk_metrics = self.portfolio.get_risk_metrics()

        vol = risk_metrics.get("volatility", 0.0)
        sharpe = risk_metrics.get("sharpe_ratio", 0.0)
        mdd = risk_metrics.get("max_drawdown", 0.0)

        lines = [
            f"Portfolio Summary: {config.name}",
            "=" * 40,
            f"Date Range: {config.start_date} to {config.end_date}",
            f"Risk-Free Rate: {config.risk_free_rate * 100:.2f}%",
            "",
            "Holdings:",
            "-" * 20,
        ]

        for ticker, weight in weights.items():
            lines.append(f"  - {ticker}: {weight * 100:.2f}%")

        lines.extend(
            [
                "",
                "Risk Metrics:",
                "-" * 20,
                f"  - Volatility: {vol * 100:.2f}%",
                f"  - Sharpe Ratio: {sharpe:.2f}",
                f"  - Max Drawdown: {mdd * 100:.2f}%",
            ]
        )

        return "\n".join(lines)

    def save_text_summary(self) -> str:
        """Write text summary to {output_dir}/summary.txt and return the file path."""
        content = self.generate_text_summary()
        summary_path = self.output_dir / "summary.txt"
        summary_path.write_text(content, encoding="utf-8")
        return str(summary_path)

    def plot_cumulative_returns(self) -> str:
        """Plot cumulative returns over time and save to {output_dir}/cumulative_returns.png."""
        port_returns_series = self.portfolio.get_portfolio_returns()
        port_returns_df = port_returns_series.to_frame(name=self.portfolio.config.name)
        cum_rets = cumulative_returns(port_returns_df)

        plt.figure(figsize=(10, 5))
        plt.plot(
            cum_rets.index,
            cum_rets[self.portfolio.config.name] * 100,
            label=self.portfolio.config.name,
        )
        plt.title(f"Cumulative Returns - {self.portfolio.config.name}")
        plt.xlabel("Date")
        plt.ylabel("Cumulative Return (%)")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()
        plt.tight_layout()

        chart_path = self.output_dir / "cumulative_returns.png"
        plt.savefig(chart_path)
        plt.close()

        return str(chart_path)

    def plot_allocation_pie(self) -> str:
        """Plot portfolio weights as a pie chart and save to {output_dir}/allocation_pie.png."""
        weights = self.portfolio.get_weights()
        labels = list(weights.keys())
        sizes = [w * 100 for w in weights.values()]

        plt.figure(figsize=(7, 7))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
        plt.title(f"Portfolio Allocation - {self.portfolio.config.name}")
        plt.tight_layout()

        chart_path = self.output_dir / "allocation_pie.png"
        plt.savefig(chart_path)
        plt.close()

        return str(chart_path)

    def generate_full_report(self) -> Dict[str, str]:
        """Generate all reports (summary text, cumulative returns plot, allocation pie plot)
        and return a dictionary of file paths.
        """
        summary_file = self.save_text_summary()
        cum_chart_file = self.plot_cumulative_returns()
        alloc_chart_file = self.plot_allocation_pie()

        return {
            "summary": summary_file,
            "cumulative_returns_chart": cum_chart_file,
            "allocation_chart": alloc_chart_file,
        }
