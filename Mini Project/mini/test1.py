import pandas as pd
import sqlalchemy
from binance import Client, BinanceSocketManager
import json 

file1 = open("api.json", "r")
auth = json.load(file1)
keys=auth['Testnet1']
