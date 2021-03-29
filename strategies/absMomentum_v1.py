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
        self.history       = pd.DataFrame(\
                                columns=['date','portfolioValue','nStock','stock','nBond','bond','cash','rebalancing']\
                                )
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
        self.history       = pd.DataFrame(\
                                columns=['date','portfolioValue'\
                                         ,'stock','bond'\
                                         ,'nStock','nBond'\
                                         ,'stockPrice','bondPrice'\
                                         ,'cash','rebalancing']\
                                )
        try:
            self.loadHistory()
            _bondInit = self.bondData.iloc[-1]['날짜']
            _stockInit= self.stockData.iloc[-1]['날짜']
            if self.initDate < _bondInit or self.initDate < _stockInit:
                print ('Initial point is even prior to the head of the data. Replace it with ',str(max(_bondInit,_stockInit)))
                self.initDate = max(_bondInit,_stockInit)
                self.date     = self.initDate
        except ValueError:
            print ('Cannot find the price data. Set the path to the storage first.')
            return False
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
        
        self.stockReturns = np.array([1.])
        self.bondReturns  = np.array([1.])
        self.datesFromLastRebal = datetime.timedelta(days=0)
        self.history.loc[0] = [self.initDate, self.initVal, self.stock, self.bond\
                              ,self.nStock, self.nBond, _initStockPrice, _initBondPrice\
                              ,self.cash, False]
        return True
    
    def verbInitialCond(self):
        print ('Storage path : ',self.storageDir)
        print ('bond data    : ',self.storageDir+'/{code}.csv'.format(code=self.bondCode))
        print ('stock data   : ',self.storageDir+'/{code}.csv'.format(code=self.stockCode))
        print ('Initial value: ',self.initVal)
        print ('Initial date : ',self.initDate)
        print ('Rebal. period: ',self.rebalPeriod.days,' days')
        print ('allos fract. : ',self.allowFrac)
        
    def verbStatus(self):
        _pVals = self.history['portfolioValue'].values
        _drops = np.array([[np.min(_pVals[i:])/_pVals[i],i+np.argmin(_pVals[i:])] for i in range(len(_pVals))])
        [_maxDrop, _maxDropIndx] = _drops[np.argmin(_drops,axis=0)[0]]
        _stockPriceToday = self.stockData.iloc[np.where(self.stockData['날짜'].values == self.date)[0][0]]['종가']
        _bondPriceToday  = self.bondData.iloc[np.where(self.bondData['날짜'].values == self.date)[0][0]]['종가']
        print ('Storage path : ',self.storageDir)
        print ('bond data    : ',self.storageDir+'/{code}.csv'.format(code=self.bondCode))
        print ('stock data   : ',self.storageDir+'/{code}.csv'.format(code=self.stockCode))
        print ('Current date : ',str(self.date))
        print ('Current value: ',self.portfolioValue,'(initial value : {i}({r}\%))'.format(i=self.initVal,r=100.0*self.portfolioValue/self.initVal))
        print ('# Stock/Bond : {ns}/{nb}'.format(ns=self.nStock,nb=self.nBond))
        print ('total stock  : {ps}({s} eash at {d})'.format(ps=self.stock,s=_stockPriceToday,d=self.date))
        print ('total bond   : {pb}({b} eash at {d})'.format(pb=self.bond ,b=_bondPriceToday ,d=self.date))
        print ('Max drop     : {md}(from {a} to {b})'\
               .format(md=100.0*_maxDrop,a=self.history.iloc[np.argmin(_drops,axis=0)[0]]['date'],b=self.history.iloc[int(_maxDropIndx)]['date']))
        print ('Last rebalancing : {d} ago'.format(d=self.datesFromLastRebal.days))

    def setStoragePath(self,storageDir:str):
        print ('Set storage path : ',storageDir)
        self.stroageDir = storageDir
        
    def loadHistory(self):
#        print ('Trying to load bond data  : '+self.storageDir+'/0_ETF/{code}.csv'.format(code=self.bondCode))
        try:
            self.bondData = pd.read_csv(self.storageDir+'/0_ETF/{code}.csv'.format(code=self.bondCode) ,encoding='utf-8',dtype='str',index_col=0)
        except:
            raise ValueError('[absMomentum:loadHistory] Cannot load bond data.')
