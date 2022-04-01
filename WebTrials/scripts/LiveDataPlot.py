from distutils.log import debug
import time
import sqlalchemy
import pandas as pd
import plotly.express as px
import logging

logging.basicConfig(filename='plotLogs.txt', filemode='a',level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

def update():
    engine = sqlalchemy.create_engine("sqlite:///BTCUSDTstream.db")
    df = pd.read_sql('BTCUSDT',engine)
    fig = px.line(df, x='Time', y="Price")
    fig.write_html("../website/static/LivePlot.html")

while True:
    time.sleep(10)
    logging.info('Updated plot successfully.')
    update()