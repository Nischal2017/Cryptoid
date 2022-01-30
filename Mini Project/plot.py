import time
import sqlalchemy
import pandas as pd
import plotly.express as px

def update():
    engine = sqlalchemy.create_engine("sqlite:///BTCUSDTstream.db")
    df = pd.read_sql('BTCUSDT',engine)
    fig = px.line(df, x='Time', y="Price")
    fig.write_html("index.html")

while True:
    time.sleep(10)
    print("Updated")
    update()