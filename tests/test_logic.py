import unittest
from unittest.mock import MagicMock, patch
from bot.strategy import Strategy
from bot.config import Config

class TestBotLogic(unittest.TestCase):
    def setUp(self):
        self.mock_broker = MagicMock()
        self.mock_broker.get_positions.return_value = []
        self.mock_analysis = MagicMock()
        self.mock_risk_mgmt = MagicMock()
        self.mock_execution = MagicMock()

        with patch('bot.strategy.Session'):
            self.strategy = Strategy(
                self.mock_broker,
                self.mock_analysis,
                self.mock_risk_mgmt,
                self.mock_execution
            )

    def test_buy_logging_side(self):
        self.mock_broker.get_balance.return_value = 10000.0
        self.mock_analysis.generate_signal.return_value = ("BUY", 150.0)
        self.mock_risk_mgmt.check_drawdown.return_value = True
        self.mock_risk_mgmt.calculate_position_size.return_value = 10
        self.mock_broker.get_position_for_symbol.return_value = None
        self.mock_risk_mgmt.should_stop_loss.return_value = False

        with patch('bot.strategy.log_trade') as mock_log:
            self.strategy.run_cycle(["AAPL"])
            mock_log.assert_called_with(10000.0, 10000.0, 1500.0, "AAPL", 15.0, "BUY")

    def test_dividend_buy_insufficient_funds(self):
        # accumulated profit high enough
        self.strategy.total_profit = 2000

        # Equity is 10000
        self.mock_broker.get_balance.return_value = 10000.0
        # Dividend stock price 6000, 1 qty -> cost 6000
        # Remaining would be 4000 (which is < 50% of 10000)
        self.mock_analysis.generate_signal.return_value = ("HOLD", 6000.0)
        self.mock_risk_mgmt.calculate_position_size.return_value = 1

        self.strategy.buy_dividend_stock()

        # Should NOT have bought
        self.mock_execution.buy_market.assert_not_called()
        self.assertEqual(self.strategy.total_profit, 2000)

    def test_dividend_buy_sufficient_funds(self):
        self.strategy.total_profit = 2000
        self.mock_broker.get_balance.return_value = 10000.0
        # Cost 1000, remaining 9000 (> 5000)
        self.mock_analysis.generate_signal.return_value = ("HOLD", 100.0)
        self.mock_risk_mgmt.calculate_position_size.return_value = 10

        with patch('bot.strategy.log_trade'):
            self.strategy.buy_dividend_stock()

            self.mock_execution.buy_market.assert_called_once()
            self.assertEqual(self.strategy.total_profit, 2000 - Config.DIVIDEND_REINVEST_THRESHOLD)

if __name__ == '__main__':
    unittest.main()
