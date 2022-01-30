#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sqlalchemy
import pandas as pd
from binance.client import Client
import json


# In[2]:


file = open("api.json", "r")
json1 = json.load(file)
json1 = json1["Testnet1"]


# In[3]:


client = Client(json1['api-key'],json1['secret-key'])


# In[4]:


client.API_URL = 'https://testnet.binance.vision/api'


# In[5]:


engine = sqlalchemy.create_engine('sqlite:///BTCUSDTstream.db')


# In[6]:


def strategy(entry, lookback, qty, openPosition = False):
    while True:
        df = pd.read_sql('BTCUSDT', engine)
        lookbackperiod = df.iloc[-lookback:]
        cumret = (lookbackperiod.Price.pct_change() + 1).cumprod() - 1
        if not openPosition:
            if cumret[cumret.last_valid_index()] > entry:
                order = client.create_order(symbol = 'BTCUSDT',
                                                side = 'BUY',
                                                type = 'MARKET',
                                                quantity = qty)
                print(order)
                frame = createBuySellFrame(order)
                frame.to_sql('BUY_ORDERS', engine, if_exists = 'append', index = False)
                openPosition = True
                break
    if openPosition:
        while True:
            df = pd.read_sql('BTCUSDT', engine)
            sincebuy = df.loc[df.Time > pd.to_datetime(order['transactTime'], unit = 'ms')]
            if len(sincebuy) > 1:
                sincebuyret = (sincebuy.Price.pct_change() + 1).cumprod() -1
                last_entry = sincebuyret[sincebuyret.last_valid_index()]
                if last_entry > 0.0015 or last_entry < -0.0015:
                    order = client.create_order(symbol = 'BTCUSDT',
                                                    side = 'SELL',
                                                    type = 'MARKET',
                                                    quantity = qty)
                    print(order)
                    frame = createBuySellFrame(order)
                    frame.to_sql('SELL_ORDERS', engine, if_exists = 'append', index = False)
                    break


# In[7]:


def createBuySellFrame(order):
    df = pd.DataFrame([order])
    df = df.loc[:,['symbol','orderId','transactTime','origQty','cummulativeQuoteQty']]
    df.columns = ['Symbol','Order_ID','Time','Quantity','Price']
    df.Price = df.Price.astype(float)
    df.Quantity = df.Quantity.astype(float)
    df.Time = pd.to_datetime(df.Time, unit ='ms')
    return df


strategy(0.0,60,0.01)
# In[8]:

