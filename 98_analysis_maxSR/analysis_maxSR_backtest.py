import os
import sys
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



output_dir  = str(sys.argv[1])
name_tag    = str(sys.argv[2])
ua_tag      = int(sys.argv[3])
rebal_period= int(sys.argv[4])
lb_period   = int(sys.argv[5])
rebal_gauge = int(sys.argv[6])
initial_date= str_to_date(str(sys.argv[7]))
underlying_assets = sys.argv[8:]
"""
reits = str(sys.argv[5])
gold  = str(sys.argv[6])
bond  = str(sys.argv[7])
stock_x = str(sys.argv[8])
corp_bond = str(sys.argv[9])
"""

stdout_original = sys.stdout
sys.stdout = open(output_dir+'/out_'+name_tag+'.out','w')

result_np = np.array([]).reshape((0,14))
print ('..working on tag {t}'.format(t=name_tag))
backtest_portfolio = portfolio(strategy='maximiseSR',storage_dir='./00_data/1_pricesData/1_ETF')
backtest_portfolio.init_portfolio(init_date=initial_date\
                                  ,rebal_period   =datetime.timedelta(days=rebal_period)\
                                  ,lookback_period=datetime.timedelta(days=lb_period)\
                                  ,rebal_gauge    =datetime.timedelta(days=rebal_gauge)\
                                  ,init_val=100000000\
                                  ,assets=underlying_assets\
                                  ,allow_frac=False\
                                  ,risk_free_rate='./00_data/1_pricesData/0_riskFree/KrBond30.csv'\
                                  ,tax_rate=0.00015\
                                  ,eval_bench=True\
                                  )
backtest_portfolio.get_initial_status()

backtest_history = backtest_portfolio.get_history()
backtest_history.to_csv(output_dir+'/history_'+name_tag+'.csv')
fig, ax, sharpe_ratios, mdds, growth_returns, anual_returns = analyse_history(backtest_history,[1,20,60])
plt.savefig(output_dir+'/fig_'+name_tag+'.png',dpi=fig.dpi, bbox_inches='tight')

result_np = np.append(result_np\
                      ,[[ua_tag, rebal_period, lb_period, rebal_gauge\
                        ,mdds[0], mdds[1]\
                        ,anual_returns[0], anual_returns[1]\
                        ,sharpe_ratios[0][0], sharpe_ratios[1][0]\
                        ,sharpe_ratios[0][1], sharpe_ratios[1][1]\
                        ,sharpe_ratios[0][2], sharpe_ratios[1][2]\
                       ]]
                      ,axis=0)

np.savetxt(output_dir+'/result_{tag}.csv'.format(tag=name_tag)\
           ,result_np\
           ,delimiter=','\
           ,header='underlyings_assets_config,rebal_period,lookback_period,rebal_gauge\
                   ,mdd_portfolio,mdd_benchmark\
                   ,ar_portfolio,ar_benchmark\
                   ,SR0_portfolio,SR0_benchmark\
                   ,SR1_portfolio,SR1_benchmark\
                   ,SR2_portfolio,SR2_benchmark\
           ')
backtest_portfolio.get_status()
plt.close('all')
del [backtest_history, backtest_portfolio]
gc.collect()
print ('Done.')
sys.stdout.close()
sys.stdout = stdout_original
