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

        with patch('bot.strategy.Session'), patch('bot.strategy.func'):
            self.strategy = Strategy(
                self.mock_broker,
                self.mock_analysis,
                self.mock_risk_mgmt,
                self.mock_execution
            )
            self.strategy.total_profit = 0

    def test_fractional_min_qty_rule(self):
        self.mock_broker.get_balance.return_value = 100.0
        self.mock_analysis.generate_signal.return_value = ("BUY", 20000.0)
        self.mock_risk_mgmt.check_drawdown.return_value = True

        with patch('bot.config.Config.ALLOW_FRACTIONAL_SHARES', True):
            from bot.risk_management import RiskManagement
            rm = RiskManagement(100.0)
            qty = rm.calculate_position_size(100.0, 20000.0)
            self.assertEqual(qty, 0)

    def test_fractional_valid_qty_rule(self):
        with patch('bot.config.Config.ALLOW_FRACTIONAL_SHARES', True):
            from bot.risk_management import RiskManagement
            rm = RiskManagement(1000.0)
            qty = rm.calculate_position_size(1000.0, 150.0)
            self.assertEqual(qty, 0.6667)

    def test_logging_with_quantity(self):
        self.mock_broker.get_balance.return_value = 1000.0
        self.mock_analysis.generate_signal.return_value = ("BUY", 150.0)
        self.mock_risk_mgmt.check_drawdown.return_value = True
        self.mock_risk_mgmt.calculate_position_size.return_value = 0.6667
        self.mock_broker.get_position_for_symbol.return_value = None
        self.mock_risk_mgmt.should_stop_loss.return_value = False

        with patch('bot.strategy.log_trade') as mock_log:
            self.strategy.run_cycle(["AAPL"])
            args, kwargs = mock_log.call_args
            # balance_before, balance_after, cost, symbol, percentage, side
            self.assertEqual(args[0], 1000.0)
            self.assertEqual(args[2], 100.005)
            self.assertEqual(args[5], "BUY")
            self.assertEqual(kwargs['quantity'], 0.6667)

if __name__ == '__main__':
    unittest.main()
