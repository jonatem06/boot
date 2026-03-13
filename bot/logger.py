import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Trade(Base):
    __tablename__ = 'trade'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    balance_before = Column(Float)
    balance_after = Column(Float)
    cost = Column(Float)
    symbol = Column(String)
    percentage = Column(Float)
    side = Column(String) # 'BUY' or 'SELL'
    profit = Column(Float, default=0.0) # Added profit column

# Setup database
engine = create_engine('sqlite:///trades.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def log_trade(balance_before, balance_after, cost, symbol, percentage, side, profit=0.0):
    session = Session()
    new_trade = Trade(
        balance_before=balance_before,
        balance_after=balance_after,
        cost=cost,
        symbol=symbol,
        percentage=percentage,
        side=side,
        profit=profit
    )
    session.add(new_trade)
    session.commit()
    session.close()
    print(f"Logged {side} for {symbol} at cost {cost}. Profit: {profit}")
