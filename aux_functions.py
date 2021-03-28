import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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