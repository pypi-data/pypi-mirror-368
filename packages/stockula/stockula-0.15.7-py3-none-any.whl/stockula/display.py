"""Display and output handling for Stockula results."""

import json
from datetime import date, datetime
from typing import Any

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import StockulaConfig
from .container import Container
from .domain import Category


class ResultsDisplay:
    """Handles display and formatting of results."""

    def __init__(self, console: Console | None = None):
        """Initialize the display handler.

        Args:
            console: Rich console for output (optional)
        """
        self.console = console or Console()

    def print_results(
        self, results: dict[str, Any], output_format: str = "console", config=None, container=None, portfolio=None
    ):
        """Print results in specified format.

        Args:
            results: Results dictionary
            output_format: Output format (console, json)
            config: Optional configuration object for portfolio composition
            container: Optional DI container for fetching data
            portfolio: Optional portfolio instance for forecast display
        """
        if output_format == "json":
            self.console.print_json(json.dumps(results, indent=2, default=str))
        else:
            # Console output with Rich formatting
            if "technical_analysis" in results:
                self._display_technical_analysis(results["technical_analysis"])

            if "backtesting" in results:
                self._display_backtesting_results(results, config, container)

            if "forecasting" in results:
                self._display_forecast_results(results["forecasting"], portfolio)

    def _display_technical_analysis(self, ta_results: list[dict[str, Any]]):
        """Display technical analysis results.

        Args:
            ta_results: List of technical analysis results
        """
        self.console.print("\n[bold blue]Technical Analysis Results[/bold blue]", style="bold")

        for ta_result in ta_results:
            table = Table(title=f"Technical Analysis - {ta_result['ticker']}")
            table.add_column("Indicator", style="cyan", no_wrap=True)
            table.add_column("Value", style="magenta")

            for indicator, value in ta_result["indicators"].items():
                if isinstance(value, dict):
                    for k, v in value.items():
                        formatted_value = f"{v:.2f}" if isinstance(v, int | float) else str(v)
                        table.add_row(f"{indicator} - {k}", formatted_value)
                else:
                    formatted_value = f"{value:.2f}" if isinstance(value, int | float) else str(value)
                    table.add_row(indicator, formatted_value)

            self.console.print(table)

    def _display_backtesting_results(
        self, results: dict[str, Any], config: StockulaConfig | None, container: Container | None
    ):
        """Display backtesting results.

        Args:
            results: Results dictionary
            config: Optional configuration object
            container: Optional DI container
        """
        # Display general portfolio information
        self.console.print("\n[bold green]=== Backtesting Results ===[/bold green]")

        # Create portfolio information panel
        portfolio_info = []

        # Extract portfolio info from results metadata
        if "portfolio" in results:
            portfolio_data = results["portfolio"]
            if "initial_capital" in portfolio_data:
                portfolio_info.append(f"[cyan]Initial Capital:[/cyan] ${portfolio_data['initial_capital']:,.2f}")
            if "start" in portfolio_data and portfolio_data["start"]:
                portfolio_info.append(f"[cyan]Start Date:[/cyan] {portfolio_data['start']}")
            if "end" in portfolio_data and portfolio_data["end"]:
                portfolio_info.append(f"[cyan]End Date:[/cyan] {portfolio_data['end']}")

        # If portfolio info not in metadata, try to extract from backtest results
        if not portfolio_info and results.get("backtesting"):
            # Get portfolio information from the first backtest result
            first_backtest = results["backtesting"][0] if results["backtesting"] else {}

            if "initial_cash" in first_backtest:
                portfolio_info.append(f"[cyan]Initial Capital:[/cyan] ${first_backtest['initial_cash']:,.2f}")
            if "start_date" in first_backtest:
                portfolio_info.append(f"[cyan]Start Date:[/cyan] {first_backtest['start_date']}")
            if "end_date" in first_backtest:
                portfolio_info.append(f"[cyan]End Date:[/cyan] {first_backtest['end_date']}")

        # Display portfolio information if available
        if portfolio_info:
            self.console.print("[bold blue]Portfolio Information:[/bold blue]")
            for info in portfolio_info:
                self.console.print(f"  {info}")
            self.console.print()  # Add blank line

        # Display portfolio composition table (only if config and container are provided)
        if config and container:
            self._display_portfolio_composition(config, container)

        # Show ticker-level backtest results
        self._display_backtest_ticker_results(results["backtesting"])

        # Show strategy average returns summary
        self._display_strategy_average_returns(results["backtesting"])

    def _display_portfolio_composition(self, config: StockulaConfig, container: Container):
        """Display portfolio composition table.

        Args:
            config: Configuration object
            container: DI container
        """
        table = Table(title="Portfolio Composition")
        table.add_column("Ticker", style="cyan", no_wrap=True)
        table.add_column("Category", style="yellow")
        table.add_column("Quantity", style="white", justify="right")
        table.add_column("Allocation %", style="green", justify="right")
        table.add_column("Value", style="blue", justify="right")
        table.add_column("Status", style="magenta")

        # Get portfolio composition information
        portfolio = container.domain_factory().create_portfolio(config)
        all_assets = portfolio.get_all_assets()

        # Get hold-only categories from config
        hold_only_category_names = set(config.backtest.hold_only_categories)
        hold_only_categories = set()
        for category_name in hold_only_category_names:
            try:
                hold_only_categories.add(Category[category_name])
            except KeyError:
                pass  # Skip unknown categories

        # Get current prices for calculation
        fetcher = container.data_fetcher()
        symbols = [asset.symbol for asset in all_assets]
        try:
            current_prices = fetcher.get_current_prices(symbols, show_progress=False)
            total_portfolio_value = sum(asset.quantity * current_prices.get(asset.symbol, 0) for asset in all_assets)

            for asset in all_assets:
                current_price = current_prices.get(asset.symbol, 0)
                asset_value = asset.quantity * current_price
                allocation_pct = (asset_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0

                # Determine status
                status = "Hold Only" if asset.category in hold_only_categories else "Tradeable"
                status_color = "yellow" if status == "Hold Only" else "green"

                table.add_row(
                    asset.symbol,
                    asset.category.name if asset.category and hasattr(asset.category, "name") else str(asset.category),
                    f"{asset.quantity:.2f}",
                    f"{allocation_pct:.1f}%",
                    f"${asset_value:,.2f}",
                    f"[{status_color}]{status}[/{status_color}]",
                )
        except Exception:
            # Fallback if we can't get prices
            for asset in all_assets:
                status = "Hold Only" if asset.category in hold_only_categories else "Tradeable"
                status_color = "yellow" if status == "Hold Only" else "green"

                table.add_row(
                    asset.symbol,
                    asset.category.name if asset.category and hasattr(asset.category, "name") else str(asset.category),
                    f"{asset.quantity:.2f}",
                    "N/A",
                    "N/A",
                    f"[{status_color}]{status}[/{status_color}]",
                )

        self.console.print(table)
        self.console.print()  # Add blank line

    def _display_backtest_ticker_results(self, backtest_results: list[dict[str, Any]]):
        """Display ticker-level backtest results.

        Args:
            backtest_results: List of backtest results
        """
        # Check if we have multiple strategies
        strategies = {b["strategy"] for b in backtest_results}

        # Show ticker-level backtest results in a table
        self.console.print("\n[bold green]Ticker-Level Backtest Results[/bold green]")

        # Check if we have train/test results
        has_train_test = any("train_results" in backtest for backtest in backtest_results)

        if has_train_test:
            self._display_train_test_results(backtest_results)
        else:
            self._display_standard_backtest_results(backtest_results)

        # Show summary message about strategies and stocks
        unique_tickers = {b["ticker"] for b in backtest_results}
        self.console.print(
            f"Running [bold]{len(strategies)}[/bold] strategies across [bold]{len(unique_tickers)}[/bold] stocks..."
        )
        if len(strategies) > 1:
            self.console.print("Detailed results will be shown per strategy below.")

    def _display_train_test_results(self, backtest_results: list[dict[str, Any]]):
        """Display train/test split results.

        Args:
            backtest_results: List of backtest results
        """
        table = Table(title="Ticker-Level Backtest Results (Train/Test Split)")
        table.add_column("Ticker", style="cyan", no_wrap=True)
        table.add_column("Strategy", style="yellow", no_wrap=True)
        table.add_column("Train Return", style="green", justify="right")
        table.add_column("Test Return", style="green", justify="right")
        table.add_column("Train Sharpe", style="blue", justify="right")
        table.add_column("Test Sharpe", style="blue", justify="right")
        table.add_column("Test Trades", style="white", justify="right")
        table.add_column("Test Win Rate", style="magenta", justify="right")

        for backtest in backtest_results:
            if "train_results" in backtest:
                train_return_str = f"{backtest['train_results']['return_pct']:+.2f}%"
                test_return_str = f"{backtest['test_results']['return_pct']:+.2f}%"
                train_sharpe_str = f"{backtest['train_results']['sharpe_ratio']:.2f}"
                test_sharpe_str = f"{backtest['test_results']['sharpe_ratio']:.2f}"
                test_trades_str = str(backtest["test_results"]["num_trades"])

                if backtest["test_results"]["win_rate"] is None or pd.isna(backtest["test_results"]["win_rate"]):
                    test_win_rate_str = "N/A"
                else:
                    test_win_rate_str = f"{backtest['test_results']['win_rate']:.1f}%"

                table.add_row(
                    backtest["ticker"],
                    backtest["strategy"].upper(),
                    train_return_str,
                    test_return_str,
                    train_sharpe_str,
                    test_sharpe_str,
                    test_trades_str,
                    test_win_rate_str,
                )
            else:
                # Fallback for strategies without train/test split
                return_str = f"{backtest['return_pct']:+.2f}%"
                sharpe_str = f"{backtest['sharpe_ratio']:.2f}"
                trades_str = str(backtest["num_trades"])

                if backtest["win_rate"] is None:
                    win_rate_str = "N/A"
                else:
                    win_rate_str = f"{backtest['win_rate']:.1f}%"

                table.add_row(
                    backtest["ticker"],
                    backtest["strategy"].upper(),
                    return_str,
                    return_str,  # Same for both train/test
                    sharpe_str,
                    sharpe_str,  # Same for both train/test
                    trades_str,
                    win_rate_str,
                )

        self.console.print(table)
        self.console.print()  # Add blank line

        # Show train/test periods
        first_with_split = next((b for b in backtest_results if "train_period" in b), None)
        if first_with_split:
            self.console.print("[bold cyan]Data Periods:[/bold cyan]")
            train_start = first_with_split["train_period"]["start"]
            train_end = first_with_split["train_period"]["end"]
            train_days = first_with_split["train_period"]["days"]
            test_start = first_with_split["test_period"]["start"]
            test_end = first_with_split["test_period"]["end"]
            test_days = first_with_split["test_period"]["days"]

            self.console.print(f"  Training: {train_start} to {train_end} ({train_days} days)")
            self.console.print(f"  Testing:  {test_start} to {test_end} ({test_days} days)")
            self.console.print()

    def _display_standard_backtest_results(self, backtest_results: list[dict[str, Any]]):
        """Display standard backtest results without train/test split.

        Args:
            backtest_results: List of backtest results
        """
        table = Table(title="Ticker-Level Backtest Results")
        table.add_column("Ticker", style="cyan", no_wrap=True)
        table.add_column("Strategy", style="yellow", no_wrap=True)
        table.add_column("Return", style="green", justify="right")
        table.add_column("Sharpe Ratio", style="blue", justify="right")
        table.add_column("Max Drawdown", style="red", justify="right")
        table.add_column("Trades", style="white", justify="right")
        table.add_column("Win Rate", style="magenta", justify="right")

        for backtest in backtest_results:
            return_str = f"{backtest['return_pct']:+.2f}%"
            sharpe_str = f"{backtest['sharpe_ratio']:.2f}"
            drawdown_str = f"{backtest['max_drawdown_pct']:.2f}%"
            trades_str = str(backtest["num_trades"])

            if backtest["win_rate"] is None:
                win_rate_str = "N/A"
            else:
                win_rate_str = f"{backtest['win_rate']:.1f}%"

            table.add_row(
                backtest["ticker"],
                backtest["strategy"].upper(),
                return_str,
                sharpe_str,
                drawdown_str,
                trades_str,
                win_rate_str,
            )

        self.console.print(table)
        self.console.print()  # Add blank line

    def _display_strategy_average_returns(self, backtest_results: list[dict[str, Any]]):
        """Display average returns for each strategy across all tickers.

        Args:
            backtest_results: List of backtest results
        """
        # Calculate average returns by strategy
        from collections import defaultdict

        strategy_returns = defaultdict(list)

        for backtest in backtest_results:
            strategy = backtest["strategy"]

            # Get the return percentage based on result type
            if "test_results" in backtest:
                # Use test period returns for train/test split results
                return_pct = backtest["test_results"]["return_pct"]
            else:
                # Use standard return percentage
                return_pct = backtest["return_pct"]

            strategy_returns[strategy].append(return_pct)

        # Calculate averages and sort by highest to lowest
        strategy_averages = []
        for strategy, returns in strategy_returns.items():
            avg_return = sum(returns) / len(returns)
            strategy_averages.append({"strategy": strategy, "avg_return": avg_return, "num_tickers": len(returns)})

        # Sort by average return (highest to lowest)
        strategy_averages.sort(key=lambda x: x["avg_return"], reverse=True)

        # Display the summary table
        self.console.print("\n[bold cyan]=== Strategy Average Returns Summary ===[/bold cyan]")

        table = Table(title="Average Returns by Strategy (Sorted Highest to Lowest)")
        table.add_column("Strategy", style="yellow", no_wrap=True)
        table.add_column("Average Return %", style="green", justify="right")
        table.add_column("# Tickers Tested", style="white", justify="right")

        for strategy_data in strategy_averages:
            avg_return = strategy_data["avg_return"]
            # Color code the return
            if avg_return >= 0:
                return_style = "green"
            else:
                return_style = "red"

            table.add_row(
                strategy_data["strategy"].upper(),
                f"[{return_style}]{avg_return:+.2f}%[/{return_style}]",
                str(strategy_data["num_tickers"]),
            )

        self.console.print(table)
        self.console.print()  # Add blank line

        # Show the best performing strategy
        if strategy_averages:
            best_strategy = strategy_averages[0]
            self.console.print(
                f"[bold green]Best Performing Strategy:[/bold green] "
                f"[yellow]{best_strategy['strategy'].upper()}[/yellow] "
                f"with average return of [green]{best_strategy['avg_return']:+.2f}%[/green]"
            )
            self.console.print()

    def _display_forecast_results(self, forecast_results: list[dict[str, Any]], portfolio=None):
        """Display forecasting results.

        Args:
            forecast_results: List of forecast results
            portfolio: Optional portfolio instance for displaying quantities and values
        """
        self.console.print("\n[bold purple]=== Forecasting Results ===[/bold purple]")

        # Get date range from first non-error forecast
        date_info = ""
        for forecast in forecast_results:
            if "error" not in forecast and "start_date" in forecast:
                date_info = f" ({forecast['start_date']} to {forecast['end_date']})"
                break

        # Check if we have actual prices (evaluation mode)
        has_actual_prices = any("actual_price" in f for f in forecast_results if "error" not in f)

        table = Table(title=f"Price Forecasts{date_info}", show_header=True, header_style="bold")
        table.add_column("Ticker", style="cyan", no_wrap=True)
        table.add_column("Qty", style="green", justify="right", no_wrap=True)
        table.add_column("Current\nPrice", style="white", justify="right")
        table.add_column("Current\nValue", style="blue", justify="right")
        if has_actual_prices:
            table.add_column("Actual\nPrice", style="yellow", justify="right")
            table.add_column("Actual\nValue", style="yellow", justify="right")
        table.add_column("Forecast\nPrice", style="green", justify="right")
        table.add_column("Forecast\nValue", style="blue", justify="right")
        table.add_column("Return", style="magenta", justify="right")
        table.add_column("Confidence Range", style="yellow", justify="center")
        table.add_column("Model", style="blue")

        # Sort forecasts by return percentage (highest to lowest)
        # Separate error results from valid forecasts
        error_forecasts = [f for f in forecast_results if "error" in f]
        valid_forecasts = [f for f in forecast_results if "error" not in f]

        # Calculate return percentage for sorting
        for forecast in valid_forecasts:
            forecast["return_pct"] = (
                (forecast["forecast_price"] - forecast["current_price"]) / forecast["current_price"]
            ) * 100

        # Sort valid forecasts by return percentage (highest to lowest)
        sorted_forecasts = sorted(valid_forecasts, key=lambda f: f["return_pct"], reverse=True)

        # Combine sorted valid forecasts with error forecasts at the end
        all_forecasts = sorted_forecasts + error_forecasts

        for forecast in all_forecasts:
            ticker = forecast["ticker"]

            # Get quantity from portfolio if available
            quantity = 0.0
            if portfolio:
                asset = next((a for a in portfolio.get_all_assets() if a.symbol == ticker), None)
                if asset and hasattr(asset, "quantity"):
                    quantity = asset.quantity

            if "error" in forecast:
                row_data = [
                    ticker,
                    "[red]Error[/red]",  # Quantity
                    "[red]Error[/red]",  # Current Price
                    "[red]Error[/red]",  # Current Value
                ]
                if has_actual_prices:
                    row_data.extend(
                        [
                            "[red]Error[/red]",  # Actual Price
                            "[red]Error[/red]",  # Actual Value
                        ]
                    )
                row_data.extend(
                    [
                        "[red]Error[/red]",  # Forecast Price
                        "[red]Error[/red]",  # Forecast Value
                        "[red]Error[/red]",  # Return %
                        "[red]Error[/red]",  # Confidence Range
                        f"[red]{forecast['error']}[/red]",  # Best Model/Error
                    ]
                )
                table.add_row(*row_data)
            else:
                current_price = forecast["current_price"]
                forecast_price = forecast["forecast_price"]

                # Calculate values
                current_value = quantity * current_price
                forecast_value = quantity * forecast_price

                # Calculate return percentage
                return_pct = ((forecast_price - current_price) / current_price) * 100

                # Color code forecast based on direction
                forecast_color = (
                    "green" if forecast_price > current_price else "red" if forecast_price < current_price else "white"
                )
                forecast_str = f"[{forecast_color}]${forecast_price:.2f}[/{forecast_color}]"
                forecast_value_str = f"[{forecast_color}]${forecast_value:,.2f}[/{forecast_color}]"

                # Format return percentage with color
                return_str = f"[{forecast_color}]{return_pct:+.2f}%[/{forecast_color}]"

                # Build row data
                row_data = [
                    ticker,
                    f"{quantity:.2f}",
                    f"${current_price:.2f}",
                    f"${current_value:,.2f}",
                ]

                # Add actual price and value if available
                if has_actual_prices:
                    if "actual_price" in forecast:
                        actual_price = forecast["actual_price"]
                        actual_value = quantity * actual_price
                        # Color code actual vs forecast
                        actual_color = (
                            "green"
                            if actual_price < forecast_price
                            else "red"
                            if actual_price > forecast_price
                            else "white"
                        )
                        row_data.extend(
                            [
                                f"[{actual_color}]${actual_price:.2f}[/{actual_color}]",
                                f"[{actual_color}]${actual_value:,.2f}[/{actual_color}]",
                            ]
                        )
                    else:
                        row_data.extend(["N/A", "N/A"])

                row_data.extend(
                    [
                        forecast_str,
                        forecast_value_str,
                        return_str,
                        f"${forecast['lower_bound']:.2f} - ${forecast['upper_bound']:.2f}",
                        forecast["best_model"],
                    ]
                )

                table.add_row(*row_data)

        self.console.print(table)

        # Display evaluation metrics if available
        has_evaluation = any("evaluation" in f for f in forecast_results if "error" not in f)
        if has_evaluation:
            self._display_evaluation_metrics(all_forecasts)

    def _display_evaluation_metrics(self, forecasts: list[dict[str, Any]]):
        """Display forecast evaluation metrics.

        Args:
            forecasts: List of forecast results
        """
        self.console.print("\n[bold cyan]=== Forecast Evaluation Metrics ===[/bold cyan]")

        eval_table = Table(title="Model Performance on Test Data")
        eval_table.add_column("Ticker", style="cyan", no_wrap=True)
        eval_table.add_column("RMSE", style="yellow", justify="right")
        eval_table.add_column("MAE", style="yellow", justify="right")
        eval_table.add_column("MASE", style="green", justify="right")
        eval_table.add_column("Train Period", style="white")
        eval_table.add_column("Test Period", style="white")

        # Use the same sorted order as the forecast table
        for forecast in forecasts:
            if "error" not in forecast and "evaluation" in forecast:
                eval_metrics = forecast["evaluation"]
                train_period = forecast.get("train_period", {})
                test_period = forecast.get("test_period", {})

                train_str = f"{train_period.get('start', 'N/A')} to {train_period.get('end', 'N/A')}"
                test_str = f"{test_period.get('start', 'N/A')} to {test_period.get('end', 'N/A')}"

                # Use MASE if available, otherwise fall back to MAPE
                mase_value = eval_metrics.get("mase")
                if mase_value is not None:
                    mase_str = f"{mase_value:.3f}"
                    # Add interpretation: < 1 is better than naive
                    if mase_value < 1:
                        mase_str += " ✓"  # Good performance
                else:
                    # Fall back to MAPE if MASE not available
                    mape_value = eval_metrics.get("mape", 0)
                    mase_str = f"({mape_value:.1f}%)"  # Show MAPE in parentheses

                eval_table.add_row(
                    forecast["ticker"],
                    f"${eval_metrics['rmse']:.2f}",
                    f"${eval_metrics['mae']:.2f}",
                    mase_str,
                    train_str,
                    test_str,
                )

        self.console.print(eval_table)
        self.console.print(
            "\n[dim]MASE: Mean Absolute Scaled Error (< 1.0 = better than naive forecast, marked with ✓)[/dim]"
        )

    def show_forecast_warning(self, config: StockulaConfig):
        """Show forecast mode warning.

        Args:
            config: Configuration object
        """
        # Determine forecast mode message
        if config.forecast.forecast_length is not None:
            forecast_msg = f"• Forecasting {config.forecast.forecast_length} days into the future"
        elif config.forecast.test_start_date and config.forecast.test_end_date:
            forecast_msg = (
                f"• Evaluating forecast on test period: "
                f"{config.forecast.test_start_date} to {config.forecast.test_end_date}"
            )
        else:
            forecast_msg = "• Forecast configuration error: neither forecast_length nor test dates specified"

        self.console.print(
            Panel.fit(
                f"[bold yellow]FORECAST MODE - IMPORTANT NOTES:[/bold yellow]\\n"
                f"{forecast_msg}\\n"
                f"• The selected backend determines the approach (Chronos/AutoGluon/Simple)\\n"
                f"• This process may take several minutes per ticker\\n"
                f"• Press Ctrl+C at any time to cancel\\n"
                f"• Enable logging for more detailed progress information",
                border_style="yellow",
            )
        )

    def show_portfolio_forecast_value(self, config: StockulaConfig, portfolio, results: dict[str, Any]):
        """Show portfolio value for forecast mode with consistent price calculations.

        This method calculates portfolio values using consistent price baselines to ensure
        accurate portfolio return calculations. The current value is calculated using the
        same historical prices that the forecasting algorithm uses as its baseline, rather
        than real-time market prices, to maintain consistency between current and forecast
        values.

        Args:
            config: Configuration object
            portfolio: Portfolio instance
            results: Results dictionary containing forecasting results

        Note:
            The current portfolio value is calculated using the forecast algorithm's
            "current price" baseline to ensure the portfolio return percentage accurately
            reflects the forecasted price changes.
        """
        # Show portfolio value in a nice table
        portfolio_value_table = Table(title="Portfolio Value")
        portfolio_value_table.add_column("Metric", style="cyan", no_wrap=True, width=18)
        portfolio_value_table.add_column("Date", style="white", no_wrap=True, width=25)
        portfolio_value_table.add_column("Value", style="green", no_wrap=True, width=12)

        # Add initial capital row with appropriate date
        if config.forecast.test_start_date:
            # Historical evaluation mode - use test start date
            test_start = (
                config.forecast.test_start_date.strftime("%Y-%m-%d")
                if isinstance(config.forecast.test_start_date, date)
                else str(config.forecast.test_start_date)
            )
        else:
            # Future prediction mode - use today's date
            test_start = datetime.now().strftime("%Y-%m-%d")

        # For forecast mode, calculate current value based on the prices used in forecasting
        # This ensures consistency between current and forecast values
        #
        # Important: The forecasting algorithm uses the last price in the historical training
        # data as its "current price" baseline, which may differ from real-time market prices.
        # To ensure accurate portfolio return calculations, we use the same price baseline
        # for both current and forecast values. This prevents misleading return percentages
        # that could occur if different price sources were used.
        current_portfolio_value = 0.0
        if "forecasting" in results and results["forecasting"]:
            # Calculate current value using the same prices that forecasting uses
            for forecast in results["forecasting"]:
                if "error" not in forecast:
                    ticker = forecast["ticker"]
                    asset = next(
                        (a for a in portfolio.get_all_assets() if a.symbol == ticker),
                        None,
                    )
                    if asset and asset.quantity:
                        current_portfolio_value += asset.quantity * forecast["current_price"]

        # Fallback to initial capital if no forecast data available
        if current_portfolio_value == 0.0:
            current_portfolio_value = portfolio.initial_capital

        # Show initial capital and current value
        portfolio_value_table.add_row("Initial Capital", "Start", f"${portfolio.initial_capital:,.2f}")
        portfolio_value_table.add_row("Current Value", test_start, f"${current_portfolio_value:,.2f}")

        # Calculate forecasted portfolio value based on forecast results
        if "forecasting" in results and results["forecasting"]:
            forecasted_value = 0.0
            total_accuracy = 0
            valid_forecasts = 0

            # Check if we're in evaluation mode (have evaluation metrics)
            is_evaluation_mode = any("evaluation" in f for f in results["forecasting"] if "error" not in f)

            for forecast in results["forecasting"]:
                if "error" not in forecast:
                    ticker = forecast["ticker"]
                    asset = next(
                        (a for a in portfolio.get_all_assets() if a.symbol == ticker),
                        None,
                    )
                    if asset and asset.quantity:
                        # Calculate the forecasted value for this asset based on quantity and forecast price
                        # This simple calculation (quantity × forecast_price) ensures the forecast value
                        # represents what the portfolio would be worth at the forecasted prices
                        forecasted_asset_value = asset.quantity * forecast["forecast_price"]
                        forecasted_value += forecasted_asset_value

                        # If in evaluation mode, track accuracy
                        if "evaluation" in forecast:
                            accuracy = 100 - forecast["evaluation"]["mape"]
                            total_accuracy += accuracy
                            valid_forecasts += 1

            # Add forecasted value row with appropriate end date
            test_end = None
            if config.forecast.test_end_date:
                test_end = (
                    config.forecast.test_end_date.strftime("%Y-%m-%d")
                    if isinstance(config.forecast.test_end_date, date)
                    else str(config.forecast.test_end_date)
                )
            elif config.forecast.forecast_length:
                # Calculate future date based on forecast length
                from datetime import timedelta

                future_date = datetime.now() + timedelta(days=config.forecast.forecast_length)
                test_end = future_date.strftime("%Y-%m-%d") if isinstance(future_date, date) else str(future_date)
            else:
                # Try to get end date from any forecast result
                for forecast in results["forecasting"]:
                    if "error" not in forecast and "end_date" in forecast:
                        test_end = forecast["end_date"]
                        break

            if not test_end:
                # Default to 14 days if no forecast length specified
                from datetime import timedelta

                future_date = datetime.now() + timedelta(days=14)
                test_end = future_date.strftime("%Y-%m-%d") if isinstance(future_date, date) else str(future_date)

            portfolio_value_table.add_row("Forecast Value", test_end, f"${forecasted_value:,.2f}")

            # Show portfolio return
            if current_portfolio_value > 0:
                portfolio_return = ((forecasted_value - current_portfolio_value) / current_portfolio_value) * 100
                portfolio_value_table.add_row(
                    "Portfolio Return", f"{test_start} → {test_end}", f"{portfolio_return:+.2f}%"
                )

            # Add average accuracy row only for evaluation mode
            if is_evaluation_mode and valid_forecasts > 0 and test_end:
                avg_accuracy = total_accuracy / valid_forecasts
                portfolio_value_table.add_row("Accuracy", test_end, f"{avg_accuracy:.4f}%")

        self.console.print(portfolio_value_table)

    def show_strategy_summaries(self, manager, config: StockulaConfig, results: dict[str, Any]):
        """Show strategy-specific summaries.

        Args:
            manager: StockulaManager instance
            config: Configuration object
            results: Results dictionary
        """
        from collections import defaultdict

        # Group results by strategy
        strategy_results = defaultdict(list)

        for backtest in results["backtesting"]:
            strategy_results[backtest["strategy"]].append(backtest)

        # Only proceed if we have results
        if not strategy_results:
            self.console.print("\n[red]No backtesting results to display.[/red]")
            return

        # Create structured backtest results
        portfolio_backtest_results = manager.create_portfolio_backtest_results(results, strategy_results)

        # Sort strategy summaries by return during period (highest to lowest)
        sorted_summaries = sorted(
            portfolio_backtest_results.strategy_summaries,
            key=lambda s: (s.final_portfolio_value - s.initial_portfolio_value),
            reverse=True,  # Highest returns first
        )

        # Show summary for each strategy using structured data
        for strategy_summary in sorted_summaries:
            # Get broker config info
            broker_info = self._get_broker_info(config)

            # Create rich panel for strategy summary
            period_return = strategy_summary.final_portfolio_value - strategy_summary.initial_portfolio_value
            period_return_color = "green" if period_return > 0 else "red" if period_return < 0 else "white"

            # Format dates
            start_date, end_date = self._get_strategy_dates(config, portfolio_backtest_results)

            summary_content = f"""Start: {start_date}
End:   {end_date}

Parameters: {strategy_summary.parameters if strategy_summary.parameters else "Default"}
{broker_info}

Portfolio Value at {start_date}: ${strategy_summary.initial_portfolio_value:,.2f}
Portfolio Value at {end_date}: ${strategy_summary.final_portfolio_value:,.2f}

Strategy Performance:
  Average Return: [{period_return_color}]{strategy_summary.average_return_pct:+.2f}%[/{period_return_color}]
  Winning Stocks: {strategy_summary.winning_stocks}
  Losing Stocks: {strategy_summary.losing_stocks}
  Total Trades: {strategy_summary.total_trades}

Return During Period: [{period_return_color}]${period_return:,.2f} \
({strategy_summary.total_return_pct:+.2f}%)[/{period_return_color}]

Detailed report saved to: {
                manager.save_detailed_report(
                    strategy_summary.strategy_name,
                    [r.model_dump() for r in strategy_summary.detailed_results],
                    results,
                )
            }"""

            self.console.print(
                Panel(
                    summary_content,
                    title=f" STRATEGY: {strategy_summary.strategy_name.upper()} ",
                    border_style="white",
                    padding=(0, 1),
                )
            )

    def _get_broker_info(self, config: StockulaConfig) -> str:
        """Get broker information string.

        Args:
            config: Configuration object

        Returns:
            Formatted broker information string
        """
        if config.backtest.broker_config:
            broker_config = config.backtest.broker_config
            if broker_config.name in [
                "td_ameritrade",
                "etrade",
                "robinhood",
                "fidelity",
                "schwab",
            ]:
                broker_info = f"Broker: {broker_config.name} (zero-commission)"
            elif broker_config.commission_type == "percentage":
                commission_val = broker_config.commission_value
                if isinstance(commission_val, dict):
                    # If it's a dict, use the first value or default
                    commission_val = next(iter(commission_val.values())) if commission_val else 0.0
                broker_info = f"Broker: {broker_config.name} ({commission_val * 100:.1f}% commission"
                if broker_config.min_commission:
                    broker_info += f", ${broker_config.min_commission:.2f} min"
                broker_info += ")"
            elif broker_config.commission_type == "per_share":
                per_share_comm = broker_config.per_share_commission or broker_config.commission_value
                broker_info = f"Broker: {broker_config.name} (${per_share_comm:.3f}/share"
                if broker_config.min_commission:
                    broker_info += f", ${broker_config.min_commission:.2f} min"
                broker_info += ")"
            elif broker_config.commission_type == "tiered":
                broker_info = f"Broker: {broker_config.name} (tiered pricing"
                if broker_config.min_commission:
                    broker_info += f", ${broker_config.min_commission:.2f} min"
                broker_info += ")"
            elif broker_config.commission_type == "fixed":
                broker_info = f"Broker: {broker_config.name} (${broker_config.commission_value:.2f}/trade)"
            else:
                broker_info = f"Broker: {broker_config.name} ({broker_config.commission_type})"
        else:
            broker_info = f"Commission: {config.backtest.commission * 100:.1f}%"

        return broker_info

    def _get_strategy_dates(self, config: StockulaConfig, portfolio_backtest_results) -> tuple[str, str]:
        """Get strategy date range.

        Args:
            config: Configuration object
            portfolio_backtest_results: Portfolio backtest results

        Returns:
            Tuple of (start_date, end_date) as strings
        """
        start_date: str = "N/A"
        end_date: str = "N/A"

        # First try backtest dates, then data dates, then results
        if config.backtest.start_date:
            start_date = (
                config.backtest.start_date.strftime("%Y-%m-%d")
                if isinstance(config.backtest.start_date, date)
                else str(config.backtest.start_date)
            )
        elif config.data.start_date:
            start_date = (
                config.data.start_date.strftime("%Y-%m-%d")
                if isinstance(config.data.start_date, date)
                else str(config.data.start_date)
            )
        elif portfolio_backtest_results.date_range and portfolio_backtest_results.date_range.get("start"):
            start_date = portfolio_backtest_results.date_range["start"]

        if config.backtest.end_date:
            end_date = (
                config.backtest.end_date.strftime("%Y-%m-%d")
                if isinstance(config.backtest.end_date, date)
                else str(config.backtest.end_date)
            )
        elif config.data.end_date:
            end_date = (
                config.data.end_date.strftime("%Y-%m-%d")
                if isinstance(config.data.end_date, date)
                else str(config.data.end_date)
            )
        elif portfolio_backtest_results.date_range and portfolio_backtest_results.date_range.get("end"):
            end_date = portfolio_backtest_results.date_range["end"]

        return start_date, end_date
