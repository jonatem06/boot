import pandas as pd
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

class Analysis:
    def __init__(self, data_client):
        self.data_client = data_client

    def get_indicators(self, symbol):
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=datetime.now() - timedelta(days=70)
        )
        bars = self.data_client.get_stock_bars(request_params)
        df = bars.df

        if df.empty:
            return pd.DataFrame()

        # Handle MultiIndex if present
        if isinstance(df.index, pd.MultiIndex):
            df = df.xs(symbol, level=0)

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
        """Simulated Order Flow Analysis"""
        # In a real scenario, compare bid/ask volume
        print(f"Analyzing order flow for {symbol}...")
        return "BULLISH" # Simulated

    def get_sentiment(self, symbol):
        """Simulated AI Sentiment Analysis"""
        # In a real scenario, use NLP on news articles
        print(f"Analyzing sentiment for {symbol} using IA...")
        return 0.75 # Simulated positive sentiment

    def generate_signal(self, symbol):
        try:
            df = self.get_indicators(symbol)
            if df.empty:
                return "HOLD", 0

            last_close = df['close'].iloc[-1]
            last_rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
            sma_20 = df['SMA_20'].iloc[-1] if not pd.isna(df['SMA_20'].iloc[-1]) else last_close

            sentiment = self.get_sentiment(symbol)
            order_flow = self.analyze_order_flow(symbol)

            if last_rsi < 35 and last_close > (sma_20 * 0.98) and sentiment > 0.7:
                return "BUY", last_close
            elif last_rsi > 65 or (sentiment < 0.3):
                return "SELL", last_close

            return "HOLD", last_close # Always return current price
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")

        return "HOLD", 0
