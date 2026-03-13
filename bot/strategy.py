import time
from bot.logger import log_trade
from bot.config import Config

class Strategy:
    def __init__(self, broker, analysis, risk_mgmt, execution):
        self.broker = broker
        self.analysis = analysis
        self.risk_mgmt = risk_mgmt
        self.execution = execution
        self.total_profit = 0
        self.dividend_stocks = ["KO", "PEP", "T", "VZ", "XOM"] # Example dividend stocks
        self.owned_dividend_stocks = {} # symbol -> {entry_price, qty}

    def run_cycle(self, symbols):
        current_equity = self.broker.get_balance()
        self.risk_mgmt.update_initial_equity(current_equity)

        if not self.risk_mgmt.check_drawdown(current_equity):
            print("ALERT: Max drawdown reached. Stopping trading.")
            return

        for symbol in symbols:
            # Skip if it's a dividend stock we are holding with the 50% rule
            if symbol in self.owned_dividend_stocks:
                self.manage_dividend_stock(symbol)
                continue

            signal, price = self.analysis.generate_signal(symbol)

            # Risk Management: Stop Loss Check
            position = self.broker.get_position_for_symbol(symbol)
            if position:
                entry_price = float(position.avg_entry_price)
                if self.risk_mgmt.should_stop_loss(entry_price, price):
                    print(f"Stop loss triggered for {symbol}")
                    self.sell_and_track_profit(symbol, position.qty, price, entry_price)
                    continue

            if signal == "BUY":
                if not position: # Don't buy if we already have a position
                    qty = self.risk_mgmt.calculate_position_size(current_equity, price)
                    if qty > 0:
                        balance_before = current_equity
                        self.execution.buy_market(symbol, qty)
                        time.sleep(1) # Wait for order to fill
                        new_equity = self.broker.get_balance()
                        cost = qty * price
                        log_trade(balance_before, new_equity, cost, symbol, (cost/balance_before)*100)
                        print(f"Bought {qty} of {symbol}")

            elif signal == "SELL":
                if position:
                    self.sell_and_track_profit(symbol, position.qty, price, float(position.avg_entry_price))

        # Check for profit reinvestment
        if self.total_profit >= Config.DIVIDEND_REINVEST_THRESHOLD:
            self.buy_dividend_stock()

    def sell_and_track_profit(self, symbol, qty, current_price, entry_price):
        profit = (current_price - entry_price) * float(qty)
        self.total_profit += profit
        self.execution.sell_market(symbol, qty)
        print(f"Sold {symbol}. Profit from trade: {profit}. Total profit accumulated: {self.total_profit}")

    def buy_dividend_stock(self):
        # Pick one from the list
        symbol = self.dividend_stocks[0]
        current_equity = self.broker.get_balance()
        _, price = self.analysis.generate_signal(symbol)
        qty = self.risk_mgmt.calculate_position_size(current_equity, price)

        if qty > 0:
            balance_before = current_equity
            self.execution.buy_market(symbol, qty)
            self.total_profit -= Config.DIVIDEND_REINVEST_THRESHOLD
            self.owned_dividend_stocks[symbol] = {"entry_price": price, "qty": qty}

            new_equity = self.broker.get_balance()
            cost = qty * price
            log_trade(balance_before, new_equity, cost, symbol, (cost/balance_before)*100)
            print(f"Profit reinvested: Bought dividend stock {symbol}")

    def manage_dividend_stock(self, symbol):
        data = self.owned_dividend_stocks[symbol]
        _, current_price = self.analysis.generate_signal(symbol)

        # Only sell if it gained 50%
        if current_price >= data["entry_price"] * Config.DIVIDEND_HOLD_PROFIT_TARGET:
            self.execution.sell_market(symbol, data["qty"])
            del self.owned_dividend_stocks[symbol]
            print(f"Target reached! Sold dividend stock {symbol} for 50%+ profit.")
