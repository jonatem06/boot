from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

class Execution:
    def __init__(self, trading_client):
        self.trading_client = trading_client

    def buy_market(self, symbol, qty):
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.GTC
        )
        return self.trading_client.submit_order(order_data=market_order_data)

    def sell_market(self, symbol, qty):
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC
        )
        return self.trading_client.submit_order(order_data=market_order_data)

    def buy_limit(self, symbol, qty, limit_price):
        limit_order_data = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY,
            limit_price=limit_price,
            time_in_force=TimeInForce.GTC
        )
        return self.trading_client.submit_order(order_data=limit_order_data)
