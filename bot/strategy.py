import time
from bot.logger import log_trade, Session, Trade
from bot.config import Config
from sqlalchemy import func

class Strategy:
    def __init__(self, broker, analysis, risk_mgmt, execution):
        self.broker = broker
        self.analysis = analysis
        self.risk_mgmt = risk_mgmt
        self.execution = execution
        self.total_profit = 0
        self.dividend_stocks = ["KO", "PEP", "T", "VZ", "XOM"]
        self.owned_dividend_stocks = {}
        self._load_memory()

    def _load_memory(self):
        print("Loading bot memory...")
        positions = self.broker.get_positions()
        for pos in positions:
            if pos.symbol in self.dividend_stocks:
                self.owned_dividend_stocks[pos.symbol] = {
                    "entry_price": float(pos.avg_entry_price),
                    "qty": float(pos.qty)
                }
                print(f"Memory: Recovered dividend stock {pos.symbol}")

        session = Session()
        result = session.query(func.sum(Trade.profit)).scalar()
        self.total_profit = float(result) if result else 0.0
        session.close()
        print(f"Memory: Recovered accumulated profit: {self.total_profit}")

    def run_cycle(self, symbols):
        current_equity = self.broker.get_balance()
        self.risk_mgmt.update_initial_equity(current_equity)

        if not self.risk_mgmt.check_drawdown(current_equity):
            print("ALERT: Max drawdown reached. Stopping trading.")
            return

        for symbol in list(self.owned_dividend_stocks.keys()):
            self.manage_dividend_stock(symbol)

        for symbol in symbols:
            if symbol in self.owned_dividend_stocks:
                continue

            signal, price = self.analysis.generate_signal(symbol)
            if price <= 0: continue

            position = self.broker.get_position_for_symbol(symbol)

            if position:
                entry_price = float(position.avg_entry_price)
                if self.risk_mgmt.should_stop_loss(entry_price, price):
                    print(f"Stop loss triggered for {symbol}")
                    self.sell_and_track_profit(symbol, position.qty, price, entry_price)
                    continue

            if signal == "BUY":
                if not position:
                    qty = self.risk_mgmt.calculate_position_size(current_equity, price)
                    if qty > 0:
                        balance_before = current_equity
                        self.execution.buy_market(symbol, qty)
                        time.sleep(1)
                        new_equity = self.broker.get_balance()
                        cost = qty * price
                        log_trade(balance_before, new_equity, cost, symbol, (cost/balance_before)*100, "BUY", quantity=qty)
                        print(f"Bought {qty} of {symbol}")

            elif signal == "SELL":
                if position:
                    self.sell_and_track_profit(symbol, position.qty, price, float(position.avg_entry_price))

        if self.total_profit >= Config.DIVIDEND_REINVEST_THRESHOLD:
            self.buy_dividend_stock()

    def sell_and_track_profit(self, symbol, qty, current_price, entry_price):
        balance_before = self.broker.get_balance()
        profit = (current_price - entry_price) * float(qty)
        self.total_profit += profit
        self.execution.sell_market(symbol, qty)
        time.sleep(1)
        balance_after = self.broker.get_balance()

        log_trade(balance_before, balance_after, current_price * float(qty), symbol, 0, "SELL", quantity=float(qty), profit=profit)
        print(f"Sold {symbol}. Profit: {profit}. Total profit: {self.total_profit}")

    def buy_dividend_stock(self):
        symbol = next((s for s in self.dividend_stocks if s not in self.owned_dividend_stocks), self.dividend_stocks[0])

        current_equity = self.broker.get_balance()
        _, price = self.analysis.generate_signal(symbol)

        if price > 0:
            qty = self.risk_mgmt.calculate_position_size(current_equity, price)
            cost = qty * price

            remaining_equity = current_equity - cost
            if remaining_equity < (current_equity * 0.5):
                print(f"Skipping dividend buy for {symbol}: insufficient extra money to maintain portfolio diversity.")
                return

            if qty > 0:
                balance_before = current_equity
                self.execution.buy_market(symbol, qty)
                reinvest_cost = Config.DIVIDEND_REINVEST_THRESHOLD
                self.total_profit -= reinvest_cost

                time.sleep(1)
                new_equity = self.broker.get_balance()
                log_trade(balance_before, new_equity, cost, symbol, (cost/balance_before)*100, "BUY", quantity=qty, profit=-reinvest_cost)
                self.owned_dividend_stocks[symbol] = {"entry_price": price, "qty": qty}
                print(f"Profit reinvested: Bought dividend stock {symbol}")

    def manage_dividend_stock(self, symbol):
        data = self.owned_dividend_stocks.get(symbol)
        if not data: return

        _, current_price = self.analysis.generate_signal(symbol)
        if current_price <= 0: return

        if current_price >= data["entry_price"] * Config.DIVIDEND_HOLD_PROFIT_TARGET:
            balance_before = self.broker.get_balance()
            profit = (current_price - data["entry_price"]) * float(data["qty"])
            self.total_profit += profit
            self.execution.sell_market(symbol, data["qty"])
            time.sleep(1)
            balance_after = self.broker.get_balance()

            log_trade(balance_before, balance_after, current_price * float(data["qty"]), symbol, 0, "SELL", quantity=float(data["qty"]), profit=profit)
            del self.owned_dividend_stocks[symbol]
            print(f"Target reached! Sold dividend stock {symbol} for 50%+ profit.")
