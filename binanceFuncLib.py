#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 17:17:02 2021

@author: akimlavrinenko
"""
import pandas as pd
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import numpy as np
from pyti.smoothed_moving_average import smoothed_moving_average as sma
from pyti.moving_average_convergence_divergence import moving_average_convergence_divergence as macd
from pyti.stochrsi import stochrsi as srsi
from pyti.exponential_moving_average import exponential_moving_average as ema
import math
import time,datetime
from acc import *
from binance.enums import *

client = Client(api_key, api_secret)

class binanceFuncLib:
    
    def buyOrder(self, quantity, symbol, price):
        try:
            print("sending buy order!")
            order = client.create_order(symbol=symbol, side=SIDE_BUY, type=ORDER_TYPE_LIMIT, timeInForce=TIME_IN_FORCE_GTC, quantity=quantity, price=price)
            print(order)
        except Exception as e:
            print("an exception occured - {}".format(e))
            return False
    
        return order

    def sellLimitOrder(self, quantity, symbol, price):
        try:
            print("sending sell order!")
            order = client.create_order(symbol=symbol, side=SIDE_SELL, type=ORDER_TYPE_LIMIT, timeInForce=TIME_IN_FORCE_GTC, quantity=quantity, price=price)
            print(order)
        except Exception as e:
            print("an exception occured - {}".format(e))
            return False
    
        return order
    
    def sellMarketOrder(self, quantity, symbol):
        try:
            print("sending sell order!")
            order = client.create_order(symbol=symbol, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=quantity)
            print(order)
        except Exception as e:
            print("an exception occured - {}".format(e))
            return False
    
        return order

    def checkMarket(self, coin):
        m5 = binanceFuncLib().data5m(coin, '1 day ago GMT+2', 'close')
        m5['slow_ema'] = ema(m5['close'].tolist(), 20)
        m5['fast_ema'] = ema(m5['close'].tolist(), 6)
        stDev = np.std(m5['close'])
        m5['BBlow'] = m5['slow_ema'] - 0.4*stDev
        m5['BBhigh'] = m5['slow_ema'] + 0.4*stDev
        m5['slow_ema_dim'] = m5['slow_ema']/m5['slow_ema'].max()
        m5['fast_ema_dim'] = m5['fast_ema']/m5['fast_ema'].max()
        m5['macd_dim'] = (m5['fast_ema_dim'] - m5['slow_ema_dim'])*200
        m5['signal_line'] = ema(m5['macd_dim'].tolist(), 9)
        m5['macd_dif'] = ((m5['macd_dim'] - m5['signal_line']))
        m5['avg'] = ((m5['high'] + m5['low'])/2)
        m5['stochRSI'] = (srsi(m5['close'].tolist(), 14))/100-0.5
        m5.fillna(-1,inplace=True)
        m = m5.iloc[-1]
        tickDec, stepDec = binanceFuncLib().check_decimals(coin)
        avg_price = round(binanceFuncLib().avgPrice5min(coin), tickDec)
        return m, tickDec, stepDec, avg_price
    
    def newOrders(self, pair, startTime):
        openOrders =  client.get_all_orders(symbol=pair)
        sell = []
        buy = []
        for order in openOrders:
            if (order['side'] == 'SELL') & (order['time'] > startTime) & (order['status'] == 'NEW' ):
                sell.append([order['symbol'], order['orderId'], order['time'], order['status'], order['price'], order['cummulativeQuoteQty'], order['executedQty'], order['origQty']])
            elif (order['side'] == 'BUY') & (order['time'] > startTime) & (order['status'] == 'NEW' ):
                buy.append([order['symbol'], order['orderId'], order['time'], order['status'], order['price'], order['cummulativeQuoteQty'], order['executedQty'], order['origQty']])
        return [sell, buy]

    def filledOrders(self, pair, startTime):
        openOrders =  client.get_all_orders(symbol=pair)
        sell = []
        buy = []
        for order in openOrders:
            if (order['side'] == 'SELL') & (order['time'] > startTime) & (order['status'] == 'FILLED' ):
                sell.append([order['symbol'], order['orderId'], order['time'], order['status'], order['price'], order['cummulativeQuoteQty'], order['executedQty'], order['origQty']])
            elif (order['side'] == 'BUY') & (order['time'] > startTime) & (order['status'] == 'FILLED' ):
                buy.append([order['symbol'], order['orderId'], order['time'], order['status'], order['price'], order['cummulativeQuoteQty'], order['executedQty'], order['origQty']])
        return [sell, buy]

    def tradePass(self, coin, startTime):
        go = False
        filledOrders =  client.get_all_orders(symbol=coin)
        buyOrder = []
        sellOrder = []
        for order in filledOrders:
            if (order['time'] > startTime) & (order['status'] == 'FILLED') & (order['side'] == 'BUY'):
                buyOrder.append([order['symbol'], order['orderId'], order['time'], order['status'], order['side'], order['price'],
                                order['cummulativeQuoteQty'], order['executedQty'], order['origQty']])
            elif (order['time'] > startTime) & (order['status'] == 'FILLED') & (order['side'] == 'SELL'):
                sellOrder.append([order['symbol'], order['orderId'], order['time'], order['status'], order['side'], order['price'],
                                order['cummulativeQuoteQty'], order['executedQty'], order['origQty']])
        print(len(buyOrder), len(sellOrder))
        if len(buyOrder) > 0:
            t1 = float(buyOrder[-1][2]) #time of last filled buy order
        else:
            t1 = 0
        
        if len(sellOrder) > 0:
            t2 = float(sellOrder[-1][2]) #time of last filled sell order
        else:
            t2 = 0
            
        if t1 > t2:
            go = True
        else:
            go = False
            
        return go
    
    def buyPass(self, pair, startTime):
        orders =  client.get_all_orders(symbol=pair)
        
        newSell = []
        newBuy = []
        filledSell = []
        filledBuy = []
        
        go = False
        for order in orders:
            if (order['side'] == 'SELL') & (order['time'] > startTime) & (order['status'] == 'NEW' ):
                newSell.append([order['symbol'], order['orderId'], order['time'], order['status'], order['price'], order['cummulativeQuoteQty'], order['executedQty'], order['origQty']])
            elif (order['side'] == 'BUY') & (order['time'] > startTime) & (order['status'] == 'NEW' ):
                newBuy.append([order['symbol'], order['orderId'], order['time'], order['status'], order['price'], order['cummulativeQuoteQty'], order['executedQty'], order['origQty']])
    
        print('new ', len(newBuy), len(newSell))
    
        for order in orders:
            if (order['time'] > startTime) & (order['status'] == 'FILLED') & (order['side'] == 'BUY'):
                filledBuy.append([order['symbol'], order['orderId'], order['time'], order['status'], order['side'], order['price'],
                                order['cummulativeQuoteQty'], order['executedQty'], order['origQty']])
            elif (order['time'] > startTime) & (order['status'] == 'FILLED') & (order['side'] == 'SELL'):
                filledSell.append([order['symbol'], order['orderId'], order['time'], order['status'], order['side'], order['price'],
                                order['cummulativeQuoteQty'], order['executedQty'], order['origQty']])
        
        print('filled', len(filledBuy), len(filledSell))
        
        if len(filledBuy) > 0:
            t1 = float(filledBuy[-1][2]) #time of last filled buy order
        else:
            t1 = 0
        
        if len(filledSell) > 0:
            t2 = float(filledSell[-1][2]) #time of last filled sell order
        else:
            t2 = 1
        
        if t1 <= t2:
            go = True
        else:
            go = False
    
        return newSell, newBuy, go
    
    
    def lastBuyPrice(self, pair, startTime):
        filledOrders =  client.get_all_orders(symbol = pair)
        
        lb = []
        for order in filledOrders:
            if (order['time'] > startTime) & (order['status'] == 'FILLED') & (order['side'] == 'BUY'):
                lb.append([order['symbol'], order['orderId'], order['time'], order['status'], order['side'], order['price'],
                                order['cummulativeQuoteQty'], order['executedQty'], order['origQty']])
            
        if len(lb) >= 2:
            lastBuyPrice = lb[-1][5]
            lastQ = ([lb[-1][7]])
        elif (len(lb) < 2) & (len(lb) >= 1):
            lastBuyPrice = lb[-1][5]
            lastQ = ([lb[-1][7]])
        else:
            info = client.get_symbol_info(pair)
            lastQ = float(info['filters'][2]['minQty'])
            m, tickDec, stepDec, avg_price = binanceFuncLib().checkMarket(pair)
            tickDec, stepDec = binanceFuncLib().check_decimals(pair)
            lastBuyPrice = round(binanceFuncLib().avgPrice5min(), tickDec)
            
        return float(lastBuyPrice), lastQ
    
    def coinBalance(self, coin):
        info = client.get_account()
        balance = info['balances']
        # stableBalance= list(filter(lambda balance: balance['asset'] == stableCoin , balance))
        symbolBalance = list(filter(lambda balance: balance['asset'] == coin, balance))
        symbolBalance = symbolBalance[0]['free']

        return float(symbolBalance)
    
    def check_decimals(self, coin):
        info = client.get_symbol_info(coin)
        
        tickSize = int(float(info['filters'][0]['tickSize'])*1e8)
        stepSize = int(float(info['filters'][2]['stepSize'])*1e8)
        
        tickDigits = int(8 - (math.log10(tickSize)))
        stepDigits = int(8 - (math.log10(stepSize)))

        return tickDigits, stepDigits
    
    def minQty(self, pair):
        info = client.get_symbol_info(pair)
        info2 = float(info['filters'][2]['minQty'])
        return info2
    
    def avgPrice5min(self, coin):
        avg_price = client.get_avg_price(symbol=coin)
        avg_price = float(avg_price['price'])
        return avg_price

    def binanceToPython(self, data):
        col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
        klines = pd.DataFrame(data)
        klines = klines.drop(range(6, 12), axis=1)
        klines.columns = col_names
        for col in col_names:
            klines[col] = klines[col].astype(float)
        return klines
    
    
    def data1d(self, coin, period, dct):
        
        klines = client.get_historical_klines(coin, Client.KLINE_INTERVAL_1DAY, period)
        p = binanceFuncLib().binanceToPython(klines)
        
        return (p)

    def data30m(self, coin, period, dct):
        
        klines = client.get_historical_klines(coin, Client.KLINE_INTERVAL_30MINUTE, period)
        p = binanceFuncLib().binanceToPython(klines)
        
        return (p)
    
    def data5m(self, coin, period, dct):
        
        klines = client.get_historical_klines(coin, Client.KLINE_INTERVAL_5MINUTE, period)
        p = binanceFuncLib().binanceToPython(klines)
        
        return (p)


    def plot(self, df, coin):
        # plot candlestick chart
        candle = go.Candlestick(
            x = df['time'],
            open = df['open'],
            close = df['close'],
            high = df['high'],
            low = df['low'],
            name = "Candlesticks")
        
        # plot MAs
        fsma = go.Scatter(
            x = df['time'],
            y = df['fast_sma'],
            name = "Fast SMA",
            line = dict(color = ('rgba(102, 207, 255, 50)')))
        
        ssma = go.Scatter(
            x = df['time'],
            y = df['slow_sma'],
            name = "Slow SMA",
            line = dict(color = ('rgba(255, 207, 102, 50)')))
        
        avg = go.Scatter(
            x = df['time'],
            y = df['avg'],
            name = 'avg',
            line = dict())
        fema = go.Scatter(
            x = df['time'],
            y = df['fast_ema'],
            name = "fema",
            line = dict())
        
        sema = go.Scatter(
            x = df['time'],
            y = df['slow_ema'],
            name = "sema",
            line = dict())

        data = [candle, ssma, fsma, avg, fema, sema]
        
                # style and display
        layout = go.Layout(title = coin)
        fig = go.Figure(data = data, layout = layout)
        
        plot(fig)
        fig.show()
    
