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

        # Mock Session and Trade to avoid DB issues
        with patch('bot.strategy.Session'), patch('bot.strategy.func'):
            self.strategy = Strategy(
                self.mock_broker,
                self.mock_analysis,
                self.mock_risk_mgmt,
                self.mock_execution
            )
            self.strategy.total_profit = 0 # reset from setup _load_memory

    def test_fractional_buy_logging(self):
        self.mock_broker.get_balance.return_value = 1000.0
        self.mock_analysis.generate_signal.return_value = ("BUY", 150.0)
        self.mock_risk_mgmt.check_drawdown.return_value = True
        self.mock_risk_mgmt.calculate_position_size.return_value = 0.6667
        self.mock_broker.get_position_for_symbol.return_value = None
        self.mock_risk_mgmt.should_stop_loss.return_value = False

        with patch('bot.strategy.log_trade') as mock_log:
            self.strategy.run_cycle(["AAPL"])

            # Use assert_called() and check args manually for precision issues if needed
            args, _ = mock_log.call_args
            self.assertEqual(args[0], 1000.0)
            self.assertEqual(args[2], 100.005)
            self.assertEqual(args[5], "BUY")

    def test_fractional_sell_profit(self):
        self.mock_broker.get_balance.return_value = 1000.0
        self.mock_analysis.generate_signal.return_value = ("SELL", 200.0)
        self.mock_risk_mgmt.check_drawdown.return_value = True
        self.mock_risk_mgmt.should_stop_loss.return_value = False

        mock_position = MagicMock()
        mock_position.avg_entry_price = "150.0"
        mock_position.qty = "0.5"
        self.mock_broker.get_position_for_symbol.return_value = mock_position

        with patch('bot.strategy.log_trade') as mock_log:
            self.strategy.run_cycle(["AAPL"])
            self.assertEqual(self.strategy.total_profit, 25.0)
            mock_log.assert_any_call(1000.0, 1000.0, 100.0, "AAPL", 0, "SELL", profit=25.0)

if __name__ == '__main__':
    unittest.main()
