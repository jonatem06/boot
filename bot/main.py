import time
from bot.broker import Broker
from bot.analysis import Analysis
from bot.risk_management import RiskManagement
from bot.execution import Execution
from bot.strategy import Strategy

def main():
    print("Starting Trading Bot...")

    try:
        broker = Broker()
        initial_equity = broker.get_balance()
        print(f"Initial Equity: {initial_equity}")

        analysis = Analysis(broker.data_client)
        risk_mgmt = RiskManagement(initial_equity)
        execution = Execution(broker.trading_client)

        strategy = Strategy(broker, analysis, risk_mgmt, execution)

        symbols_to_watch = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

        while True:
            print("Running cycle...")
            strategy.run_cycle(symbols_to_watch)
            print("Cycle complete. Waiting 1 hour.")
            time.sleep(3600) # Run every hour

    except Exception as e:
        print(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()
