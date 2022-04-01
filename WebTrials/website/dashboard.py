from flask import Blueprint, flash, redirect, render_template,request, url_for
from flask_login import login_required, current_user
from . import db
from .models import User
import sqlalchemy
import pandas as pd
from binance.client import Client 
import time

dashboard = Blueprint('dashboard', __name__)
engine1 = sqlalchemy.create_engine('sqlite:///scripts/BTCUSDTstream.db')
df1 = pd.read_sql('BUY_ORDERS', engine1)
df2 = pd.read_sql('TRANSACTIONS', engine1)
df3 = pd.read_sql('BTCUSDT', engine1)
df4 = pd.read_sql('SELL_ORDERS', engine1)

@dashboard.route('/dash')
@login_required
def dash():
    return render_template("dashboard.html",user=current_user,df3=df3)

@dashboard.route('/orders')
@login_required
def orders():
    return render_template("orders.html", user=current_user,df1=df1,df4=df4)

@dashboard.route('/history')
@login_required
def history():
    print(df2)
    return render_template("history.html", user=current_user,df2=df2)
    

@dashboard.route('/trade', methods = ['GET', 'POST'])
@login_required
def trade():
    
    def strategy(entry, lookback, qty,json1, openPosition = False):
        client = Client(json1['api-key'],json1['secret-key'])
        client.API_URL = 'https://testnet.binance.vision/api'
        engine = sqlalchemy.create_engine('sqlite:///scripts/BTCUSDTstream.db')
        print("Connected to DB, Started Trade.")
        status = 1
        while True:
            
            if status:
                print("Position:Open")
                status=0
            
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
                    # transc = createTranscFrame(entry,lookback,quantity)
                    frame.to_sql('BUY_ORDERS', engine, if_exists = 'append', index = False)
                    # transc.to_sql('Transactions', engine, if_exists = 'append', index = False)
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
                        print("Position:Closed")
                        break
    
    def createBuySellFrame(order):
        df = pd.DataFrame([order])
        df = df.loc[:,['symbol','orderId','transactTime','origQty','cummulativeQuoteQty']]
        df.columns = ['Symbol','Order_ID','Time','Quantity','Price']
        df.Price = df.Price.astype(float)
        df.Quantity = df.Quantity.astype(float)
        df.Time = pd.to_datetime(df.Time, unit ='ms')
        return df

    # def createTranscFrame(entry,lookback,quantity):
    #     data = [entry,lookback,quantity]
    #     df = pd.DataFrame(data, columns = ['entry', 'lookback','quantity'])
    #     return df

    if request.method == 'POST':
        
        entry = float(request.form.get('entry'))
        lookback = int(request.form.get('lookback'))
        quantity = float(request.form.get('quantity'))
        curUsr = current_user.get_id()
        user = User.query.get(int(curUsr))
        json1={'api-key':user.apiK,'secret-key':user.secK}
        render_template("trade.html",user=current_user)
        time.sleep(5)
        strategy(entry,lookback,quantity,json1)
        return redirect(url_for('dashboard.orders'))        

    return render_template("trade.html", user=current_user)

#*1% of Bitcoin's value is $475, aim for a smaller change like 0.1% which is 47.5 or even better 0.05% which is $23