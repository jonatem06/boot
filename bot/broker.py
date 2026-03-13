from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from bot.config import Config

class Broker:
    def __init__(self):
        self.trading_client = TradingClient(
            api_key=Config.ALPACA_API_KEY,
            secret_key=Config.ALPACA_SECRET_KEY,
            paper=(Config.TRADING_MODE == "PAPER")
        )
        self.data_client = StockHistoricalDataClient(
            api_key=Config.ALPACA_API_KEY,
            secret_key=Config.ALPACA_SECRET_KEY
        )

    def get_account_info(self):
        return self.trading_client.get_account()

    def get_balance(self):
        account = self.get_account_info()
        return float(account.equity)

    def get_buying_power(self):
        account = self.get_account_info()
        return float(account.buying_power)

    def get_positions(self):
        return self.trading_client.get_all_positions()

    def get_position_for_symbol(self, symbol):
        try:
            return self.trading_client.get_open_position(symbol)
        except Exception:
            return None
