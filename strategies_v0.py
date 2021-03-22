import sys,os
import datetime
from datetime import date
from datetime import timedelta
import crawler_v0
from crawler_v0 import *
import pandas as pd
import numpy as np

class absMomentumStrategy:
    def __init__(self, initDate:datetime.date = datetime.date.today()\
                 ,initVal:float = 0,bondCode:str='', stockCode:str=''\
                 ,rebalPeriod:datetime.timedelta = datetime.timedelta(days=1)\
                 ,allowFrac:bool=True, storageDir:str='./'):
        self.initDate      = initDate
        self.initVal       = initVal
        self.bondCode      = bondCode
        self.stockCode     = stockCode
        self.rebalPeriod   = rebalPeriod
        self.allowFrac     = allowFrac
        self.storageDir    = storageDir
        self.date          = self.initDate
        self.portfolioValue= self.initVal
        """
        try:
            self.loadHistory()
            _bondInit = self.bondData.iloc[-1]['날짜']
            _stockInit= self.stockData.iloc[-1]['날짜']
            if self.initDate < _bondInit or self.initDate < _stockInit:
                print ('Initial point is even prior to the head of the data.')
                print ('Replace it with ',str(max(_bondInit,_stockInit)))
                self.initDate = max(_bondInit,_stockInit)
        except:
            print ('Cannot find the price data. Set the path to the storage first.')
        """
    
    def initialisePortfolio(self, initDate:datetime.date = datetime.date.today()\
                            ,initVal:float = 0, bondCode:str='', stockCode:str=''\
                            ,rebalPeriod:datetime.timedelta = datetime.timedelta(days=1)\
                            ,allowFrac:bool=True, storageDir:str='.'):
        self.initDate      = initDate
        self.initVal       = initVal
        self.bondCode      = bondCode
        self.stockCode     = stockCode
        self.rebalPeriod   = rebalPeriod
        self.allowFrac     = allowFrac
        self.storageDir    = storageDir
        self.date          = self.initDate
        self.portfolioValue= self.initVal
        try:
            self.loadHistory()
            _bondInit = self.bondData.iloc[-1]['날짜']
            _stockInit= self.stockData.iloc[-1]['날짜']
            if self.initDate < _bondInit or self.initDate < _stockInit:
                print ('Initial point is even prior to the head of the data. Replace it with ',str(max(_bondInit,_stockInit)))
                self.initDate = max(_bondInit,_stockInit)
                self.date     = self.initDate
        except:
            print ('Cannot find the price data. Set the path to the storage first.')
            return False
        #testDf.loc[testDf['날짜']==datetime.date(2021,3,15)]
        #testDf.loc[testDf['날짜']==datetime.date(2021,3,15)].iloc[0]['종가']
        _initStockPrice = float(self.stockData.loc[self.stockData['날짜']==self.initDate].iloc[0]['종가'])
        _initBondPrice  = float(self.bondData.loc[self.bondData['날짜']==self.initDate].iloc[0]['종가'])
        if self.allowFrac:
            self.nStock = self.initVal/_initStockPrice
        else:
            self.nStock = float(np.floor(self.initVal/_initStockPrice))
        _nBond  = 0
        self.nBond = 0

        self.stock= self.nStock*_initStockPrice
        self.bond = 0
        self.cash = self.portfolioValue - self.nStock*_initStockPrice
        
        self.stockReturns = np.array([])
        self.bondReturns  = np.array([])
        self.datesFromLastRebal = datetime.timedelta(days=0)
        
        return True
            
    def verbInitialCond(self):
        print ('Storage path : ',self.storageDir)
        print ('bond data    : ',self.storageDir+'/1_bondETF/{code}.csv'.format(code=self.bondCode))
        print ('stock data   : ',self.storageDir+'/0_stockETF/{code}.csv'.format(code=self.stockCode))

    def setStoragePath(self,storageDir:str):
        print ('Set storage path : ',storageDir)
        self.stroageDir = storageDir
    
    def loadHistory(self):
        print ('Trying to load bond data  : '+self.storageDir+'/1_bondETF/{code}.csv'.format(code=self.bondCode))
        try:
            self.bondData = pd.read_csv(self.storageDir+'/1_bondETF/{code}.csv'.format(code=self.bondCode) ,encoding='utf-8',dtype='str',index_col=0)
        except:
            print ('Cannot load bond data.')
            return False
        print ('Trying to load stock data : '+self.storageDir+'/0_stockETF/{code}.csv'.format(code=self.stockCode))
        try:
            self.stockData= pd.read_csv(self.storageDir+'/0_stockETF/{code}.csv'.format(code=self.stockCode),encoding='utf-8',dtype='str',index_col=0)
        except:
            print ('Cannot load stock data.')
            return False
        for i in range(len(self.bondData)):
            self.bondData.iloc[i]['날짜']=strToDate(self.bondData.iloc[i]['날짜'])
        for i in range(len(self.stockData)):
            self.stockData.iloc[i]['날짜']=strToDate(self.stockData.iloc[i]['날짜'])
        self.stockData[['종가','시가','거래량']] = self.stockData[['종가','시가','거래량']].apply(pd.to_numeric)
        self.bondData[['종가','시가','거래량']]  = self.bondData[['종가','시가','거래량']].apply(pd.to_numeric)
        return True

    def elapse(self,interval:datetime.timedelta=datetime.timedelta(days=1)):
        _elapsed   = datetime.timedelta(days=0)
        _stockDates= self.stockData['날짜'].values
        _bondDates = self.bondData['날짜'].values
        while _elapsed < interval:
            self.date = self.date + datetime.timedelta(days=1)
            if self.date > self.bondData.iloc[0]['날짜'] or self.date > self.stockData.iloc[0]['날짜']:
                print ('Exceeded data range.')
                return True
            
            _indxStock = np.where(_stockDates == self.date)[0]
            _indxBond  = np.where(_bondDates == self.date)[0]
            while len(_indxStock)*len(_indxBond) == 0:
                self.date = self.date + datetime.timedelta(days=1)
                if self.date > self.bondData.iloc[0]['날짜'] or self.date > self.stockData.iloc[0]['날짜']:
                    print ('Exceeded data range.')
                    return True
                _indxStock = np.where(_stockDates == self.date)[0]
                _indxBond  = np.where(_bondDates == self.date)[0]
