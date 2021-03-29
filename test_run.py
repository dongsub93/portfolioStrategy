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
    """#######################################################
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
    
    tempPrice.to_csv('./00_data/1_pricesData/1_stock/{code}_{start}-{end}.csv'
                    .format(code='069500'
                            ,start=str(tempPrice.iloc[-1]['날짜'])
                            ,end=str(tempPrice.iloc[0]['날짜']))
                    , encoding='UTF-8-SIG')
    """#######################################################
    """
        Iteration example over whole dictionary is given below.

    for key, value in kospiDict.items():
        print ('Download the price data of {company}(code={code}'.\
                format(company=key,code=value))
        tempPrice = getPrice(value)
        tempPrice.to_csv('./00_data/1_pricesData/1_stock/{code}_{start}_{end}.csv'
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
    
    for code in KrStockETFcode[:10]:
        while len(code) < 6:
            code = '0'+code
        try:
            priceDf = getPrice(code,datetime.date(1900,1,1))
            priceDf.to_csv('./00_data/1_pricesData/0_ETF/{code}.csv'.format(code=code)\
                            ,encoding='UTF-8-SIG')
        except:
            print ('Failed to download data for ',code)
            continue
    """#######################################################
    for code in KrBondETFcode[:5]:
        while len(code) < 6:
            code = '0'+code
        try:
            priceDf = getPrice(code,datetime.date(1900,1,1))
            priceDf.to_csv('./00_data/1_pricesData/0_ETF/{code}.csv'.format(code=code)\
                   ,encoding='UTF-8-SIG')
        except:
            print ('Failed to download data for ',code)
            continue
    """#######################################################
    # Example implementation of absolute momentum strategy
    import strategies.absMomentum_v1
    from strategies.absMomentum_v1 import absMomentumStrategy
    print ([KrBondETFcode[0],KrStockETFcode[0]])
    test0 = absMomentumStrategy()
    test0.setStoragePath('./00_data/1_pricesData/0_ETF')
    test0.initialisePortfolio(initDate=datetime.date(1900,1,1)\
                            ,rebalPeriod=datetime.timedelta(days=7)\
                            ,initVal=100000000\
                            ,bondCode=KrBondETFcode[0],stockCode=KrStockETFcode[0]\
                            ,storageDir='./00_data/1_pricesData'\
                            ,allowFrac=False)
    test0.verbInitialCond()
#    sys.exit(0)
#    test0.elapse(interval=datetime.timedelta(days=365))
    test0.verbStatus()
    test0History = test0.getHistory(start=datetime.date(2019,11,2),end=datetime.date(2021,3,20))
    
    print (test0History[0:20])

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import aux_functions
    from aux_functions import *

    test0_fig, test0_ax = drawHistory(test0History)
    plt.savefig('./99_tempOutput/example_test0.png',dpi=test0_fig.dpi, bbox_inches='tight')

    import strategies.momentum_v0
    from strategies.momentum_v0 import momentumStrategy
    test0new = momentumStrategy()
    test0new.setStoragePath('./00_data/1_pricesData/0_ETF')
    test0new.initialisePortfolio(initDate=datetime.date(1900,1,1)\
                            ,rebalPeriod=datetime.timedelta(days=7)\
                            ,rebalScope =datetime.timedelta(days=7)\
                            ,initVal=100000000\
                            ,assetCodes=[KrBondETFcode[0],KrStockETFcode[0]]
                            ,assetWeights=[1.0,0.0]
                            ,storageDir='./00_data/1_pricesData/0_ETF'\
                            ,allowFrac=False)
    test0new.verbInitialCond()
    test0new.verbStatus()
    test0newHistory = test0new.getHistory(start=datetime.date(2019,11,2),end=datetime.date(2021,3,20))
    test0new.verbStatus()
    test0new_fig, test0new_ax = drawHistory(test0newHistory)
    plt.savefig('./99_tempOutput/example_test0new.png',dpi=test0new_fig.dpi, bbox_inches='tight')
    
    test1 = momentumStrategy()
    test1.setStoragePath('./00_data/1_pricesData/0_ETF')
    test1.initialisePortfolio(initDate=datetime.date(1900,1,1)\
                            ,rebalPeriod=datetime.timedelta(days=7)\
                            ,rebalScope =datetime.timedelta(days=7)\
                            ,initVal=100000000\
                            ,assetCodes=[KrBondETFcode[0],KrStockETFcode[0],KrStockETFcode[1]]
                            ,assetWeights=[0.5,0.3,0.2]
                            ,storageDir='./00_data/1_pricesData/0_ETF'\
                            ,allowFrac=False)
    test1.verbInitialCond()
    test1.verbStatus()
    test1History = test1.getHistory(start=datetime.date(2019,11,2))
    test1.verbStatus()
    test1_fig, test1_ax = drawHistory(test1History)
    plt.savefig('./99_tempOutput/example_test1.png',dpi=test1_fig.dpi, bbox_inches='tight')

    import strategies.modifiedMomentum_v0
    from strategies.modifiedMomentum_v0 import modifiedMomentumStrategy
    import strategies.fixedWeights_v0
    from strategies.fixedWeights_v0 import fixedWeightsStrategy

    test2 = momentumStrategy()
    test2.initialisePortfolio(initDate=datetime.date(1900,1,1)\
                            ,rebalPeriod=datetime.timedelta(days=7)\
                            ,rebalScope =datetime.timedelta(days=7)\
                            ,initVal=100000000\
                            ,assetCodes=[KrBondETFcode[2],KrStockETFcode[3],KrStockETFcode[4]\
                                        ,KrStockETFcode[5],KrStockETFcode[6],KrStockETFcode[7]]\
                            ,assetWeights=[0.5,0.2,0.1\
                                        ,0.05,0.03,0.02]\
                            ,storageDir='./00_data/1_pricesData/0_ETF'\
                            ,allowFrac=False)
    test2.verbStatus()
    test2History = test2.getHistory(start=datetime.date(2019,11,2))
    test2_fig, test2_ax = drawHistory(test2History)
    plt.savefig('./99_tempOutput/example_test2.png',dpi=test2_fig.dpi, bbox_inches='tight')

    test3 = modifiedMomentumStrategy()
    test3.initialisePortfolio(initDate=datetime.date(1900,1,1)\
                            ,rebalPeriod=datetime.timedelta(days=7)\
                            ,rebalScope =datetime.timedelta(days=7)\
                            ,initVal=100000000\
                            ,assetCodes=[KrBondETFcode[2],KrStockETFcode[3],KrStockETFcode[4]\
                                        ,KrStockETFcode[5],KrStockETFcode[6],KrStockETFcode[7]]
                            ,storageDir='./00_data/1_pricesData/0_ETF'\
                            ,allowFrac=False)
    test3.verbStatus()
    test3History = test3.getHistory(start=datetime.date(2019,11,2))
    test3_fig, test3_ax = drawHistory(test3History)
    plt.savefig('./99_tempOutput/example_test3.png',dpi=test3_fig.dpi, bbox_inches='tight')
                            

    test4 = fixedWeightsStrategy()
    test4.initialisePortfolio(initDate=datetime.date(1900,1,1)\
                            ,rebalPeriod=datetime.timedelta(days=7)\
                            ,rebalScope =datetime.timedelta(days=7)\
                            ,initVal=100000000\
                            ,assetCodes=[KrBondETFcode[2],KrStockETFcode[3],KrStockETFcode[4]\
                                        ,KrStockETFcode[5],KrStockETFcode[6],KrStockETFcode[7]]
                            ,assetWeights=[0.17,0.17,0.17\
                                        ,0.17,0.16,0.16]
                            ,storageDir='./00_data/1_pricesData/0_ETF'\
                            ,allowFrac=False)
    test4.verbStatus()
    test4History = test4.getHistory(start=datetime.date(2019,11,2))
    test4_fig, test4_ax = drawHistory(test4History)
    plt.savefig('./99_tempOutput/example_test4.png',dpi=test4_fig.dpi, bbox_inches='tight')

    sys.exit(0)