#        print ('Trying to load stock data : '+self.storageDir+'/0_ETF/{code}.csv'.format(code=self.stockCode))
        try:
            self.stockData= pd.read_csv(self.storageDir+'/0_ETF/{code}.csv'.format(code=self.stockCode),encoding='utf-8',dtype='str',index_col=0)
        except:
            raise ValueError('[absMomentum:loadHistory] Cannot load stock data.')
        for i in range(len(self.bondData)):
            self.bondData.iloc[i]['날짜']=strToDate(self.bondData.iloc[i]['날짜'])
        for i in range(len(self.stockData)):
            self.stockData.iloc[i]['날짜']=strToDate(self.stockData.iloc[i]['날짜'])
        self.stockData[['종가','시가','거래량']] = self.stockData[['종가','시가','거래량']].apply(pd.to_numeric)
        self.bondData[['종가','시가','거래량']]  = self.bondData[['종가','시가','거래량']].apply(pd.to_numeric)

    def elapse(self,interval:datetime.timedelta=datetime.timedelta(days=1)):
        _elapsed   = datetime.timedelta(days=0)
        _stockDates= self.stockData['날짜'].values
        _bondDates = self.bondData['날짜'].values
        while _elapsed < interval:
            if self.date + datetime.timedelta(days=1) > self.bondData.iloc[0]['날짜'] \
                or self.date + datetime.timedelta(days=1) > self.stockData.iloc[0]['날짜']:
                print ('[absMomentum:elapse] Stop passing time. It reached to the end of the data.')
                return True
            else:
                self.date = self.date + datetime.timedelta(days=1)
            
            _indxStock = np.where(_stockDates == self.date)[0]
            _indxBond  = np.where(_bondDates == self.date)[0]
            while len(_indxStock)*len(_indxBond) == 0:
                if self.date + datetime.timedelta(days=1) > self.bondData.iloc[0]['날짜'] \
                    or self.date + datetime.timedelta(days=1) > self.stockData.iloc[0]['날짜']:
                    print ('[absMomentum:elapse] Stop passing time. It reached to the end of the data.')
                    return True
                else:
                    self.date = self.date + datetime.timedelta(days=1)
                    _indxStock = np.where(_stockDates == self.date)[0]
                    _indxBond  = np.where(_bondDates == self.date)[0]
            self.stockReturns = np.append(self.stockReturns\
                                            ,self.stockData.iloc[_indxStock[0]]['종가']/self.stockData.iloc[_indxStock[0]+1]['종가'])
            self.bondReturns = np.append(self.bondReturns\
                                            ,self.bondData.iloc[_indxBond[0]]['종가']/self.bondData.iloc[_indxBond[0]+1]['종가'])
            
            self.stock = self.nStock * self.stockData.iloc[_indxStock[0]]['종가']
            self.bond  = self.nBond * self.bondData.iloc[_indxBond[0]]['종가']
            self.portfolioValue = self.stock + self.bond + self.cash
            
            _elapsed = _elapsed + datetime.timedelta(days=1)
            self.datesFromLastRebal = self.datesFromLastRebal + datetime.timedelta(days=1)
            
            if self.datesFromLastRebal == self.rebalPeriod:
                self.doRebalance()
                self.history.loc[len(self.history)]=[self.date\
                                                ,self.portfolioValue\
                                                ,self.stock , self.bond\
                                                ,self.nStock, self.nBond\
                                                ,self.stockData.iloc[_indxStock[0]]['종가'], self.bondData.iloc[_indxBond[0]]['종가']\
                                                ,self.cash\
                                                ,True]
            else:
                 self.history.loc[len(self.history)]=[self.date\
                                                ,self.portfolioValue\
                                                ,self.stock , self.bond\
                                                ,self.nStock, self.nBond\
                                                ,self.stockData.iloc[_indxStock[0]]['종가'], self.bondData.iloc[_indxBond[0]]['종가']\
                                                ,self.cash\
                                                ,False]
                
        return True
            
        
    def doRebalance(self):
        _stockPriceToday = self.stockData.iloc[np.where(self.stockData['날짜'].values == self.date)[0][0]]['종가']
        _bondPriceToday  = self.bondData.iloc[np.where(self.bondData['날짜'].values == self.date)[0][0]]['종가']
        self.datesFromLastRebal = datetime.timedelta(days=0)
        _rebalScopeLen = int(np.ceil(self.rebalPeriod/datetime.timedelta(days=1)))
        if self.nStock == 0 \
            and np.prod(self.stockReturns[len(self.stockReturns)-_rebalScopeLen:len(self.stockReturns)])\
                    > np.prod(self.bondReturns[len(self.bondReturns)-_rebalScopeLen:len(self.bondReturns)]):
            if self.allowFrac:
                self.nStock = self.portfolioValue/_stockPriceToday
            else:
                self.nStock = np.floor(self.portfolioValue/_stockPriceToday)
                self.nBond  = 0
        if self.nBond == 0 \
            and np.prod(self.stockReturns[len(self.stockReturns)-_rebalScopeLen:len(self.stockReturns)])\
                    < np.prod(self.bondReturns[len(self.bondReturns)-_rebalScopeLen:len(self.bondReturns)]):
            if self.allowFrac:
                self.nBond = self.portfolioValue/_bondPriceToday
            else:
                self.nBond = np.floor(self.portfolioValue/_bondPriceToday)
            self.nStock = 0
        self.stock = _stockPriceToday*self.nStock
        self.bond  = _bondPriceToday*self.nBond
        self.cash = self.portfolioValue - self.bond - self.stock
        
    def getHistory(self, start=None, end:datetime.date=datetime.date.today()):
        if start == None  or start < self.history['date'].values[0]:
            start = self.history['date'].values[0]
        if start > end:
            print ('[absMomentum:getHistory]The argument indicating the last date of the history is prior than start date. Switching them.')
            buffer = start
            start = end
            end = buffer
            del buffer
        print ('start : ',start)
        print (' end  : ',end)
        self.initialisePortfolio(self.initDate, self.initVal, self.bondCode, self.stockCode, self.rebalPeriod, self.allowFrac, self.storageDir)
        self.elapse(end - self.initDate)
        _historyDates = self.history['date'].values
        _indxStart = np.where(_historyDates == start)[0]
        while len(_indxStart) == 0:
            if start - datetime.timedelta(days=1) < _historyDates[0]:
                print ('[absMomentum:getHistory] There is no day included in the interval.')
                return None
            else:
                start = start - datetime.timedelta(days=1)
                _indxStart = np.where(_historyDates == start)[0]
        _indxEnd = np.where(_historyDates == end)[0]
        while len(_indxEnd) == 0:
            if end - datetime.timedelta(days=1) < start:
                print ('[absMomentum:getHistory] There is no day included in the interval.')
                return None
            else:
                end = end - datetime.timedelta(days=1)
                _indxEnd = np.where(_historyDates == end)[0]
        _returnDf = self.history.iloc[_indxStart[0]:_indxEnd[0]+1]
        _returnDf.index = range(len(_returnDf))
        return _returnDf