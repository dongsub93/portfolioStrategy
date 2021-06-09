import os
import sys
import subprocess
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
from analysis_functions import *
from portfolio import portfolio
import gc

#storage_dir ='./98_analysis_maxSR'
#tag_fmt = 'maxSR_{t}ua{ua}_rp{rp}_lp{lp}_rg{rg}'
#strategy='maxSR'

#storage_dir ='./96_analysis_momentum'
#tag_fmt = 'momentum_{t}ua{ua}_rp{rp}_lp{lp}_rg{rg}'
#strategy='momentum'

storage_dir ='./95_analysis_momentum_linear'
tag_fmt = 'momentum_linear_{t}ua{ua}_rp{rp}_lp{lp}_rg{rg}'
strategy='momentum_linear'

for tag in ['','no-reits_','no-cb_','no-reits_no-cb_']:
#for tag in ['no-reits_no-cb_']:
    for ua in [0,1]:
        result_benchmark_rg1 = np.array([]).reshape((0,22))
        result_benchmark_rg5 = np.array([]).reshape((0,22))
        result_portfolio_rg1 = np.array([]).reshape((0,22))
        result_portfolio_rg5 = np.array([]).reshape((0,22))
        for rp in [1,5,20,40,60,120,225]:
            for lp in [1,5,20,40,60,120,225]:
                #for rg in [1,5]:
                for rg in [1]:
                    if rg >= lp or rp > lp:
                        continue
                    name_tag = tag_fmt.format(t=tag, ua=ua, rp=rp, lp=lp, rg=rg)
                    result_csv = np.array([]).reshape((0,14))
                    for shift in range(rp):
                        result_file_name = 'result_'+name_tag +'_shift{s}.csv'.format(s=shift)
                        if not os.path.isfile('{s}/{dir}/{fname}'.format(s=storage_dir, dir=name_tag, fname=result_file_name)):
                            print ('Cannot find a file : ',result_file_name)
                            continue
                        temp_csv = np.loadtxt('{s}/{dir}/{fname}'.format(s=storage_dir, dir=name_tag, fname=result_file_name),delimiter=',',comments='#')
                        result_csv = np.append(result_csv,[temp_csv],axis=0)
                   
                    #if ua == 0:
                    #    print (np.mean(result_csv[:,6]),np.mean(result_csv[:,7]))
                    if rg == 1 :
                        result_portfolio_rg1 = np.append(result_portfolio_rg1\
                                                        ,[[rp, lp\
                                                            ,np.mean(result_csv[:,4]),np.std(result_csv[:,4]),np.min(result_csv[:,4]),np.max(result_csv[:,4])\
                                                            ,np.mean(result_csv[:,6]),np.std(result_csv[:,6]),np.min(result_csv[:,6]),np.max(result_csv[:,6])\
                                                            ,np.mean(result_csv[:,8]),np.std(result_csv[:,8]),np.min(result_csv[:,8]),np.max(result_csv[:,8])\
                                                            ,np.mean(result_csv[:,10]),np.std(result_csv[:,10]),np.min(result_csv[:,10]),np.max(result_csv[:,10])\
                                                            ,np.mean(result_csv[:,12]),np.std(result_csv[:,12]),np.min(result_csv[:,12]),np.max(result_csv[:,12])\
                                                        ]]\
                                                        ,axis=0)
                        result_benchmark_rg1 = np.append(result_benchmark_rg1\
                                                        ,[[rp, lp\
                                                            ,np.mean(result_csv[:,5]),np.std(result_csv[:,5]),np.min(result_csv[:,5]),np.max(result_csv[:,5])\
                                                            ,np.mean(result_csv[:,7]),np.std(result_csv[:,7]),np.min(result_csv[:,7]),np.max(result_csv[:,7])\
                                                            ,np.mean(result_csv[:,9]),np.std(result_csv[:,9]),np.min(result_csv[:,9]),np.max(result_csv[:,9])\
                                                            ,np.mean(result_csv[:,11]),np.std(result_csv[:,11]),np.min(result_csv[:,11]),np.max(result_csv[:,11])\
                                                            ,np.mean(result_csv[:,13]),np.std(result_csv[:,13]),np.min(result_csv[:,13]),np.max(result_csv[:,13])\
                                                        ]]\
                                                        ,axis=0)
                    else:
                        result_portfolio_rg5 = np.append(result_portfolio_rg5\
                                                        ,[[rp, lp\
                                                            ,np.mean(result_csv[:,4]),np.std(result_csv[:,4]),np.min(result_csv[:,4]),np.max(result_csv[:,4])\
                                                            ,np.mean(result_csv[:,6]),np.std(result_csv[:,6]),np.min(result_csv[:,6]),np.max(result_csv[:,6])\
                                                            ,np.mean(result_csv[:,8]),np.std(result_csv[:,8]),np.min(result_csv[:,8]),np.max(result_csv[:,8])\
                                                            ,np.mean(result_csv[:,10]),np.std(result_csv[:,10]),np.min(result_csv[:,10]),np.max(result_csv[:,10])\
                                                            ,np.mean(result_csv[:,12]),np.std(result_csv[:,12]),np.min(result_csv[:,12]),np.max(result_csv[:,12])\
                                                        ]]\
                                                        ,axis=0)
                        result_benchmark_rg5 = np.append(result_benchmark_rg5\
                                                        ,[[rp, lp\
                                                            ,np.mean(result_csv[:,5]),np.std(result_csv[:,5]),np.min(result_csv[:,5]),np.max(result_csv[:,5])\
                                                            ,np.mean(result_csv[:,7]),np.std(result_csv[:,7]),np.min(result_csv[:,7]),np.max(result_csv[:,7])\
                                                            ,np.mean(result_csv[:,9]),np.std(result_csv[:,9]),np.min(result_csv[:,9]),np.max(result_csv[:,9])\
                                                            ,np.mean(result_csv[:,11]),np.std(result_csv[:,11]),np.min(result_csv[:,11]),np.max(result_csv[:,11])\
                                                            ,np.mean(result_csv[:,13]),np.std(result_csv[:,13]),np.min(result_csv[:,13]),np.max(result_csv[:,13])\
                                                        ]]\
                                                        ,axis=0)
        np.savetxt('{s}/summary_{st}_{t}ua{ua}_rg{rg}_portfolio.csv'.format(s=storage_dir, st=strategy, t=tag, ua=ua, rg=1)\
                    ,result_portfolio_rg1\
                    ,delimiter=','\
                    ,header='rp,lp,E(mdd),s(mdd),min(mdd),max(mdd),E(ar),s(ar),min(ar),max(ar),E(SR1),s(SR1),min(SR1),max(SR1),E(SR2),s(SR2),min(SR2),max(SR2),E(SR3),s(SR3),min(SR3),max(SR3)')
        np.savetxt('{s}/summary_{st}_{t}ua{ua}_rg{rg}_benchmark.csv'.format(s=storage_dir, st=strategy, t=tag, ua=ua, rg=1)\
                    ,result_benchmark_rg1\
                    ,delimiter=','\
                    ,header='rp,lp,E(mdd),s(mdd),min(mdd),max(mdd),E(ar),s(ar),min(ar),max(ar),E(SR1),s(SR1),min(SR1),max(SR1),E(SR2),s(SR2),min(SR2),max(SR2),E(SR3),s(SR3),min(SR3),max(SR3)')
        """
        np.savetxt('{s}/summary_{st}_{t}ua{ua}_rg{rg}_portfolio .csv'.format(s=storage_dir, st=strategy, t=tag, ua=ua, rg=1)\
                    ,result_portfolio_rg5\
                    ,delimiter=','\
                    ,header='rp,lp,E(mdd),s(mdd),min(mdd),max(mdd),E(ar),s(ar),min(ar),max(ar),E(SR1),s(SR1),min(SR1),max(SR1),E(SR2),s(SR2),min(SR2),max(SR2),E(SR3),s(SR3),min(SR3),max(SR3)')
        np.savetxt('{s}/summary_{st}_{t}ua{ua}_rg{rg}_benchmark.csv'.format(s=storage_dir, st=strategy, t=tag, ua=ua, rg=1)\
                    ,result_benchmark_rg5\
                    ,delimiter=','\
                    ,header='rp,lp,E(mdd),s(mdd),min(mdd),max(mdd),E(ar),s(ar),min(ar),max(ar),E(SR1),s(SR1),min(SR1),max(SR1),E(SR2),s(SR2),min(SR2),max(SR2),E(SR3),s(SR3),min(SR3),max(SR3)')
        """
                            