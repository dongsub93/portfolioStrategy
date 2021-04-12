import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime

def strToDate(dateStr:str):
    """
        It returns the the date in 'datetime.date' class from the argument which is the date string in
        'yyyy.mm.dd'
    """
    _splitters = ['.','/','-']
    for _delimiter in _splitters:
        _ymdList = dateStr.rsplit(_delimiter)
        try:
            int(_ymdList[0])
            break
        except:
            continue
    if len(_ymdList) == 1:
        return datetime.date(int(_ymdList[0]),1,1)
    elif len(_ymdList) == 2:
        return datetime.date(int(_ymdList[0]),int(_ymdList[1]),1)
    elif len(_ymdList) == 3:
        return datetime.date(int(_ymdList[0]),int(_ymdList[1]),int(_ymdList[2]))
    else:
        raise ValueError('[strToDate] Input string({str}) has more than year/month/day.'.format(str=dateStr))

def drawHistory(data:pd.DataFrame):
    _cols  = data.columns
    _nAsset= int((len(_cols)-6)/3)
    _dates = data.iloc[:,0].values
    _pVals = data.iloc[:,1].values
    _bVals = data.iloc[:,-3].values
    _prices= data.iloc[:,range(2*_nAsset+2,3*_nAsset+2)].values
    #_assets= data.iloc[:,range(2,_nAsset+2)].values
    _fig, _ax = plt.subplots(1,1,sharex=True,figsize=(10,4))
    #_ax.plot_date(x = _dates,y=_pVals, linestyle='-',marker=None,label=_cols[1],color='black')
    _ax.plot_date(x = _dates,y=_pVals, fmt='-k',marker=None,label=_cols[1])
    _ax.plot_date(x = _dates,y=_bVals, fmt='--k',marker=None,label=_cols[-3])
    for i in range(_nAsset):
        _ax.plot_date(x = _dates, y = (_pVals[0]/_prices[0,i])*_prices[:,i],fmt='-',label=_cols[2*_nAsset+2+i])
        #_ax.plot_date(x = _dates, y = (_pVals[0]/_prices[0,i])*_prices[:,i],linestyle='-',marker=None,label=_cols[2*_nAsset+2+i])
    _ax.legend(loc='upper left')
    _fig.autofmt_xdate(rotation=45)
    return _fig, _ax

def getMDD(data:pd.DataFrame, asset:str='portfolioValue', start:datetime.date=None, end:datetime.date=None):
    if asset != 'portfolioValue' and asset != 'benchmarkValue':
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
    _dates = data.iloc[_indxStart[0]:_indxEnd[0]+1]['date'].values
    _prices= data.iloc[_indxStart[0]:_indxEnd[0]+1][asset].values
    _drops = np.array([[np.min(_prices[i:])/_prices[i],i+np.argmin(_prices[i:])]\
                        for i in range(len(_prices))
                        ])
    _mddStartIndx = np.argmin(_drops,axis=0)[0]
    [_mdd, _mddEndIndx ] = _drops[_mddStartIndx]
    return 100.0 - 100.0*_mdd, _dates[_mddStartIndx], _dates[int(_mddEndIndx)]

def maximiseSharpe(rf:float, r1:float, r2:float, var1:float, var2:float, cov:float):
    _weight = ( (rf-r2)*cov + (r1-rf)*var2 )/((r2-rf)*var1 + (r1-rf)*var2 -(r1+r2)*cov + 2*rf*cov)
    _SRmax  = (_weight*r1 + (1-_weight)*r2 - rf)/np.sqrt(var1*_weight**2 + var2*(1.-_weight)**2 + 2*_weight*(1.-_weight)*cov)
    if _SRmax >= max( (r1-rf)/np.sqrt(var1), (r2-rf)/np.sqrt(var2) )\
         and _weight <= 1.\
         and _weight >= 0.:
        return _SRmax, _weight
    else:
        if (r1-rf)/np.sqrt(var1) >= (r2-rf)/np.sqrt(var2):
            return (r1-rf)/np.sqrt(var1),  1.
        else:
            return (r2-rf)/np.sqrt(var2),  0.