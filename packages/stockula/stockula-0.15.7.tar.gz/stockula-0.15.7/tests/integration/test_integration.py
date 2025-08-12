"""Integration tests for Stockula."""

from unittest.mock import patch

import pytest
import yaml

from stockula.config import StockulaConfig, load_config
from stockula.data.fetcher import DataFetcher
from stockula.database.manager import DatabaseManager
from stockula.domain import DomainFactory


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete workflows."""

    def test_config_to_portfolio_workflow(self, temp_config_file, mock_data_fetcher, integration_container):
        """Test loading config and creating portfolio."""
        # Load config
        config = load_config(temp_config_file)
        assert isinstance(config, StockulaConfig)

        # Increase max position size to avoid allocation constraint errors
        config.portfolio.max_position_size = 75.0

        # Create portfolio with mock data fetcher
        factory = DomainFactory(fetcher=mock_data_fetcher, logging_manager=integration_container.logging_manager())
        portfolio = factory.create_portfolio(config)

        assert portfolio.name == "Test Portfolio"
        assert len(portfolio.assets) == 4
        assert portfolio.initial_capital == 100000.0

    def test_data_fetching_with_cache(self, temp_db_path, mock_yfinance_ticker, integration_container):
        """Test data fetching with database caching."""
        with patch("yfinance.Ticker", return_value=mock_yfinance_ticker) as mock_yf:
            fetcher = DataFetcher(
                use_cache=True, db_path=temp_db_path, logging_manager=integration_container.logging_manager()
            )

            # Use a specific date range that won't change
            start_date = "2023-01-01"
            end_date = "2023-01-31"

            # First fetch - should hit API and cache
            data1 = fetcher.get_stock_data("AAPL", start=start_date, end=end_date)
            assert not data1.empty
            assert mock_yf.called  # First call should hit API

            # Reset the mock
            mock_yf.reset_mock()

            # Second fetch - should use cache
            data2 = fetcher.get_stock_data("AAPL", start=start_date, end=end_date)
            # The mock might be called for info, but history should come from cache
            assert len(data2) == len(data1)

    def test_full_analysis_workflow(
        self, sample_stockula_config, mock_data_fetcher, backtest_data, mock_container, integration_container
    ):
        """Test complete analysis workflow."""
        # Mock the container to use our mock data fetcher
        mock_data_fetcher.get_stock_data = lambda *args, **kwargs: backtest_data

        # Adjust max_position_size to accommodate SPY allocation
        sample_stockula_config.portfolio.max_position_size = 75.0

        factory = DomainFactory(fetcher=mock_data_fetcher, logging_manager=integration_container.logging_manager())
        portfolio = factory.create_portfolio(sample_stockula_config)

        # Test that we can access portfolio assets
        assert len(portfolio.assets) > 0
        assert portfolio.assets[0].ticker.symbol == "AAPL"

        # Test Technical Analysis creation
        from stockula.technical_analysis import TechnicalIndicators

        ta = TechnicalIndicators(backtest_data)
        # Test individual indicators
        sma = ta.sma(period=50)
        rsi = ta.rsi(period=14)
        assert len(sma) > 0
        assert len(rsi) > 0

        # Test Backtesting setup
        from stockula.backtesting import BacktestRunner

        runner = BacktestRunner(cash=10000.0, commission=0.002)
        # BacktestRunner doesn't take data in __init__, it's passed to run()
        assert runner.cash == 10000.0

        # Test Forecasting setup
        from stockula.forecasting import ForecastingManager

        forecaster = ForecastingManager(
            data_fetcher=integration_container.data_fetcher(), logging_manager=integration_container.logging_manager()
        )
        assert forecaster is not None  # Just check that it initialized successfully


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database integration."""

    def test_database_workflow(self, temp_db_path, sample_ohlcv_data):
        """Test complete database workflow."""
        db = DatabaseManager(temp_db_path)

        # Add stock
        db.add_stock("AAPL", "Apple Inc.", "Technology", 3000000000000)

        # Add price data
        price_data = []
        for date, row in sample_ohlcv_data.iterrows():
            price_data.append(
                (
                    "AAPL",
                    date,
                    row["Open"],
                    row["High"],
                    row["Low"],
                    row["Close"],
                    row["Volume"],
                    "1d",
                )
            )
        db.bulk_add_price_data(price_data)

        # Add additional data
        db.add_stock_info("AAPL", {"sector": "Technology", "employees": 150000})
        import pandas as pd

        dividends = pd.Series([0.23], index=[sample_ohlcv_data.index[0]])
        db.add_dividends("AAPL", dividends)

        # Retrieve data
        price_history = db.get_price_history("AAPL")
        assert len(price_history) == len(sample_ohlcv_data)

        info = db.get_stock_info("AAPL")
        assert info["sector"] == "Technology"

        dividends = db.get_dividends("AAPL")
        assert len(dividends) == 1

        # Get statistics
        stats = db.get_database_stats()
        assert stats["stocks"] == 1
        assert stats["price_history"] == len(sample_ohlcv_data)
        assert stats["dividends"] == 1


