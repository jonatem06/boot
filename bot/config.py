import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TRADING_MODE = os.getenv("TRADING_MODE", "PAPER").upper() # 'PAPER' or 'LIVE'

    ALPACA_API_KEY = os.getenv(f"ALPACA_{TRADING_MODE}_API_KEY")
    ALPACA_SECRET_KEY = os.getenv(f"ALPACA_{TRADING_MODE}_SECRET_KEY")

    if TRADING_MODE == "LIVE":
        BASE_URL = "https://api.alpaca.markets"
    else:
        BASE_URL = "https://paper-api.alpaca.markets"

    # Risk settings
    MAX_POSITION_PERCENT = 0.10  # Max 10% of portfolio per stock
    MAX_DRAWDOWN_PERCENT = 0.20  # Stop trading if 20% drawdown
    ALLOW_FRACTIONAL_SHARES = True # Allow buying 0.5, 1.25 shares etc.

    # Strategy settings
    DIVIDEND_REINVEST_THRESHOLD = 1000  # Amount of profit before buying dividend stock
    DIVIDEND_HOLD_PROFIT_TARGET = 1.50 # 50% gain
