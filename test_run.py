import os
import sys
import datetime
from datetime import date
from datetime import timedelta
import pandas as pd
import numpy as np
import urllib
from crawler import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from aux_functions import *
from strategies.portfolio import portfolio

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
    """
    #######################################################
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
    """
    #######################################################
    # Example implementation of momentum strategy
    assets_for_test = ['114100', '287300', '287310', '290080', '284980', '287320']

    test_momentum = portfolio(strategy='momentum',storage_dir='./00_data/1_pricesData/1_ETF')
    test_momentum.init_portfolio(init_date=datetime.date(1900,1,1)\
                                ,rebal_period   =datetime.timedelta(days=20)\
                                ,lookback_period=datetime.timedelta(days=60)\
                                ,rebal_gauge    =datetime.timedelta(days=1)\
                                ,init_val=100000000\
                                ,assets=assets_for_test
                                ,weights=[0.6, 0.2, 0.1, 0.05, 0.03, 0.02]
                                ,allow_frac=False
                                ,risk_free_rate='./00_data/1_pricesData/0_riskFree/KrBond30.csv'
                                ,tax_rate=0.00015
                                ,eval_bench=True
                                )
    test_momentum_history = test_momentum.get_history()
    test_momentum_fig, test_momentum_ax = draw_history(test_momentum_history)
    plt.savefig('./99_tempOutput/mom_{r}_{l}.png'\
            .format(r=int(test_momentum.rebal_period.days),l=int(test_momentum.lookback_period.days) )\
            ,dpi=test_momentum_fig.dpi,bbox_inches='tight')
    sys.exit(0)

