import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import datetime


def aux_functions_version():
    return '6.1.0'

def str_to_date(date:str):
    """
        It returns the the date in 'datetime.date' class from the argument which is the date string in
        'yyyy.mm.dd'
    """
    splitters = ['.','/','-']
    for delimiter in splitters:
        ymd = date.rsplit(delimiter)
        try:
            int(ymd[0])
            break
        except:
            continue
    if len(ymd) == 1:
        return datetime.date(int(ymd[0]),1,1)
    elif len(ymd) == 2:
        return datetime.date(int(ymd[0]),int(ymd[1]),1)
    elif len(ymd) == 3:
        return datetime.date(int(ymd[0]),int(ymd[1]),int(ymd[2]))
    else:
        raise ValueError('[str_to_date] Input string({str}) has more than year/month/day.'.format(str=date))

def draw_history(data:pd.DataFrame, time_scales:list=[1]):
    cols  = data.columns
    n_asset= int((len(cols)-6)/3)
    dates  = data.iloc[:,0].values
    p_vals = data.iloc[:,1].values
    b_vals = data.iloc[:,-3].values
    prices = data.iloc[:,range(2*n_asset+2,3*n_asset+2)].values
    fig, axes = plt.subplots(1+len(time_scales),1,sharex=True,figsize=(10,4+4*len(time_scales)))
    fig.tight_layout()
    axes[0].plot_date(x = dates ,y=p_vals, fmt='-k',marker=None,label=cols[1])
    axes[0].plot_date(x = dates ,y=b_vals, fmt='--r',marker=None,label=cols[-3])
    for i in range(n_asset):
        axes[0].plot_date(x = dates , y = (p_vals[0]/prices [0,i])*prices [:,i],fmt='-',label=cols[2*n_asset+2+i],alpha=0.3)
    axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    p_returns = [np.array([1.])]*len(time_scales)
    b_returns = [np.array([1.])]*len(time_scales)
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
                if starts[it] < len(p_vals):
                    p_returns[it] = np.append(p_returns[it]\
                                            ,p_vals[starts[it]]/p_vals[starts[it]-int(scale)]\
                                             )
                    b_returns[it] = np.append(b_returns[it]\
                                              ,b_vals[starts[it]]/b_vals[starts[it]-int(scale)]\
                                             )
            counters[it] = counters[it]+1
    
    for it, scale in enumerate(time_scales):
        axes[it+1].plot_date(x = dates ,y=p_returns[it], fmt='-k',marker=None,label='portfolio return({d}-days)'.format(d=scale))
        axes[it+1].plot_date(x = dates ,y=b_returns[it], fmt='--r',marker=None,label='benchmark return({d}-days)'.format(d=scale))
        axes[it+1].plot_date(x = dates ,y=[1.]*len(dates), fmt='-y',marker=None,alpha=0.4)
        axes[it+1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    fig.autofmt_xdate(rotation=45)
    return fig, axes

def get_MDD(data:pd.DataFrame, asset:str='portfolio_value', start:datetime.date=None, end:datetime.date=None):
    if asset != 'portfolio_value' and asset != 'benchmark_value':
        asset = 'p'+asset
    if start == None:
        start = data['date'].values[0]
    if end == None:
        end = data['date'].values[-1]
    if start > end:
        print ('[get_MDD] input:end is prior to input:start. They will replace each others.')
        _buffer = start
        start = end
        end = _buffer

    dates = data['date'].values
    it_begin = np.where(dates == start)[0]

    while len(it_begin) == 0 :
        if start - datetime.timedelta(days=1) < dates[0]:
            print ('[get_MDD] There is no single day included in the time interval to evaluate MDD.')
            return None
        else:
            start = start - datetime.timedelta(days=1)
            it_begin = np.where(dates  == start)[0]
    
    it_end = np.where(dates  == end)[0]
    while len(it_end) == 0 :
        if end - datetime.timedelta(days=1) < start:
            print ('[get_MDD] There is no single day included in the time interval to evaluate MDD.')
            return None
        else:
            start = start - datetime.timedelta(days=1)
            it_end = np.where(dates == end)[0]

    dates = data.iloc[it_begin[0]:it_end[0]+1]['date'].values
    prices= data.iloc[it_begin[0]:it_end[0]+1][asset].values
    drops = np.array([[np.min(prices [i:])/prices [i],i+np.argmin(prices [i:])]\
                        for i in range(len(prices ))
                        ])
    it_from = np.argmin(drops,axis=0)[0]
    [mdd, it_to ] = drops[it_from]
    return 100.0 - 100.0*mdd, dates[it_from], dates[int(it_to)]

def get_maxSR(rf:float, r1:float, r2:float, var1:float, var2:float, cov:float):
    atanSR1 = np.arctan2(r1-rf,np.sqrt(var1))
    atanSR2 = np.arctan2(r2-rf,np.sqrt(var2))
    result  = np.array([[atanSR1, 1., 0.]\
                        ,[atanSR2, 0., 1.]])
    try:
        weight = ( (rf-r2)*cov + (r1-rf)*var2 )/((r2-rf)*var1 + (r1-rf)*var2 -(r1+r2)*cov + 2*rf*cov)
        if weight > 0. and weight < 1.:
            result = np.append(result\
                             ,[[np.arctan2(weight*r1 + (1-weight)*r2 - rf\
                                           ,np.sqrt(var1*weight**2 + var2*(1.-weight)**2 + 2*weight*(1.-weight)*cov))\
                                ,weight\
                                ,1-weight]\
                              ]\
															,axis=0
                            )
        else:
            result = np.append(result, [[-0.5*np.pi , 0. , 0.]], axis=0)
    except:
        result = np.append(result, [[-0.5*np.pi , 0. , 0.]], axis=0)
    return result[np.argmax(result,axis=0)[0]]

def verbose(allowed_lv, required_lv,*args):
    if allowed_lv <= required_lv:
        print (*args)
    else:
        None