#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 17:15:10 2021

@author: akimlavrinenko
"""
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from acc import *
from binance.enums import *
from binanceFuncLib import *
import time,datetime
from datetime import datetime
import numpy as np

client = Client(api_key, api_secret)

def scalpingGreenMarket(coin1, coin2, nt, TS, startTime):# trading pair and number of simultanious trades
    
    if coin1 != coin2:
        pair = coin1 + coin2
        print(pair)
        coin2Balance = binanceFuncLib().coinBalance(coin2)
        sell = True
        print('-- Trying to buy ---')
        if coin2Balance > TS:
            newSellList, newBuyList, buy =  binanceFuncLib().buyPass(pair, startTime)
            print(coin2Balance, newBuyList, newSellList, 'buy', buy)
            if (len(newBuyList) <= nt) & (buy == True): #check the sellList, if it less than nt
                m, tickDec, stepDec, avg_price = binanceFuncLib().checkMarket(pair)
                print('MACD',np.round(m['macd_dif'],tickDec),',', 'RSI',np.round(m['stochRSI'], tickDec),'|',np.round(m['BBlow'], tickDec), np.round(m['BBhigh'], tickDec),'|', 'fast EMA ', np.round(m['fast_ema'],tickDec),',', 'avg p ',np.round(avg_price, tickDec))
                if (m['macd_dif']<-0.3) & (m['stochRSI']<=-0.45) & (m['BBlow']>avg_price) & (m['fast_ema']>avg_price):
                    print('I am buying!', 'MACD', m['macd_dif'], ', RSI', m['stochRSI'], m['fast_ema'], avg_price )
                    p = (avg_price*0.9965)
                    q = round((TS / p), stepDec)
                    buyPrice = round(p, tickDec)
                    print('avg price ',str(avg_price) , 'quantity ', str(q), ',','buy price ' + str(buyPrice), 'money spent', str(round((q*buyPrice), 2)))
                    order = binanceFuncLib().buyOrder(q, pair, buyPrice)
                    sell = False
                else:
                    print('Next time!')
        
        if sell == False:
            print('Just bought!')
        else:
            coin1Balance = binanceFuncLib().coinBalance(coin1)
            minQty = binanceFuncLib().minQty(pair)
            goSell = binanceFuncLib().tradePass(pair, startTime)
            print(coin1Balance, minQty, 'sell?', goSell)
            if (coin1Balance > minQty) & (goSell == True):
                m, tickDec, stepDec, avg_price = binanceFuncLib().checkMarket(pair)
                lastBuyPrice, q = binanceFuncLib().lastBuyPrice(pair, startTime)
                print('MACD ', np.round(m['macd_dif'], tickDec), ', RSI ', np.round(m['stochRSI'], tickDec), ', last buy price ', np.round(lastBuyPrice, tickDec), ', priceBB high ', np.round(m['BBhigh'], tickDec), ', avg p ', np.round(avg_price, tickDec))
                if (m['BBhigh'] < avg_price) & (avg_price > lastBuyPrice * 1.005) or avg_price > lastBuyPrice * 1.01: # or avg_price < float(lastBuyPrice) * 0.946:
                    print('I am going to sell!')
                    q = round(float(q[0]), stepDec)
                    print(avg_price)
                    sellPrice = round(avg_price, tickDec)
                    order = binanceFuncLib().sellMarketOrder(q, pair)
                    # orderList.append(order)
                    print(q, sellPrice)
                    print('Selling!', 'MACD ', str(m['macd_dif']), ', RSI ', str(m['stochRSI']), ', last buy price ', str(lastBuyPrice))
                    print('avg price ',str(avg_price) , 'quantity ', str(q), ',','sell price ' + str(sellPrice), 'money recieved', str(q*sellPrice))
        
            else:
                print('Not yet!')
