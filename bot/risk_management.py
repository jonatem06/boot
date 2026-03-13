from bot.config import Config

class RiskManagement:
    def __init__(self, initial_equity):
        self.initial_equity = initial_equity
        self.max_drawdown = Config.MAX_DRAWDOWN_PERCENT

    def check_drawdown(self, current_equity):
        drawdown = (self.initial_equity - current_equity) / self.initial_equity
        if drawdown >= self.max_drawdown:
            return False  # Drawdown limit reached
        return True

    def calculate_position_size(self, current_equity, stock_price):
        # Limit per position based on Config
        max_alloc = current_equity * Config.MAX_POSITION_PERCENT

        if Config.ALLOW_FRACTIONAL_SHARES:
            qty = max_alloc / stock_price
            return round(qty, 4) # Alpaca supports up to 9, but 4 is usually plenty
        else:
            qty = max_alloc // stock_price
            return int(qty)

    def should_stop_loss(self, entry_price, current_price, stop_loss_pct=0.05):
        if (entry_price - current_price) / entry_price >= stop_loss_pct:
            return True
        return False

    def update_initial_equity(self, new_equity):
        """If user deposits more money, we update initial equity for drawdown calculation"""
        if new_equity > self.initial_equity:
            self.initial_equity = new_equity
