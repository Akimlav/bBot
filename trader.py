#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 12:11:24 2021

@author: akimlavrinenko
"""

from apscheduler.schedulers.blocking import BlockingScheduler
import time,datetime
from datetime import date
from strategies import *
from binanceFuncLib import *



# coin1List = ['BTC', 'ETH', 'BCH', 'BNB', 'XLM', 'MATIC', 'DOGE', 'SOL', 'DOT', 'ETC', 'XRP', 'SHIB', 'ADA', 'NEO', 'ONE', 'LTC']
coin1List = ['SOL', 'XLM', 'MATIC', 'DOGE', 'DOT', 'XRP', 'ADA', 'AVAX', 'MANA', 'SAND', 'CAKE', 'ENJ', 'LUNA', 'TRX', 'ATOM', 'CRV', 'SUSHI', 'LUNA', 'RUNE', 'UNI', 'ADA', 'WAVES']

# coin1List = ['XRP']
coin2List = ['USDT']
#coin2List = ['BTC']

startTime = int((time.mktime(datetime.datetime.today().timetuple()))*1000)# - 8*3600000
# startTime = 1637400000000
            # 1637412233042
              
print(startTime)
def loop():
    start_time = time.time()
    for coin2 in coin2List:
        for coin1 in coin1List:
            today = datetime.datetime.now()
            print()
            print("Time: ", today)
            scalpingGreenMarket(coin1, coin2, 1, 12, startTime)
            time.sleep(5)
    print('___________________________________________')
    print("--- %s seconds ---" % round((time.time() - start_time),3 ))


def main():
    while True:
        loop()


if __name__ == "__main__":
    main()


print('___________________________________________')
print("--- %s seconds ---" % round((time.time() - start_time),3 ))
