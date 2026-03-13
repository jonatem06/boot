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

        with patch('bot.strategy.Session'): # avoid DB in setup
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

    def test_sell_logging_side(self):
        self.mock_broker.get_balance.return_value = 12000.0
        self.mock_analysis.generate_signal.return_value = ("SELL", 200.0)
        self.mock_risk_mgmt.check_drawdown.return_value = True
        self.mock_risk_mgmt.should_stop_loss.return_value = False
        self.mock_risk_mgmt.calculate_position_size.return_value = 10

        mock_position = MagicMock()
        mock_position.avg_entry_price = "100.0"
        mock_position.qty = "10"
        self.mock_broker.get_position_for_symbol.return_value = mock_position

        with patch('bot.strategy.log_trade') as mock_log:
            self.strategy.run_cycle(["AAPL"])
            # side should be correct and profit should be (200-100)*10 = 1000
            mock_log.assert_any_call(12000.0, 12000.0, 2000.0, "AAPL", 0, "SELL", profit=1000.0)

    def test_memory_loading(self):
        mock_pos = MagicMock()
        mock_pos.symbol = "KO"
        mock_pos.avg_entry_price = "50.0"
        mock_pos.qty = "100"
        self.mock_broker.get_positions.return_value = [mock_pos]

        with patch('bot.strategy.Session'):
            strategy = Strategy(self.mock_broker, self.mock_analysis, self.mock_risk_mgmt, self.mock_execution)
            self.assertIn("KO", strategy.owned_dividend_stocks)
            self.assertEqual(strategy.owned_dividend_stocks["KO"]["entry_price"], 50.0)

if __name__ == '__main__':
    unittest.main()
