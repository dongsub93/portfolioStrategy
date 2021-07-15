import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import datetime
from aux_functions import *

def analysis_functions_version():
    return '0.1.0'

def analyse_history(data:pd.DataFrame=None, time_scales:list=[1]):
    cols  = data.columns
    n_asset= int((len(cols)-6)/3)
    dates  = np.array([str_to_date(date) if type(date)=='str' else date for date in data.iloc[:,0].values])
    p_vals = data.iloc[:,1].values.astype(float)
    b_vals = data.iloc[:,-3].values.astype(float)    
    rf     = data.iloc[:,-2].values.astype(float)

    prices = data.iloc[:,range(2*n_asset+2,3*n_asset+2)].values
    fig, axes = plt.subplots(2+len(time_scales),1,sharex=True,figsize=(10,8+4*len(time_scales)))
    fig.tight_layout()
    axes[0].plot_date(x = dates ,y=p_vals, fmt='-k',marker=None,label=cols[1])
    axes[0].plot_date(x = dates ,y=b_vals, fmt='--r',marker=None,label=cols[-3])
    axes[0].set_yscale('log')
    axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    axes[1].plot_date(x = dates ,y=p_vals, fmt='-k',marker=None,label=cols[1])
    axes[1].plot_date(x = dates ,y=b_vals, fmt='--r',marker=None,label=cols[-3])
    for i in range(n_asset):
        axes[1].plot_date(x = dates , y = (p_vals[0]/prices [0,i])*prices [:,i],fmt='-',alpha=0.3)
        #axes[0].plot_date(x = dates , y = (p_vals[0]/prices [0,i])*prices [:,i],fmt='-',label=cols[2*n_asset+2+i],alpha=0.3)
    axes[1].set_yscale('log')
    axes[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))

    p_returns = [np.array([1.])]*len(time_scales)
    b_returns = [np.array([1.])]*len(time_scales)
    rf_returns= [np.array([ np.power(rf[0],scale) ]) for scale in time_scales]
    starts  = np.array(time_scales)
    counters= np.ones(len(time_scales))
    
    for day in range(1,len(p_vals)):   
        for it, scale in enumerate(time_scales):
            if not counters[it] < scale:
                starts[it]  = day
                counters[it]= 0
            
            if day < scale:
                p_returns[it] = np.append(p_returns[it],1.0)
                b_returns[it] = np.append(b_returns[it],1.0)
            else:
                p_returns[it] = np.append(p_returns[it]\
                                          ,p_vals[starts[it]]/p_vals[starts[it]-int(scale)]\
                                         )
                b_returns[it] = np.append(b_returns[it]\
                                          ,b_vals[starts[it]]/b_vals[starts[it]-int(scale)]\
                                         )
                if counters[it] == 0:
                    rf_returns[it]= np.append(rf_returns[it],np.product(rf[starts[it]-int(scale):starts[it]+1]))
            counters[it] = counters[it]+1
            
    p_returns_unique = [np.array([p_returns[kscale][it] for it in range(0,len(p_returns[kscale]),scale)])\
                          for kscale, scale in enumerate(time_scales) ]
    b_returns_unique = [np.array([b_returns[kscale][it] for it in range(0,len(b_returns[kscale]),scale)])\
                          for kscale, scale in enumerate(time_scales) ]
    p_sharpe_ratios = [(np.mean(p_returns_unique[kscale])-np.mean(rf_returns[kscale]))/np.std(np.log(p_returns_unique[kscale]))\
                           for kscale in range(len(time_scales))]
    b_sharpe_ratios = [(np.mean(b_returns_unique[kscale])-np.mean(rf_returns[kscale]))/np.std(np.log(b_returns_unique[kscale]))\
                           for kscale in range(len(time_scales))]
    
    for it, scale in enumerate(time_scales):
        axes[it+2].plot_date(x = []    ,y=[]           , marker=None,label='{d}-day returns'.format(d=scale))
        axes[it+2].plot_date(x = dates ,y=p_returns[it], fmt='-k',marker=None,label='portfolio')
        axes[it+2].plot_date(x = []    ,y=[]           , marker=None,label='Sharpe Ratio : {sr:1.4f}'.format(sr=p_sharpe_ratios[it]))
        axes[it+2].plot_date(x = dates ,y=b_returns[it], fmt='--r',marker=None,label='benchmark')
        axes[it+2].plot_date(x = []    ,y=[]           , marker=None,label='Sharpe Ratio : {sr:1.4f}'.format(sr=b_sharpe_ratios[it]))
        axes[it+2].plot_date(x = dates ,y=[1.]*len(dates), fmt='-y',marker=None,alpha=0.4)
        axes[it+2].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    fig.autofmt_xdate(rotation=45)
    p_mdd, p_mdd_from, p_mdd_to = get_MDD(data, asset='portfolio_value',start=dates[0],end=dates[-1])
    b_mdd, b_mdd_from, b_mdd_to = get_MDD(data, asset='benchmark_value',start=dates[0],end=dates[-1])
    p_return_growth = 100.0*(p_vals[-1]/p_vals[0]-1.0)
    b_return_growth = 100.0*(b_vals[-1]/b_vals[0]-1.0)
    p_return_anual  = 100.0*(np.power(p_vals[-1]/p_vals[0], 252.0/len(dates))-1.0)
    b_return_anual  = 100.0*(np.power(b_vals[-1]/b_vals[0], 252.0/len(dates))-1.0)
                    
    return (fig, axes, [p_sharpe_ratios, b_sharpe_ratios], [p_mdd, b_mdd], [p_return_growth, b_return_growth], [p_return_anual, b_return_anual])