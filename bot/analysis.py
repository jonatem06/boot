import pandas as pd
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

class Analysis:
    def __init__(self, data_client):
        self.data_client = data_client

    def get_indicators(self, symbol):
        # Fetch last 50 bars
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=datetime.now() - timedelta(days=70)
        )
        bars = self.data_client.get_stock_bars(request_params)
        df = bars.df

        # Simple Moving Average
        df['SMA_20'] = df['close'].rolling(window=20).mean()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        return df

    def analyze_order_flow(self, symbol):
        """Placeholder for order flow analysis"""
        # In a real scenario, we would use trades and quotes data
        print(f"Analyzing order flow for {symbol}...")
        return "NEUTRAL"

    def get_sentiment(self, symbol):
        """Placeholder for AI-based sentiment analysis"""
        print(f"Analyzing sentiment for {symbol} using IA...")
        return 0.5  # Neutral sentiment 0 to 1

    def generate_signal(self, symbol):
        df = self.get_indicators(symbol)
        last_rsi = df['RSI'].iloc[-1]
        last_close = df['close'].iloc[-1]
        sma_20 = df['SMA_20'].iloc[-1]

        sentiment = self.get_sentiment(symbol)

        if last_rsi < 30 and last_close > sma_20 and sentiment > 0.6:
            return "BUY", last_close
        elif last_rsi > 70:
            return "SELL", last_close

        return "HOLD", last_close
