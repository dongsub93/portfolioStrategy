import sys,os
import datetime
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
    # Get dictionary of {'Coorp':'Code'} dictionary.
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
    tempPrice = getPrice(kospiDict['삼성전자'])
    print (tempPrice)

    tempPrice.to_csv('./00_data/00_1_pricesData/{code}_{start}_{end}.csv'
                    .format(code=kospiDict['삼성전자']
                            ,start=str(datetime.date.today()-datetime.timedelta(days=365))
                            ,end=str(datetime.date.today()))
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
    tempFinance = getFiance('005930')
    print (tempFinance)

    sys.exit(0)