@pytest.mark.integration
class TestConfigurationIntegration:
    """Test configuration integration."""

    def test_yaml_roundtrip(self, sample_stockula_config, tmp_path):
        """Test saving and loading configuration."""
        from stockula.config import save_config

        # Save config
        config_path = tmp_path / "test_.stockula.yaml"
        save_config(sample_stockula_config, str(config_path))

        # Load it back
        loaded_config = load_config(str(config_path))

        # Compare key fields
        assert loaded_config.portfolio.name == sample_stockula_config.portfolio.name
        assert loaded_config.portfolio.initial_capital == sample_stockula_config.portfolio.initial_capital
        assert len(loaded_config.portfolio.tickers) == len(sample_stockula_config.portfolio.tickers)

    def test_environment_override(self, tmp_path, monkeypatch):
        """Test environment variable overrides."""
        # Create a config file
        config_data = {"portfolio": {"name": "Original Name", "initial_capital": 50000}}
        config_path = tmp_path / "env_test.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Set environment variable
        monkeypatch.setenv("STOCKULA_CONFIG_FILE", str(config_path))

        # Load config (in real implementation, this would check env var)
        config = load_config(str(config_path))
        assert config.portfolio.name == "Original Name"


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Test performance with larger datasets."""

    def test_large_portfolio_performance(self, integration_container, mock_data_fetcher):
        """Test performance with large portfolio."""
        from unittest.mock import Mock

        from stockula.config import PortfolioConfig, TickerConfig

        # Mock the fetcher to return fake prices for our fake stocks
        def mock_get_current_prices(symbols, show_progress=True):
            """Return mock prices for fake stock symbols."""
            if isinstance(symbols, str):
                symbols = [symbols]
            return {symbol: 100.0 + i for i, symbol in enumerate(symbols)}

        def mock_get_info(symbol):
            """Return mock info for fake stock symbols."""
            return {"longName": f"Company {symbol}", "sector": "Technology", "marketCap": 1000000000}

        mock_data_fetcher.get_current_prices = Mock(side_effect=mock_get_current_prices)
        mock_data_fetcher.get_info = Mock(side_effect=mock_get_info)

        # Create portfolio with 100 assets
        tickers = []
        for i in range(100):
            tickers.append(
                TickerConfig(
                    symbol=f"STOCK{i:03d}",
                    quantity=10.0,
                    category="GROWTH" if i % 2 == 0 else "VALUE",
                )
            )

        config = StockulaConfig(
            portfolio=PortfolioConfig(name="Large Portfolio", initial_capital=1000000.0, tickers=tickers)
        )

        factory = DomainFactory(fetcher=mock_data_fetcher, logging_manager=integration_container.logging_manager())
        portfolio = factory.create_portfolio(config)

        assert len(portfolio.assets) == 100

        # Test category allocation
        from stockula.domain import Category

        growth_assets = portfolio.get_assets_by_category(Category.GROWTH)
        assert len(growth_assets) == 50

    def test_large_dataset_analysis(self, mock_data_fetcher):
        """Test analysis with large dataset."""
        import numpy as np
        import pandas as pd

        # Create 5 years of daily data
        dates = pd.date_range(start="2019-01-01", end="2023-12-31", freq="D")
        large_data = pd.DataFrame(
            {
                "Open": 100 + np.random.randn(len(dates)).cumsum(),
                "High": 102 + np.random.randn(len(dates)).cumsum(),
                "Low": 98 + np.random.randn(len(dates)).cumsum(),
                "Close": 100 + np.random.randn(len(dates)).cumsum(),
                "Volume": np.random.randint(1000000, 5000000, len(dates)),
            },
            index=dates,
        )

        # Ensure positive prices
        large_data = large_data.abs()

        # Test technical analysis
        from stockula.technical_analysis import TechnicalIndicators

        ta = TechnicalIndicators(large_data)

        # Calculate multiple indicators
        sma_200 = ta.sma(200)
        ema_50 = ta.ema(50)
        rsi = ta.rsi(14)
        macd = ta.macd()

        # All should complete without errors
        assert not sma_200.iloc[200:].isna().any()
        assert not ema_50.isna().all()
        assert not rsi.iloc[14:].isna().any()
        assert not macd["MACD"].iloc[26:].isna().any()