#            print ('STOCK',self.stockData.iloc[_indxStock[0]]['종가'])
            self.stockReturns = np.append(self.stockReturns\
                                            ,self.stockData.iloc[_indxStock[0]]['종가']/self.stockData.iloc[_indxStock[0]-1]['종가']-1)
#            print ('BOND',self.bondData.iloc[_indxBond[0]]['종가'])
            self.bondReturns = np.append(self.bondReturns\
                                            ,self.bondData.iloc[_indxBond[0]]['종가']/self.bondData.iloc[_indxBond[0]-1]['종가']-1)
            
            self.stock = self.nStock * self.stockData.iloc[_indxStock[0]]['종가']
            self.bond  = self.nBond * self.bondData.iloc[_indxBond[0]]['종가']
            self.portfolioValue = self.stock + self.bond + self.cash
            
            _elapsed = _elapsed + datetime.timedelta(days=1)
            self.datesFromLastRebal = self.datesFromLastRebal + datetime.timedelta(days=1)
            if self.datesFromLastRebal == self.rebalPeriod:
                self.doRebalance()
        return True
            
        
    def doRebalance(self):
#        print ('Rebalancing the portfolio.')
        _stockPriceToday = self.stockData.iloc[np.where(self.stockData['날짜'].values == self.date)[0][0]]['종가']
        _bondPriceToday  = self.bondData.iloc[np.where(self.bondData['날짜'].values == self.date)[0][0]]['종가']
        self.datesFromLastRebal = datetime.timedelta(days=0)
#        print ('Stock returns : ',len( self.stockReturns), self.stockReturns)
#        print ('Bond returns  : ',len(self.bondReturns), self.bondReturns)
#        print ('Bofore rebalancing : {pv}'.format(pv = self.portfolioValue))
#        print ('#Stock = {ns}({ps}), #bond = {nb}({pb}), cash = {pc}'.format(ns=self.nStock,nb=self.nBond,ps=self.stock,pb=self.bond,pc=self.cash))
        if self.nStock == 0 and np.prod(1+self.stockReturns)>np.prod(1+self.bondReturns):
            if self.allowFrac:
                self.nStock = self.portfolioValue/_stockPriceToday
            else:
                self.nStock = np.floor(self.portfolioValue/_stockPriceToday)
                self.nBond  = 0
        if self.nBond == 0 and np.prod(1+self.stockReturns)<np.prod(1+self.bondReturns):
            if self.allowFrac:
                self.nBond = self.portfolioValue/_bondPriceToday
            else:
                self.nBond = np.floor(self.portfolioValue/_bondPriceToday)
            self.nStock = 0
        self.stock = _stockPriceToday*self.nStock
        self.bond  = _bondPriceToday*self.nBond
        self.portfolioValue = self.stock + self.bond + self.cash
#        print ('After rebalancing : {pv}'.format(pv = self.portfolioValue))
#        print ('#Stock = {ns}({ps}), #bond = {nb}({pb}), cash = {pc}'.format(ns=self.nStock,nb=self.nBond,ps=self.stock,pb=self.bond,pc=self.cash))

        self.cash = self.portfolioValue - self.bond - self.stock
            
        self.stockReturns = np.array([])
        self.bondReturns  = np.array([])
            
            
            
            
        
            