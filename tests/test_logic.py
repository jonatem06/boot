import unittest
from unittest.mock import MagicMock, patch
from bot.strategy import Strategy
from bot.config import Config

class TestBotLogic(unittest.TestCase):
    def setUp(self):
        self.mock_broker = MagicMock()
        self.mock_analysis = MagicMock()
        self.mock_risk_mgmt = MagicMock()
        self.mock_execution = MagicMock()

        self.strategy = Strategy(
            self.mock_broker,
            self.mock_analysis,
            self.mock_risk_mgmt,
            self.mock_execution
        )

    def test_buy_logic(self):
        # Setup mocks
        self.mock_broker.get_balance.return_value = 10000.0
        self.mock_analysis.generate_signal.return_value = ("BUY", 150.0)
        self.mock_risk_mgmt.check_drawdown.return_value = True
        self.mock_risk_mgmt.calculate_position_size.return_value = 10
        self.mock_broker.get_position_for_symbol.return_value = None
        self.mock_risk_mgmt.should_stop_loss.return_value = False

        # Run cycle
        with patch('bot.strategy.log_trade') as mock_log:
            self.strategy.run_cycle(["AAPL"])

            # Verify execution was called
            self.mock_execution.buy_market.assert_called_with("AAPL", 10)
            # Verify log_trade was called
            mock_log.assert_called()

    def test_stop_loss_logic(self):
        self.mock_broker.get_balance.return_value = 10000.0
        self.mock_risk_mgmt.check_drawdown.return_value = True
        self.mock_analysis.generate_signal.return_value = ("HOLD", 140.0)

        # Mock existing position
        mock_position = MagicMock()
        mock_position.avg_entry_price = "150.0"
        mock_position.qty = "10"
        self.mock_broker.get_position_for_symbol.return_value = mock_position

        # Scenario: stop loss triggered
        self.mock_risk_mgmt.should_stop_loss.return_value = True

        self.strategy.run_cycle(["AAPL"])

        # Verify sell was called
        self.mock_execution.sell_market.assert_called_with("AAPL", "10")
        # Verify profit tracking (should be negative in this case)
        self.assertEqual(self.strategy.total_profit, (140.0 - 150.0) * 10)

    def test_profit_accumulation_and_dividend_buy(self):
        self.mock_broker.get_balance.return_value = 10000.0
        self.mock_risk_mgmt.check_drawdown.return_value = True
        self.mock_analysis.generate_signal.return_value = ("SELL", 200.0)
        self.mock_risk_mgmt.should_stop_loss.return_value = False
        self.mock_risk_mgmt.calculate_position_size.return_value = 10

        # Mock existing position
        mock_position = MagicMock()
        mock_position.avg_entry_price = "100.0"
        mock_position.qty = "20"
        self.mock_broker.get_position_for_symbol.return_value = mock_position

        # We need profit to reach Config.DIVIDEND_REINVEST_THRESHOLD
        # 1000 threshold
        # profit = (200 - 100) * 20 = 2000

        with patch('bot.strategy.log_trade'):
            self.strategy.run_cycle(["AAPL"])

            self.assertEqual(self.strategy.total_profit, 1000) # 2000 - 1000 spent
            self.mock_execution.buy_market.assert_any_call("KO", 10)

if __name__ == '__main__':
    unittest.main()
