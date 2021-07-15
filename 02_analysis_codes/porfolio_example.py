import os
import sys
# add ../01_main_scripts to the path to find modules
sys.path.append(os.path.abspath('../01_main_scripts'))
# below line could show warning on VScode, but it would work
from portfolio import portfolio
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
from analysis_functions import analyse_history
import gc

print ('portfolio version : ', portfolio.version())

storage_dir = '../00_data/1_pricesData/2_stock'
# declare the back-test porfolio with 'maximiseSR' strategy
backtest_portfolio = portfolio(strategy='maximiseSR',storage_dir=storage_dir)
# initialise the back-test portfolio
backtest_portfolio.init_portfolio(init_date=datetime.date(2018,1,1)\
                                  ,rebal_period   =datetime.timedelta(days=20)\
                                  ,lookback_period=datetime.timedelta(days=60)\
                                  ,rebal_gauge    =datetime.timedelta(days=1)\
                                  ,init_val=100000000\
                                  ,assets=['003670', '192080', '068270', '282330', '035720']\
                                  ,allow_frac=False\
                                  ,risk_free_rate='../00_data/1_pricesData/0_riskFree/KrBond30.csv'\
                                  ,tax_rate=0.00015\
                                  ,eval_bench=True\
                                  ,benchmark_file='../00_data/1_pricesData/1_ETF/069500.csv'\
                                  )
# print out the initialised status
backtest_portfolio.get_initial_status()
# get history in pd.DataFrame starting from the initial date of the porfolio to the latest day
backtest_history = backtest_portfolio.get_history()
# save the history in csv file
backtest_history.to_csv('./example_history.csv')
# print out the current status
backtest_portfolio.get_status()

# analyse the result of back-test history
# the last argument [time_scales] indicate the time scales for [analyse_history] function to draw yield plots
fig, ax, sharpe_ratios, mdds, growth_returns, anual_returns = analyse_history(data= backtest_history,time_scales=[1,20,60])
# print out the returns
print ('-'*50)
print ('Sharpe ratios')
print (sharpe_ratios)

print ('-'*50)
print ('M.D.Ds')
print (mdds)

print ('-'*50)
print ('Growth returns')
print (growth_returns)

print ('-'*50)
print ('Annual returns')
print (anual_returns)
# save the figure and close
plt.savefig('example_fig.png',dpi=fig.dpi, bbox_inches='tight')
plt.close()

sys.exit(0)