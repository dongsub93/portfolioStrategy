import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime

def drawHistory(data:pd.DataFrame):
    _cols  = data.columns
    _nAsset= int((len(_cols)-4)/3)
    _dates = data.iloc[:,0].values
    _pVals = data.iloc[:,1].values
    _prices= data.iloc[:,range(2*_nAsset+2,3*_nAsset+2)].values
    #_assets= data.iloc[:,range(2,_nAsset+2)].values
    _fig, _ax = plt.subplots(1,1,sharex=True,figsize=(10,4))
    _ax.plot_date(x = _dates,y=_pVals, linestyle='-',marker=None,label=_cols[1],color='black')
    for i in range(_nAsset):
        _ax.plot_date(x = _dates, y = (_pVals[0]/_prices[0,i])*_prices[:,i],linestyle='-',marker=None,label=_cols[2*_nAsset+2+i])
    _ax.legend(loc='upper left')
    _fig.autofmt_xdate(rotation=45)
    return _fig, _ax


def getMDD(data:pd.DataFrame, asset:str='portfolioValue', start:datetime.date=None, end:datetime.date=None):
    if asset != 'portfolioValue':
        asset = 'p'+asset
    if start == None:
        start = data['date'].values[0]
    if end == None:
        end = data['date'].values[-1]
    if start > end:
        print ('[getMDD] input:end is prior to input:start. They will replace each others.')
        _buffer = start
        start = end
        end = _buffer

    _dates     = data['date'].values
    _indxStart = np.where(_dates == start)[0]
    while len(_indxStart) == 0 :
        if start - datetime.timedelta(days=1) < _dates[0]:
            print ('[getMDD] There is no single day included in the time interval to evaluate MDD.')
            return None
        else:
            start = start - datetime.timedelta(days=1)
            _indxStart = np.where(_dates == start)[0]
    
    _indxEnd = np.where(_dates == end)[0]
    while len(_indxEnd) == 0 :
        if end - datetime.timedelta(days=1) < start:
            print ('[getMDD] There is no single day included in the time interval to evaluate MDD.')
            return None
        else:
            start = start - datetime.timedelta(days=1)
            _indxEnd = np.where(_dates == end)[0]
    _dates = daat.iloc[_indxStart[0]:_indxEnd[0]+1]['date'].values
    _prices= daat.iloc[_indxStart[0]:_indxEnd[0]+1][asset].values
    _drops = np.array([[np.min(_prices[i:])/_prices[i],i+np.argmin(_prices[i:])]\
                        for i in range(len(_prices))
                        ])
    _mddStartIndx = np.argmen(_drops,axis=0)[0]
    [_mdd, _mddEndIndx ] = _drops[_mddStartIndx]
    return 100.0 - 100.0*_mdd, _dates[_mddStartIndx], _dates[int(_mddEndIndx)]


