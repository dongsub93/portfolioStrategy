import sys,os
import datetime
from datetime import date
from datetime import timedelta
import crawler_v0
from crawler_v0 import *
import pandas as pd
import numpy as np
import urllib

if __name__ == "__main__":
    """
        This script demonstrates the usage of defined functions.
    """

    # Download the List of the KOSPI.
    # It returns Fails when it fails to download the data, otherwise return True.
    test = downloadMarketList('KOSPI')
    print ('Status of downloading the market data : ',test)
    # Get dictionary of {'Corp':'Code'} dictionary.
    # It requires to download the marketList using crawler_v0.downloadMarketList in a priory.
    kospiDict = getMarketDict('kospi')
    print (kospiDict['흥국화재'],type(kospiDict['흥국화재']))

    # Downliad the prices
    # The first argument is the code of a company,
    # while the second and the third are the first day and the last day of the data we will take, respectively.
    # As the default, it uses the date when the code is executed as the last day and takes one-year data.
    #
    # * example of full usage
    # > tempPrice = getPrice(kospiDict['삼성전자'],datetime.date(2020,3,10),datetime.date(2021.3.10))
    tempPrice = getPrice('069500',start=datetime.date(2020,1,1))
    print (tempPrice)
    
    tempPrice.to_csv('./00_data/1_pricesData/{code}_{start}-{end}.csv'
                    .format(code='069500'
                            ,start=str(tempPrice.iloc[-1]['날짜'])
                            ,end=str(tempPrice.iloc[0]['날짜']))
                    , encoding='UTF-8-SIG')

    """
        Iteration example over whole dictionary is given below.

    for key, value in kospiDict.items():
        print ('Download the price data of {company}(code={code}'.\
                format(company=key,code=value))
        tempPrice = getPrice(value)
        tempPrice.to_csv('./00_data/00_1_pricesData/{code}_{start}_{end}.csv'
                         .format(code=kospiDict['삼성전자']
                                 ,start=str(datetime.date.today()-datetime.timedelta(days=365))
                                 ,end=str(datetime.date.today()))
                           , encoding='UTF-8-SIG')
    """

    # Download the financial summary of the company.
#    tempFinance = getFiance('005930')
#    print (tempFinance)

    # Load the list of ETF
    etfList   = pd.read_csv('./00_data/0_marketList/etf_list.csv',encoding='euc-kr',dtype='str')
    ETFgears  = etfList.loc[:,'추적배수'].values # gearing rates of ETFs
    ETFassets = etfList.loc[:,'기초자산분류'].values # underlying assets of ETFs
    ETFmarkets= etfList.loc[:,'기초시장분류'].values # the market where ETFs are belonged 
    # Select the stock-based domestic ETFs with gear rate 1 
    bKrStockETF = np.logical_and(\
                    np.logical_and(ETFgears == '일반 (1)'\
                                    ,ETFassets == '주식')\
                    ,ETFmarkets == '국내')
    KrStockETF=etfList[bKrStockETF]
    KrStockETFcode = KrStockETF.loc[:,'단축코드'].values
    # Select the bond-based domestic ETFs with gear rate 1 
    bKrBondETF = np.logical_and(\
                    np.logical_and(ETFgears == '일반 (1)'\
                                    ,ETFassets == '채권')\
                    ,ETFmarkets == '국내')
    KrBondETF=etfList[bKrBondETF]
    KrBondETFcode = KrBondETF.loc[:,'단축코드'].values

    for code in KrStockETFcode[:5]:
        while len(code) < 6:
            code = '0'+code
        try:
            priceDf = getPrice(code,datetime.date(1900,1,1))
            priceDf.to_csv('./00_data/1_pricesData/0_stockETF/{code}.csv'.format(code=code)\
                            ,encoding='UTF-8-SIG')
        except:
            print ('Failed to download data for ',code)
            continue

    for code in KrBondETFcode[:5]:
        while len(code) < 6:
            code = '0'+code
        try:
            priceDf = getPrice(code,datetime.date(1900,1,1))
            priceDf.to_csv('./00_data/1_pricesData/1_bondETF/{code}.csv'.format(code=code)\
                   ,encoding='UTF-8-SIG')
        except:
            print ('Failed to download data for ',code)
            continue
    
    # Example implementation of absolute momentum strategy
    import strategies_v0
    from strategies_v0 import absMomentumStrategy
    print ([KrBondETFcode[0],KrStockETFcode[0]])
    test0 = absMomentumStrategy()
    test0.setStoragePath('./00_data/1_pricesData/')
    test0.initialisePortfolio(initDate=datetime.date(1900,1,1),rebalPeriod=datetime.timedelta(days=7),initVal=100000000,bondCode=KrBondETFcode[0],stockCode=KrStockETFcode[0],storageDir='./00_data/1_pricesData',allowFrac=False)
    test0.verbInitialCond()
    
    test0.elapse(interval=datetime.timedelta(days=365))
    print ('date       : ', test0.date)
    print ('total value: ', test0.portfolioValue, '(initial value : {iv}({r}))'.format(iv=test0.initVal,r=-1+test0.portfolioValue/test0.initVal))
    print ('# stock    : ', test0.nStock,'(total stock price = {p})'.format(p = test0.stock))
    print ('# bond     : ', test0.nBond,'(total bond price = {p})'.format(p=test0.bond))
    print ('total cash : ', test0.cash)
    sys.exit(0)

