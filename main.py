import argparse
import sys
from typing import List, Optional

from src.analytics.report import ReportGenerator
from src.config.config_loader import load_config
from src.core.portfolio import Portfolio
from src.data.market_data import MarketDataService


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse CLI arguments for the Portfolio Analytics tool."""
    parser = argparse.ArgumentParser(
        description="Portfolio Analytics Platform - Analyze portfolio risk and returns."
    )
    parser.add_argument(
        "--config",
        required=True,
        type=str,
        help="Path to the portfolio configuration JSON file.",
    )
    parser.add_argument(
        "--output",
        default="output",
        type=str,
        help="Output directory path for reports and charts (default: 'output').",
    )
    return parser.parse_args(args)


def main(args_list: Optional[List[str]] = None) -> int:
    """Main execution entry point for the portfolio analytics CLI tool."""
    try:
        args = parse_args(args_list)

        try:
            config = load_config(args.config)
        except ValueError as e:
            print(f"Configuration Error: {e}", file=sys.stderr)
            return 1

        market_data_service = MarketDataService()
        portfolio = Portfolio(config, market_data_service)
        report_generator = ReportGenerator(portfolio, output_dir=args.output)

        report_paths = report_generator.generate_full_report()

        summary_text = report_generator.generate_text_summary()
        print("\n" + summary_text + "\n")
        print("=" * 40)
        print("Report Generation Complete!")
        print(f"Summary Text: {report_paths.get('summary')}")
        print(f"Cumulative Returns Chart: {report_paths.get('cumulative_returns_chart')}")
        print(f"Allocation Chart: {report_paths.get('allocation_chart')}")
        print("=" * 40)

        return 0

    except Exception as e:
        print(f"Error executing portfolio analysis: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
