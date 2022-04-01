import sqlalchemy
from sqlalchemy.sql import text

engine = sqlalchemy.create_engine("sqlite:///BTCUSDTstream.db")
with engine.connect() as con:
    statement = text("""DELETE FROM BTCUSDT WHERE SYMBOL = 'BTCUSDT'""")
    con.execute(statement)

