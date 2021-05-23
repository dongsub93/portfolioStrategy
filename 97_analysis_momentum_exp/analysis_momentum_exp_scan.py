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

# maximum number of iterations 
max_it = 10
# counting jobs in progress
running_jobs = 0

etf_reits = ['182480']
#etf_gold  = ['139320','132030']
etf_gold  = ['132030']
#etf_bond  = ['114100','114820']
etf_bond  = ['114100']
etf_corp_bond = ['239660']
#etf_stock_indx = ['159800','148020','140950','152870','102110','232080','229200','226490','069500','069660']
etf_stock_indx = ['069500','069660']
#etf_stock_indx = ['069500']


# analyse the case without reits and corp. bond
#tag_fmt = 'maxSR_no-reits_no-cb_ua{it}_rp{rp}_lp{lp}_rg{rg}'
tag_fmt = 'momentum_exp_{t}ua{it}_rp{rp}_lp{lp}_rg{rg}'

for tag in ['','no-reits_','no-cb_','no-reits_no-cb_']:
    it = 0
    for gold in etf_gold:
        for bond in etf_bond:
            for stock_indx in etf_stock_indx:
                if tag == '':
                    underlying_assets = [gold, bond, stock_indx] + etf_corp_bond + etf_reits
                elif tag == 'no-reits_':
                    underlying_assets = [gold, bond, stock_indx] + etf_corp_bond
                elif tag == 'no-cb_':
                    underlying_assets = [gold, bond, stock_indx] + etf_reits
                elif tag == 'no-reits_no-cb_':
                    underlying_assets = [gold, bond, stock_indx]
                # Assign weights exponentially
                asset_weights = [1.]*len(underlying_assets)
                norm_factor=(1.0-np.exp(-1.0*float(len(underlying_assets))))/(1.0-np.exp(-1.0))
                for i in range(len(asset_weights)):
                    asset_weights[i] = np.exp(-1.0*float(i))*norm_factor
                for rp in [1,5,20,40,60,120,225]:
                    for lp in [1,5,20,40,60,120,225]:
#                        for rg in [1,5]:
                        for rg in [1]:
                            if rg >= lp or rp > lp:
                                continue
                            output_dir = './97_analysis_momentum_exp/'+tag_fmt.format(t=tag, it=it,rp=rp,lp=lp,rg=rg)
                            backtest_portfolio = portfolio(strategy='momentum',storage_dir='./00_data/1_pricesData/1_ETF')
                            backtest_portfolio.init_portfolio(init_date=datetime.date(1900,1,1)\
                                                            ,rebal_period   =datetime.timedelta(days=rp)\
                                                            ,lookback_period=datetime.timedelta(days=lp)\
                                                            ,rebal_gauge    =datetime.timedelta(days=rg)\
                                                            ,init_val=100000000\
                                                            ,assets=underlying_assets
                                                            ,weights=asset_weights
                                                            ,allow_frac=False
                                                            ,risk_free_rate='./00_data/1_pricesData/0_riskFree/KrBond30.csv'
                                                            ,tax_rate=0.00015
                                                            ,eval_bench=True
                                                            )
                            init_date = backtest_portfolio.init_date
                            del backtest_portfolio
                            gc.collect()
                            if not os.path.isdir(output_dir):
                                os.mkdir(output_dir)
                            with open(output_dir+'/config_underlying_assets.cofig','w') as f:
                                f.write('underlying assets\n')
                                if tag == 'no-reits_' or tag =='no-reits_no-cb_':
                                    f.write('reits : none\n')
                                else:
                                    f.write('reits : {reits}\n'.format(reits=etf_reits[0]))
                                f.write('gold  : {g}\n'.format(g=gold))
                                f.write('bond  : {b}\n'.format(b=bond))
                                f.write('stock : {s}\n'.format(s=stock_indx))
                                if tag == 'no_bc_' or tag =='no-reits_no-cb_':
                                    f.write('c.b.  : none\n')
                                else:
                                    f.write('c.b.  : {cb}\n'.format(cb=etf_corp_bond[0]))
                            print ('..working on tag {tag}'.format(tag=tag_fmt.format(t=tag, it=it,rp=rp,lp=lp,rg=rg)))
                            weekend_shift = 0
                            for init_shift in range(rp):
                                initial_date = init_date + datetime.timedelta(days=init_shift + weekend_shift)
                                while initial_date.weekday() in [5,6]:
                                    weekend_shift += 1
                                    initial_date = initial_date + datetime.timedelta(days=1)
                                name_tag= tag_fmt.format(t=tag, it=it,rp=rp,lp=lp,rg=rg) + '_shift{init_shift}'.format(init_shift=init_shift)
                                command = 'pythonw analysis_momentum_exp_backtest.py {od} {nt} {ut} {rp} {lp} {rg} {initd}'\
                                        .format(od=output_dir, nt=name_tag, ut=it, rp=rp, lp=lp, rg=rg, initd=str(initial_date))
                                for asset in underlying_assets:
                                    command = command + ' {a}'.format(a=asset)
                                print (command)
                                subprocess.run(['powershell','-Command',command],capture_output=False)
                                running_jobs += 1
                                if running_jobs == max_it or init_shift == rp-1:
                                    print ('...waiting for the last job done.')
                                    start_wait = datetime.datetime.now()
                                    while not os.path.isfile(output_dir+'/result_{tag}.csv'.format(tag=name_tag)):
                                        if (datetime.datetime.now() - start_wait).seconds > 60*30:
                                            print ('Time out while waiting for {tag} job is done.'.format(tag=name_tag))
                                            break
                                        continue
                                        #time.sleep(30)
                                    running_jobs = 0
                it += 1
