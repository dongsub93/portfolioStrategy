import sys,os
import datetime
from datetime import date
from datetime import timedelta
import crawler_v0
from crawler_v0 import *
import pandas as pd
import numpy as np
import aux_functions
from aux_functions import getMDD

class momentumStrategy:
    def __init__(self, initDate:datetime.date = datetime.date.today()\
                            ,initVal:float = 0\
                            ,assetCodes=[]\
                            ,assetWeights=[]\
                            ,rebalPeriod:datetime.timedelta = datetime.timedelta(days=1)\
                            ,rebalScope:datetime.timedelta = datetime.timedelta(days=1)\
                            ,allowFrac:bool=True\
                            ,vetoNegative:bool=True\
                            ,storageDir:str=None):
        if len(assetCodes) != len(assetWeights):
            raise ValueError('[momentumStrategy:__init__] lentgh of weights({lw}) is not matched with the number of assets({na}.'\
                             .format(lw=len(assetWeights), na=len(assetCodes)))
        self.initDate      = initDate
        self.initVal       = initVal
        self.assetCodes    = assetCodes
        self.assetWeights  = assetWeights
        if len(assetWeights) != 0 and  abs(sum(self.assetWeights)-1.0) > 1e-5:
            print ('[momentumStrategy:__init__]Sum of weights is not 1. Normalise it to have unit-sum.')
            _sumWeights = sum(self.assetWeights)
            for i in range(len(self.assetWeights)):
                self.assetWeights[i] = self.assetWeights[i]/_sumWeights
            print ('[momentumStrategy:__init__] Renormalised weights : ',self.assetWeights,' (sum = {s})'.format(s=sum(self.assetWeights)))
        self.rebalPeriod   = rebalPeriod
        self.rebalScope    = rebalScope
        self.allowFrac     = allowFrac
        self.vetoNegative  = vetoNegative
            
        self.storageDir    = None
        if storageDir == None and self.storageDir == None:
            self.storageDir = '.'
        elif storageDir == None and self.storageDir != None:
            pass
        elif storageDir != None:
            self.storageDir= storageDir
        
        self.date          = self.initDate
        self.portfolioValue= self.initVal
        
        _dfColumns = np.array(['date','portfolioValue'])
        for code in self.assetCodes:
            _dfColumns = np.append(_dfColumns, 't'+code)
        for code in self.assetCodes:
            _dfColumns = np.append(_dfColumns, 'n'+code)
        for code in self.assetCodes:
            _dfColumns = np.append(_dfColumns, 'p'+code)
        _dfColumns = np.append(_dfColumns,['cash','rebalancing'])
        self.history = pd.DataFrame(columns=_dfColumns)
        
    def initialisePortfolio(self, initDate:datetime.date = datetime.date.today()\
                            ,initVal:float = 0\
                            ,assetCodes=[]\
                            ,assetWeights=[]\
                            ,rebalPeriod:datetime.timedelta = datetime.timedelta(days=1)\
                            ,rebalScope:datetime.timedelta = datetime.timedelta(days=1)\
                            ,allowFrac:bool=True\
                            ,vetoNegative:bool=True\
                            ,storageDir:str=None):
        if len(assetCodes) != len(assetWeights):
            raise ValueError('[momentumStrategy:initialisePortfolio] lentgh of weights({lw}) is not matched with the number of assets({na}.'\
                             .format(lw=len(assetWeights), na=len(assetCodes)))
        self.initDate      = initDate
        self.initVal       = initVal
        self.assetCodes    = assetCodes
        self.assetWeights  = assetWeights
        if abs(sum(self.assetWeights)-1.0) > 1e-5:
            print ('[momentumStrategy:initialisePortfolio]Sum of weights is not 1. Normalise it to have unit-sum.')
            _sumWeights = sum(self.assetWeights)
            for i in range(len(self.assetWeights)):
                self.assetWeights[i] = self.assetWeights[i]/_sumWeights
            print ('[momentumStrategy:initialisePortfolio] Renormalised weights : ',self.assetWeights,' (sum = {s})'.format(s=sum(self.assetWeights)))
        
        self.rebalPeriod   = rebalPeriod
        self.rebalScope    = rebalScope
        self.allowFrac     = allowFrac
        self.vetoNegative  = vetoNegative
        
        self.storageDir    = None
        if storageDir == None and self.storageDir == None:
            self.storageDir = '.'
        elif storageDir == None and self.storageDir != None:
            pass
        elif storageDir != None:
            self.storageDir= storageDir
        
        self.date          = self.initDate
        self.portfolioValue= self.initVal
        
        _dfColumns = np.array(['date','portfolioValue'])
        for code in self.assetCodes:
            _dfColumns = np.append(_dfColumns, 't'+code)
        for code in self.assetCodes:
            _dfColumns = np.append(_dfColumns, 'n'+code)
        for code in self.assetCodes:
            _dfColumns = np.append(_dfColumns, 'p'+code)
        _dfColumns = np.append(_dfColumns,['cash','rebalancing'])
        self.history = pd.DataFrame(columns=_dfColumns)
        
        try:
            self.loadHistory()
            _initDates = np.array([])
            for assetData in self.assetData.values():
                _initDates = np.append(_initDates, assetData.iloc[-1]['날짜'])
            if self.initDate < max(_initDates):
                print ('[momentumStrategy:initialisePortfolio]Initial point is even prior to the head of the data. Replace it with ',str(max(_initDates)))
                self.initDate = max(_initDates)
                self.date     = self.initDate
        except ValueError:
            print ('[momentumStrategy:loadHistory]Cannot find the price data. Set the path to the storage first.')
            return False
        
        _initPrices = dict([(asset, assetData.loc[assetData['날짜']==self.initDate].iloc[0]['종가']) for asset, assetData in self.assetData.items()])
        _initPrices = dict(sorted(_initPrices.items(), key=lambda x:x[1], reverse=False))

        self.nAssets = {}
        self.tAssets = {}
        self.returns = {}
        _it = 0
        for asset,price in _initPrices.items():
            if self.allowFrac:
                self.nAssets[asset] = self.initVal*self.assetWeights[_it]/price
            else:
                self.nAssets[asset] =float(np.floor(self.initVal*self.assetWeights[_it]/price))
            _it += 1
            self.tAssets[asset] = self.nAssets[asset]*price
            self.returns[asset] = np.array([1.])
        self.cash = self.portfolioValue - sum(self.tAssets.values())
        
        #_row = [np.ones(4+len(self.assetCodes))]
        _row = [None]*(4+3*len(self.assetCodes))
        _row[0] = self.initDate
        _row[1] = self.initVal
        _row[-1]= True
        _row[-2]= self.cash
        for i in range(len(self.assetCodes)):
            _row[2+i] = self.tAssets[self.assetCodes[i]]
            _row[2+len(self.assetCodes)+i] = self.nAssets[self.assetCodes[i]]
            _row[2+2*len(self.assetCodes)+i] = _initPrices[self.assetCodes[i]]
            
        self.datesFromLastRebal = datetime.timedelta(days=0)
        self.history.loc[0] = _row
        return True
    
    def setStoragePath(self,storageDir:str):
        print ('Set storage path : ',storageDir)
        self.stroageDir = storageDir
        
    def loadHistory(self):
        self.assetData = {}
        for asset in self.assetCodes:
            try:
                self.assetData[asset] = pd.read_csv(self.storageDir+'/{code}.csv'.format(code=asset)\
                                                    ,encoding='utf-8',dtype='str',index_col=0)
            except:
                raise ValueError('[momentumStrategy:loadHistory] Cannot load price data of asset : {a}'.format(a=asset))
            for i in range(len(self.assetData[asset])):
                self.assetData[asset].iloc[i]['날짜'] = strToDate(self.assetData[asset].iloc[i]['날짜'])
            self.assetData[asset][['종가','시가','거래량']] = self.assetData[asset][['종가','시가','거래량']].apply(pd.to_numeric)
    
    def verbInitialCond(self):
        print ('='*40)
        print ('Initial condition of the portfolio')
        print ('-'*40)
        print ('Storage path : ',self.storageDir)
        print ('asset codes  : ',self.assetCodes)
        print ('asset weights: ',self.assetWeights)
        print ('Initial value: ',self.initVal)
        print ('Initial date : ',self.initDate)
        print ('Rebal. period: ',self.rebalPeriod.days,' days')
        print ('Rebal. scope : ',self.rebalScope.days,' days')
        print ('allos fract. : ',self.allowFrac)
        print ('veto (-)asset: ',self.vetoNegative)
        print ('='*40)

    def verbStatus(self):
        _pVals = self.history['portfolioValue'].values
        _drops = np.array([[np.min(_pVals[i:])/_pVals[i],i+np.argmin(_pVals[i:])] for i in range(len(_pVals))])
        [_mdd, _mddIndx] = _drops[np.argmin(_drops,axis=0)[0]]
        _assetPricesToday = {}
        for asset, assetData in self.assetData.items():
            _assetPricesToday[asset] = assetData.loc[assetData['날짜']==self.date].iloc[0]['종가']
        
        print ('='*40)
        print ('Status of the portfolio')
        print ('-'*40)
        print ('Current date : ',str(self.date))
        print ('Current value: ',self.portfolioValue,'(initial value : {i})'.format(i=self.initVal))
        print ('growth return:  {r:3.2f}% ( annual : {a:3.2f}%)'\
              .format(r=100.0*(1.0-self.portfolioValue/self.initVal)\
                      ,a=100.0*(1.0-pow(self.portfolioValue/self.initVal,252.0/float(len(self.history))))
                     )\
              )
        print ('Max.Drawdown :  {md:3.3f}%(from {a} to {b})'\
               .format(md=100.0*(1.0-_mdd)\
                       ,a=self.history.iloc[np.argmin(_drops,axis=0)[0]]['date']\
                       ,b=self.history.iloc[int(_mddIndx)]['date'])\
              )
        print ('Inventory')
        for asset in self.assetCodes:
            _assetMDD, _from, _to = getMDD(self.history, asset, self.initDate, self.date)
            print (' |= {c}     : total {t} ({p:3.2f}%)'\
                   .format(c=asset,t=self.tAssets[asset], p=100.0*self.tAssets[asset]/self.portfolioValue))
            if asset != self.assetCodes[-1]:
                print (' |   |- volume : ',int(self.nAssets[asset]))
                print (' |   |- prices : ',_assetPricesToday[asset])
                print (' |   |- MDD    :  {mdd:3.3f}%(from {a} to {b})'.format(mdd=_assetMDD,a=_from,b=_to))
                print (' |   |- return :  {r:3.2f}% (annual : {a:3.2f}%)'\
                       .format(r=100.0*(1.0-_assetPricesToday[asset]/self.history['p'+asset].values[0])\
                            ,a=100.0*(1.0\
                                        -pow(_assetPricesToday[asset]/self.history['p'+asset].values[0],252.0/float(len(self.history)))\
                                     )\
                              )
                      )
            else:
                print ('     |- volume : ',int(self.nAssets[asset]))
                print ('     |- prices : ',_assetPricesToday[asset])
                print ('     |- MDD    :  {mdd:3.2f}%(from {a} to {b})'.format(mdd=_assetMDD,a=_from,b=_to))
                print ('     |- return :  {r:3.2f}% (annual : {a:3.2f}%)'\
                       .format(r=100.0*(1.0-_assetPricesToday[asset]/self.history['p'+asset].values[0])\
                            ,a=100.0*(1.0\
                                        -pow(_assetPricesToday[asset]/self.history['p'+asset].values[0],252.0/float(len(self.history)))\
                                     )\
                              )
                      )
            #print (' |-  {c}  : total {t} (# : {n}, prices = {p} per each)'\
            #       .format(c=asset, t=self.tAssets[asset], n=int(self.nAssets[asset]),p=_assetPricesToday[asset] ))
        print ('Last rebalancing : {d} days ago'.format(d=self.datesFromLastRebal.days))


    def elapse(self,interval:datetime.timedelta=datetime.timedelta(days=1)):
        _elapsed   = datetime.timedelta(days=0)
        _assetDates = dict([(key,_df['날짜'].values) for key, _df in self.assetData.items() ])
        while _elapsed < interval:
            if any(self.date + datetime.timedelta(days=1) > _dates[0] for _dates in _assetDates.values() ):
                print ('[momentumStrategy:elapse] Stop passing time. It reached to the end of the data.')
                return True
            else:
                self.date = self.date + datetime.timedelta(days=1)
            _assetIndx = dict([(asset, np.where(_assetDates[asset]==self.date)[0]) for asset in self.assetCodes ])
            while any(len(_indexes) == 0 for _indexes in _assetIndx.values() ):
                if any(self.date + datetime.timedelta(days=1) > _dates[0] for _dates in _assetDates.values() ):
                    print ('[momentumStrategy:elapse] Stop passing time. It reached to the end of the data.')
                    return True
                else:
                    self.date = self.date + datetime.timedelta(days=1)
                    _assetIndx = dict([(asset, np.where(_assetDates[asset]==self.date)[0]) for asset in self.assetCodes ])
            for asset in self.assetCodes:
                self.returns[asset] = np.append(self.returns[asset]\
                                               ,self.assetData[asset].iloc[_assetIndx[asset][0]]['종가']/self.assetData[asset].iloc[_assetIndx[asset][0]+1]['종가']\
                                               )        
            self.tAssets = dict([ (asset, nAsset*self.assetData[asset].iloc[_assetIndx[asset][0]]['종가'])\
                                 for asset, nAsset in self.nAssets.items() ])
            self.portfolioValue = self.cash + sum(self.tAssets.values())
            _elapsed = _elapsed + datetime.timedelta(days=1)
            self.datesFromLastRebal = self.datesFromLastRebal + datetime.timedelta(days=1)
            
            _row = [None]*(4+3*len(self.assetCodes))
            _row[0] = self.date
            _row[1] = self.portfolioValue
            if self.datesFromLastRebal == self.rebalPeriod:
                self.doRebalance()
                _row[-1]= True
            else:
                _row[-1]= False
            _row[-2]= self.cash
            for i in range(len(self.assetCodes)):
                _code = self.assetCodes[i]
                _row[2+i] = self.tAssets[_code]
                _row[2+len(self.assetCodes)+i] = self.nAssets[_code]
                _row[2+2*len(self.assetCodes)+i] = self.assetData[_code].iloc[_assetIndx[_code][0]]['종가']
            self.history.loc[len(self.history)] = _row
        return True

    def doRebalance(self):
        _assetPricesToday = {}
        for asset, assetData in self.assetData.items():
            _assetPricesToday[asset] = assetData.iloc[np.where(assetData['날짜'].values == self.date)[0][0]]['종가']
        self.datesFromLastRebal = datetime.timedelta(days=0)
        _rebalScopeLen = int(np.ceil(self.rebalScope/datetime.timedelta(days=1)))
        
        _avgReturns = dict([ (_asset, np.prod(_returns[max(0,len(_returns)-_rebalScopeLen):len(_returns)]))\
                             for _asset, _returns in self.returns.items() ])
        _avgReturns = dict(sorted(_avgReturns.items(), key=lambda x:x[1], reverse=True))
        
        _assetWeights = {}
        _rank = 0
        for asset, returns in _avgReturns.items():
            if self.vetoNegative and returns < 1.0:
                _assetWeights[asset] = 0
            else:
                _assetWeights[asset] = self.assetWeights[_rank]
            _rank += 1
        if sum(_assetWeights.values()) == 0.0:
            print ('[momentumStrategy:doRebalance] All assets show returns less than 1 in the scope. Rebalancing will be tried next day again.')
            self.datesFromLastRebal = self.rebalPeriod - datetime.timedelta(days=1)
            return True
        else:
            _renorm = sum(_assetWeights.values())
            for weight in _assetWeights.values():
                weight = weight/_renorm
                
        for asset in _avgReturns.keys():
            if self.allowFrac:
                self.nAssets[asset] = self.portfolioValue*_assetWeights[asset]/_assetPricesToday[asset]
            else:
                self.nAssets[asset] = np.floor(self.portfolioValue*_assetWeights[asset]/_assetPricesToday[asset])
            self.tAssets[asset] = self.nAssets[asset]*_assetPricesToday[asset]
        self.cash = self.portfolioValue - sum(self.tAssets.values())
        return True
        
    def getHistory(self, start=None, end:datetime.date=datetime.date.today()):
        if start == None  or start < self.history['date'].values[0]:
            start = self.history['date'].values[0]
        if start > end:
            print ('[momentumStrategy:getHistory]The argument indicating the last date of the history is prior than start date. Switching them.')
            buffer = start
            start = end
            end = buffer
            del buffer
        self.initialisePortfolio(initDate = self.initDate\
                                 ,initVal = self.initVal\
                                 ,assetCodes = self.assetCodes , assetWeights = self.assetWeights\
                                 ,rebalPeriod= self.rebalPeriod, rebalScope   = self.rebalScope\
                                 ,allowFrac  = self.allowFrac  , storageDir   = self.storageDir)
        self.elapse(end - self.initDate)
        _historyDates = self.history['date'].values
        _indxStart = np.where(_historyDates == start)[0]
        while len(_indxStart) == 0:
            if start - datetime.timedelta(days=1) < _historyDates[0]:
                print ('[momentumStrategy:getHistory] There is no day included in the interval.')
                return None
            else:
                start = start - datetime.timedelta(days=1)
                _indxStart = np.where(_historyDates == start)[0]
        _indxEnd = np.where(_historyDates == end)[0]
        while len(_indxEnd) == 0:
            if end - datetime.timedelta(days=1) < start:
                print ('[momentumStrategy:getHistory] There is no day included in the interval.')
                return None
            else:
                end = end - datetime.timedelta(days=1)
                _indxEnd = np.where(_historyDates == end)[0]
        _returnDf = self.history.iloc[_indxStart[0]:_indxEnd[0]+1]
        _returnDf.index = range(len(_returnDf))
        return _returnDf
