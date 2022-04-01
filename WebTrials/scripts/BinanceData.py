#!/usr/bin/env python
# coding: utf-8

import asyncio
from binance import AsyncClient, BinanceSocketManager
from binance.client import Client
import pandas as pd
import sqlalchemy
import json
import time
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException

def createframe(msg):
    df = pd.DataFrame([msg])
    df = df.loc[:,['s','E','p']]
    df.columns = ['Symbol','Time','Price']
    df.Price = df.Price.astype(float)
    df.Time = pd.to_datetime(df.Time, unit ='ms')
    return df


file = open("api.json", "r")
dic1 = json.load(file)
json1 = dic1["Testnet1"]

engine = sqlalchemy.create_engine('sqlite:///BTCUSDTstream.db')

async def main():
    client = await AsyncClient.create(json1["api-key"],json1["secret-key"])
    client.API_URL = 'https://testnet.binance.vision/api'

    bsm = BinanceSocketManager(client,user_timeout=60)
    socket = bsm.trade_socket('BTCUSDT')

    async with socket as tscm:
        while True:
            try:
                await socket.__aenter__()
                msg = await socket.recv()
                frame = createframe(msg)
                frame.to_sql('BTCUSDT', engine, if_exists = 'append', index = False)
                print(frame)    
            except:
                bsm = BinanceSocketManager(client,user_timeout=60)
                socket = bsm.trade_socket('BTCUSDT')
                continue

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())