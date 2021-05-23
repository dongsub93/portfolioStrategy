import os
import sys
from datetime import date 
from datetime import timedelta as td
import pandas as pd
import numpy as np
#sys.path.append(os.path.abspath('../'))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from aux_functions import get_MDD
from aux_functions import get_maxSR
from aux_functions import str_to_date
from aux_functions import verbose

class portfolio:
    """
        class of three portfolio strategeies
            * dependencies
                - basic modules(os, sys, datetime.date, datetim.timedetla)
                - pandas
                - numpy
                - ../aux_functoins
            * aliasing
                - np : numpy
                - pd : pandas
                - td : timedelta( datetime.timedelta )
            * strategies
                - fixed_weight : portfolio using fixed weights for asset allocation
                - momentum     : portfolio using momentum
                - maximiseSR   : portfolio maximising Sharpe ratio(SR) of assets
    """
    # class instance determine to print level. class instance will print only above or equal to the allowed level
    k_print  = 0
    k_warning= 1
    k_error  = 2
    @classmethod
    def version(cls):
        return '1.5.0'

    @classmethod
    def strategies(cls):
        print ('='*50)
        print ('* class : portfolio ')
        print ('  - version : ',cls.version)
        print ('  - possible strategies : fixed_weight, momentum, maximiseSR')
        print ('='*50)
        
    def __init__(self, strategy:str = None\
                     , init_date:date = date.today()\
                     , init_val:float = 0.\
                     , tax_rate:float = 0.0\
                     , assets=[]\
                     , weights=[]\
                     , rebal_period:td = td(days=1)\
                     , rebal_gauge:td = td(days=1)\
                     , lookback_period:td = td(days=1)\
                     , storage_dir:str = None\
                     , risk_free_rate:str = None\
                     , mode:str = 'backtest'\
                     , allow_frac:bool = False\
                     , veto_negative:bool = True\
                     , eval_bench:bool = True\
                ):
        # private variable
        self._verbose = portfolio.k_warning

        # basic elements of portfolio
        self.strategy  = strategy
        if self.strategy == None:
            raise ValueError('[portfolio] Strategy must be specified')
        elif self.strategy not in ['fixed_weight','momentum','maximiseSR']:
            raise ValueError('[portfolio] {s} is not defined strategy.'.format(s=self.strategy))

        self.init_date = init_date
        self.init_val  = init_val
        self.tax_rate  = tax_rate

        # underlying assets
        self.assets    = assets
        self.weights   = weights
        
        # reblancing configuration
        self.rebal_period   = rebal_period
        self.rebal_gauge    = rebal_gauge
        self.lookback_period= lookback_period
        
        # data specification and portfolio specifiction(backtest/investment)
        self.storage_dir   = storage_dir if storage_dir != None else '.'
        self.risk_free_rate= risk_free_rate
        self.mode          = mode

        # other variables
        self.allow_frac    = allow_frac
        self.veto_negative = veto_negative
        self.eval_bench    = eval_bench
        
        # automatically determined elemetns
        self.date          = self.init_date
        self.portfolio_val = self.init_val
        self.portion       = dict(zip(self.assets, [0.]*len(self.assets) ))
        self.avg_price     = dict(zip(self.assets, [0.]*len(self.assets) ))
        self.total_tax     = 0.0

        # initialise portfolio history
        _df_cols = np.array(['date','portfolio_value'])
        for tag in ['t','n','p']:
            for asset in self.assets:
                _df_cols  = np.append(_df_cols, tag+asset)
        _df_cols = np.append(_df_cols, ['cash','benchmark_value','rf','rebalancing'])
        self.history = pd.DataFrame(columns = _df_cols)

    def init_portfolio(self, init_date:date = date.today()\
                           , init_val:float = 0.\
                           , tax_rate:float = 0.0\
                           , assets=[]\
                           , weights=[]\
                           , rebal_period:td = td(days=1)\
                           , rebal_gauge:td = td(days=1)\
                           , lookback_period:td = td(days=1)\
                           , storage_dir:str = None\
                           , risk_free_rate:str = None\
                           , mode:str = 'backtest'\
                           , allow_frac:bool = False\
                           , veto_negative:bool = True\
                           , eval_bench:bool = True\
                    ):
        if self.strategy == 'maximiseSR':
            verbose(self._verbose, portfolio.k_warning, 'weight -> deprecated in this strategy. It will automatically determine weights of assets.')
        else:
            verbose(self._verbose, portfolio.k_warning, 'rebal_gauge -> deprecated in this strategy. It is not relevant for this strategy.')

        # basic elements of portfolio
        self.init_date = init_date
        self.init_val  = init_val
        self.tax_rate  = tax_rate

        # underlying assets
        self.assets    = assets
        if len(self.assets) == 0:
            raise ValueError('[portfolio:init_portfolio] Cannot initialise portfolio. It requires at least one asset.')
        self.weights   = weights if self.strategy != 'maximiseSR' else [1.0/float(len(self.assets))]*len(self.assets)
        if self.strategy != 'maximiseSR' and len(self.weights) != len(self.assets):
            raise ValueError('[portfolio:init_portfolio] {s} strategy requires proper weights input to asset allocation.'\
                            .format(s=self.strategy))
        if self.strategy == 'momentum':
            verbose(self._verbose, portfolio.k_warning, '[portfolio:init_portfolio] momentum portfolio will automatically sorts the weights in descending order.')
            self.weights.sort(reverse=True)
        
        # reblancing configuration
        self.rebal_period   = rebal_period
        self.rebal_gauge    = rebal_gauge
        self.lookback_period= lookback_period

        # data specification and portfolio specifiction(backtest/investment)
        self.storage_dir   = storage_dir if storage_dir != None else self.storage_dir
        self.risk_free_rate= risk_free_rate
        self.mode          = mode

        # other variables
        self.allow_frac    = allow_frac
        self.veto_negative = veto_negative
        self.eval_bench    = eval_bench

        # automatically determined elemetns
        self.date          = self.init_date
        self.portfolio_val = self.init_val
        self.cash          = self.portfolio_val
        self.avg_price     = dict(zip(self.assets, [0.]*len(self.assets) ))
        self.portion       = dict(zip(self.assets, [0.]*len(self.assets) ))
        self.total_tax     = 0.0
        self.dates_from_rebal= td(days=0)

        # initialise private instances of the number(_n_asset), the total amount(_t_asset),
        # and the array of returns(_r_asset) of the assets
        self._n_asset = dict([(asset,0) for asset in self.assets])
        self._t_asset = dict([(asset,0) for asset in self.assets])
        self._r_asset = dict([(asset,np.array([1.])) for asset in self.assets])

        # initialise portfolio history
        _df_cols = np.array(['date','portfolio_value'])
        for tag in ['t','n','p']:
            for asset in self.assets:
                _df_cols  = np.append(_df_cols, tag+asset)
        _df_cols = np.append(_df_cols, ['cash','benchmark_value','rf_yield','rebalancing'])
        self.history = pd.DataFrame(columns = _df_cols)

        # load related data of assets
        try:
            self.load_history()
            init_dates = np.array([ data.iloc[-1]['날짜'] for data in self.asset_data.values() ])
            if self.init_date < max(init_dates):
                verbose(self._verbose, portfolio.k_warning, '[portfolio:init_portfolio] Initial date is even prior to the head of the data. Replace it by ',max(init_dates))
                self.init_date = max(init_dates)
                self.date      = self.init_date
        except ValueError:
            verbose(self._verbose, portfolio.k_error, '[portfolio] Cannot load all relevant data.')
            return False

        # initialise the array of rf's.
        date_it = self.init_date
        rf_yield= 1.0
        while date_it >= self._rf_data.iloc[-1,0]:
            try:
                rf_yield = self._rf_data.loc[self._rf_data['date']==date_it].iloc[0]['interest']
                break
            except:
                date_it = date_it - td(days=1)
        self._rf_yield = np.array([rf_yield])

        # make first transaction
        while True:
            try:
                self.price = dict([(asset, data.loc[data['날짜']==self.date].iloc[0]['종가'])\
                                    for asset, data in self.asset_data.items() ])
                break
            except:
                self.date = self.date + td(days=1)
        self.price = dict(sorted(self.price.items(), key=lambda x:x[1], reverse=False))
        transitions= dict([(asset, self.weights[it]-self.portion[asset]) for it, asset in enumerate(self.price.keys()) ])
        self.transaction(transitions)

        # filling the first row of history
        row = [None]*len(self.history.columns)
        row[0] = self.init_date
        row[1] = self.portfolio_val
        for it, asset in enumerate(self.assets):
                row[2+it] = self._t_asset[asset]
                row[2+len(self.assets)+it] = self._n_asset[asset]
                row[2+2*len(self.assets)+it] = self.price[asset]
        row[-4] = self.cash
        row[-3] = self.portfolio_val if self.eval_bench else 0.0
        row[-2] = rf_yield
        row[-1] = True
        self.history.loc[0] = row

        # initialise benchmark portfolio
        if self.eval_bench:
            verbose(self._verbose, portfolio.k_print, '[portfolio:init_portfolio] Initialise benchmark portfolio.')
            self.benchmark = portfolio('fixed_weight')
            self.benchmark._verbose = portfolio.k_error
            self.benchmark.init_portfolio(init_date = self.init_date\
                                        ,init_val = self.init_val\
                                        ,tax_rate = self.tax_rate\
                                        ,assets   = self.assets\
                                        ,weights  = [1.0/float(len(self.assets))]*len(self.assets)\
                                        ,rebal_period   = self.rebal_period\
                                        ,lookback_period= self.lookback_period\
                                        ,storage_dir    = self.storage_dir\
                                        ,risk_free_rate = self.risk_free_rate\
                                        ,allow_frac   = False\
                                        ,veto_negative= True\
                                        ,eval_bench   = False\
                                        )	
        return True

    
    def set_storage(self, storage_dir:str):
        verbose(self._verbose, portfolio.k_print, '[portfolio] Set storage path : ',storage_dir)
        self.storage_dir = storage_dir

    def load_history(self):
        self.asset_data = {}
        verbose(self._verbose, portfolio.k_print, '[portfolio:load_history] ...Try to load price data of assets.')
        for asset in self.assets:
            try:
                self.asset_data[asset] = pd.read_csv(self.storage_dir+'/{a}.csv'.format(a=asset),encoding='utf-8',dtype='str',index_col=0)
            except:
                raise ValueError('[portfolio:load_history] Cannot load data of {a}.'.format(a=self.storage_dir+asset))

            for i in range(len(self.asset_data[asset])):
                self.asset_data[asset].iloc[i]['날짜']=str_to_date(self.asset_data[asset].iloc[i]['날짜'])
            self.asset_data[asset][['종가','시가','거래량']]=self.asset_data[asset][['종가','시가','거래량']].apply(pd.to_numeric)
        verbose(self._verbose, portfolio.k_print, '[portfolio:load_history] Done.')

        verbose(self._verbose, portfolio.k_print, '[portfolio:load_history] ...Try to load risk free rate data.')
        try:
            self._rf_data = pd.read_csv(self.risk_free_rate,encoding='utf-8',dtype='str',index_col=0)	
            self._rf_data = self._rf_data.apply(lambda x: [str_to_date(x[0]), np.power(float(x[1]),1./252.)]\
                                                                                    ,axis=1\
                                                                                    ,result_type='broadcast')
            self._rf_data = self._rf_data.sort_values(by=['date'], ascending=False)
            self._rf_data.index = range(len(self._rf_data))
        except:
            verbose(self._verbose, portfolio.k_warning, '[portfolio:load_history] Cannot load risk free rate data. Prociding fictitious data with rf=0.')
            self._rf_data = pd.DataFrame(columns=['date','interest']\
                                                                    ,index=range(len(self.asset_data[self.assets[0]]['날짜'].values))\
                                                                    ,data=np.array([self.asset_data[self.assets[0]]['날짜'].values\
                                                                                                 ,[1.0]*len(self.asset_data[self.assets[0]]['날짜'].values)\
                                                                                                 ]).T\
                                                                    )
        verbose(self._verbose, portfolio.k_print, '[portfolio:load_history] Done.')

    def get_initial_status(self):
        print ('='*60)
        print ('Initial condition of the portfolio')
        print ('strategy         : ',self.strategy)
        print ('-'*60)
        print ('Storage path     : ',self.storage_dir)
        print ('assets           : ',self.assets)
        if self.strategy == 'maximiseSR':
            print ('weights          : ',self.weights, ' -> deprecated in this strategy.')
        else:
            print ('weights          : ',self.weights)
        print ('Initial value    : ',self.init_val)
        print ('Initial date     : ',self.init_date)
        print ('rebal. period    : ',self.rebal_period.days,' days')
        if not self.strategy == 'maximiseSR':
            print ('rebal. gauge     : ',self.rebal_gauge.days, ' days -> deprecated in this strategy.')
        else:
            print ('rebal. gauge     : ',self.rebal_gauge.days, ' days')
        print ('look-back period : ',self.lookback_period.days,' days')
        print ('allos fract.     : ',self.allow_frac)
        print ('veto (-) yeidls  : ',self.veto_negative)
        print ('Benchmark        : Equal-weight portfolio')
        print ('Risk-free intrst.: ', self.risk_free_rate)
        print ('='*60)

    def get_status(self):
        p_mdd, p_mdd_from, p_mdd_to = get_MDD(self.history)
        prices = dict([(asset,data.loc[data['날짜']==self.date].iloc[0]['종가']) for asset, data in self.asset_data.items()])
        print ('='*60)
        print (' - status of portfolio -')
        print ('* portfolio strategy : ',self.strategy)
        print ('* underlying assets  : ',self.assets)
        print ('-'*60)
        print ('* date      : ',self.date)
        print ('* value     : ',self.portfolio_val, '(initial value = {i})'.format(i=self.init_val))
        print ('-'*60)
        print ('* returns')
        print (' after tax  : {g:3.2f}% (growth), {a:3.2f}% (annual)'\
                            .format(g=100.*(-1.0+self.portfolio_val/self.init_val)\
                                            ,a=100.*(-1.0+pow(self.portfolio_val/self.init_val,252.0/float(len(self.history))))\
                                            )\
                    )
        if self.eval_bench:
            print (' |-benchmark: {g:3.2f}% (growth), {a:3.2f}% (annual)'\
                    .format(g=100.*(-1.0+self.history['benchmark_value'].values[-1]/self.init_val)\
                                    ,a=100.*(-1.0+pow(self.history['benchmark_value'].values[-1]/self.init_val,252.0/float(len(self.history))))\
                                    )\
                        )
        print ('before tax  : {g:3.2f}% (growth), {a:3.2f}% (annual)'\
                            .format(g=100.*(-1.0+(self.total_tax+self.portfolio_val)/self.init_val)\
                                            ,a=100.*(-1.0+pow((self.total_tax+self.portfolio_val)/self.init_val,252.0/float(len(self.history))))\
                                            )\
                    )
        if self.eval_bench:
            print (' |-benchmark: {g:3.2f}% (growth), {a:3.2f}% (annual)'\
                .format(g=100.*(-1.0+(self.benchmark.total_tax+self.history['benchmark_value'].values[-1])/self.init_val)\
                        ,a=100.*(-1.0+pow((self.benchmark.total_tax+self.history['benchmark_value'].values[-1])/self.init_val,252.0/float(len(self.history))))\
                        )\
                  )
        print ('-'*60)
        print ('* tax')
        print ('total tax   : {t}({p:2.2f}% of profit)'\
            .format(t=self.total_tax\
                    ,p=100.*self.total_tax/(self.portfolio_val-self.init_val) if self.portfolio_val > self.init_val else 0.0\
                    )\
              )
        if self.eval_bench:
            print (' |-benchmark: {t}({p:2.2f}% of profit)'\
            .format(t=self.benchmark.total_tax\
                    ,p=100.*self.benchmark.total_tax/(self.benchmark.portfolio_val-self.init_val) if self.benchmark.portfolio_val > self.init_val else 0.0\
                    )\
              )
        print ('-'*60)
        print ('* maximum drawdown(m.d.d.)')
        print ('m.d.d.      : {mdd:3.3f}% from {f} to {t}'.format(mdd=p_mdd, f=p_mdd_from, t=p_mdd_to))
        if self.eval_bench:
            b_mdd, b_mdd_from, b_mdd_to = get_MDD(self.history, 'benchmark_value')
            print (' |-benchmark: {mdd:3.3f}% from {f} to {t}'.format(mdd=b_mdd, f=b_mdd_from, t=b_mdd_to))
        print ('-'*60)
        print ('Inventory')
        for asset in self.assets:
            mdd, mdd_from, mdd_to = get_MDD(self.history, asset, self.init_date, self.date)
            print ('   |= {c}      : total {t} ({p:3.2f}%)'\
                    .format(c=asset,t=self._t_asset[asset], p=100.0*self._t_asset[asset]/self.portfolio_val))
            if asset != self.assets[-1] :
                print ('   |   |- volume  : ',int(self._n_asset[asset]))
                print ('   |   |- prices  : ',prices[asset])
                print ('   |   |- MDD     :  {mdd:3.3f}%(from {a} to {b})'.format(mdd=mdd,a=mdd_from,b=mdd_to))
                print ('   |   |- return  :  {r:3.2f}% (annual : {a:3.2f}%)'\
                        .format(r=100.0*(-1.0+prices[asset]/self.history['p'+asset].values[0])\
                        ,a=100.0*(-1.0+pow(prices[asset]/self.history['p'+asset].values[0],252.0/float(len(self.history))))\
                        )
                      )
            else:
                print ('       |- volume  : ',int(self._n_asset[asset]))
                print ('       |- prices  : ',prices[asset])
                print ('       |- MDD     :  {mdd:3.2f}%(from {a} to {b})'.format(mdd=mdd,a=mdd_from,b=mdd_to))
                print ('       |- return  :  {r:3.2f}% (annual : {a:3.2f}%)'\
                    .format(r=100.0*(-1.0+prices[asset]/self.history['p'+asset].values[0])\
                        ,a=100.0*(-1.0+pow(prices[asset]/self.history['p'+asset].values[0],252.0/float(len(self.history))))\
                            )
                     )
        print ('-'*60)
        print ('Last rebalancing : {d} days ago'.format(d=self.dates_from_rebal.days))
        print ('='*60)

    def elapse(self, interval:td = td(days=1)):
        elapsed = td(days=0)
        dates   = dict([ (asset,data['날짜'].values) for asset, data in self.asset_data.items() ])
        is_eof  = False
        while elapsed < interval:
            # if [self.date] reaches to the end of any data, it breaks the iteration
            if any(self.date + td(days=1) > date[0] for date in dates.values() ):
                verbose(self._verbose, portfolio.k_warning, '[portfolio:elapse] Stop passing time. It reached to the end of the data.')
                is_eof = True
                break
            else:
                self.date = self.date + td(days=1)

            # get indexes of price data of each asset corresponding [self.date] while passing days
            indexes = dict([ (asset, np.where(dates[asset]==self.date)[0]) for asset in self.assets ])
            while any( len(index) == 0 for index in indexes.values() ):
                if any( self.date + td(days=1) > date[0] for date in dates.values() ):
                    verbose(self._verbose, portfolio.k_warning, '[portfolio:elapse] Stop passing time. It reached to the end of the data.')
                    is_eof = True
                    break
                else:
                    self.date = self.date + td(days=1)
                    indexes = dict([ (asset, np.where(dates[asset]==self.date)[0]) for asset in self.assets ])
            if is_eof:
                break

            # passing time
            elapsed = elapsed + td(days=1)
            self.dates_from_rebal = self.dates_from_rebal + td(days=1)

            # rebalancing if needed
            if self.dates_from_rebal == self.rebal_period:
                # evaluate the required portion after rebalancing
                if self.strategy == 'fixed_weight':
                    required_portion = self.fw_rebal()
                elif self.strategy == 'momentum':
                    required_portion = self.mom_rebal()
                elif self.strategy == 'maximiseSR':
                    required_portion = self.maxSR_rebal()
                # get prices of each asset to carry orders
                self.price = dict([ (asset, self.asset_data[asset].iloc[indexes[asset][0]]['종가']) for asset in self.assets ])
                # carry transaction on rebalancing with today's prices. It will automatically update the stocks.
                self.transaction(required_portion)
            else:
                # not in rebalancing day, record the price, the total amount, and the portion of assets with portfolio value
                self.price = dict([ (asset, self.asset_data[asset].iloc[indexes[asset][0]]['종가']) for asset in self.assets ])
                self._t_asset = dict([ (asset, self._n_asset[asset]*price) for asset, price in self.price.items() ])
                self.portfolio_val = self.cash + sum(self._t_asset.values())
                self.portion = dict([ (asset, total/self.portfolio_val) for asset, total in self._t_asset.items() ])

            # appending returns(1+r) of each asset to corresponding arrays
            for asset in self._r_asset.keys():
                self._r_asset[asset] = np.append(self._r_asset[asset]
                                                ,self.asset_data[asset].iloc[indexes[asset][0]]['종가']\
                                                    /self.asset_data[asset].iloc[indexes[asset][0]+1]['종가']\
                                                )

            # get the latest returns of risk free rate and appending to the array(_rf_yield)
            date_it = self.date
            rf_yield= 1.0
            while date_it >= self._rf_data.iloc[-1,0]:
                try:
                    rf_yield = self._rf_data.loc[self._rf_data['date']==date_it].iloc[0]['interest']
                    break
                except:
                    date_it = date_it - td(days=1)
            self._rf_yield = np.append(self._rf_yield, rf_yield)

            # appending the corresponding information to the history
            row = [None]*len(self.history.columns)
            row[0] = self.date
            row[1] = self.portfolio_val
            for it, asset in enumerate(self.assets):
                    row[2+it] = self._t_asset[asset]
                    row[2+len(self.assets)+it] = self._n_asset[asset]
                    row[2+2*len(self.assets)+it] = self.price[asset]
            row[-4] = self.cash
            # (-3)-th column is value of benchmark portfolio. It will be evaluated outside the while-loop.
            row[-3] = 0.0
            row[-2] = rf_yield
            row[-1] = True if self.dates_from_rebal.days == 0 else False
            self.history.loc[len(self.history)] = row

        if self.eval_bench:
                verbose(self._verbose, portfolio.k_print, '[portfolio:elapse] evaluate benchmark portfolio.')
                self.benchmark.elapse(interval)
                self.history['benchmark_value'] = self.benchmark.history['portfolio_value']

    def transaction(self, required_portion:dict):
        """
            Carry transaction. It reqruires [required_portion:dict], which indicates the desired portion after rebalancing.
        """
        tax = 0.0
        # amount of changes
        changes = dict([(asset, (required-self.portion[asset])*self.price[asset]) for asset, required in required_portion.items()])
        changes = dict(sorted(changes.items(),key=lambda x: (x[1] if x[1] <= 0.0 else 1.0/x[1]), reverse=False ))
        # transactions are carried in [short -> huge long -> small long] order.
        required_portion = dict([(asset, required_portion[asset]) for asset in changes.keys()])
        for asset, portion in required_portion.items():
            # evaluates new volume([new_volume]) that we want to keep for [asset] and corresponding stock changes([delta_n]).
            try:
                new_n = max(0, self.portfolio_val*portion/self.price[asset])\
                         if self.allow_frac	else\
                        max(0, np.floor(self.portfolio_val*portion/self.price[asset]))
            except:
                verbose(self._verbose, portfolio.k_warning, '[portfolio:transaction] {a} has 0 price at {d}, it will be sold.'.format(a=asset,d=self.date))
                new_n = 0.0

            # prevent negative portion due to round-off errors.
            delta_n = max(new_n - self._n_asset[asset],-self._n_asset[asset])
            # taking short position pays tax, and increases cash.
            if delta_n < 0.0:
                tax -= delta_n*self.price[asset]*self.tax_rate
                # remind that delta_n < 0 in this case.
                self.cash = self.cash - delta_n*self.price[asset]*(1.0-self.tax_rate)
            # taking long position can only be done with cash we have.
            if delta_n > 0.0:
                # estimates the required costs of taking long position with todays' price of [asset].
                cost = delta_n*self.price[asset]
                # if the cost exceed the cash([self.cash]), replace the amount of the order.
                if cost > self.cash:
                    # [feas_delta_n] is feasible amount of changes in stock of [asset]
                    feas_delta_n = self.cash/self.price[asset] if self.allow_frac else np.floor(self.cash/self.price[asset])
                    verbose(self._verbose, portfolio.k_print\
                            ,'[portfolio:transaction] {d}, current cash is not eough to carry order.'.format(d=self.date))
                    verbose(self._verbose, portfolio.k_print\
                            ,'                       For {a}, necessary cost is {cost} but only has {cash} in cash.'\
                            .format(a=asset, cost=cost, cash=self.cash))
                    verbose(self._verbose,portfolio.k_print\
                            ,'                       -> Desired volume change was {d}, but will only buy {f}.'\
                            .format(d=delta_n,f=feas_delta_n))
                    delta_n = feas_delta_n
                # update average price of [asset].
                if self._n_asset[asset]+delta_n > 0.:
                    self.avg_price[asset] = (self.avg_price[asset]*self._n_asset[asset] + delta_n*self.price[asset])\
                                                                        /(self._n_asset[asset]+delta_n)
                # paying cash to buy [asset] without paying tax.
                self.cash = self.cash - delta_n*self.price[asset]
            # update the total amount(_t_asset[asset]) and the number (_n_asset[asset]) of the [asset].
            self._t_asset[asset] = max(0,self._n_asset[asset] + delta_n)*self.price[asset]
            self._n_asset[asset] = max(0,self._n_asset[asset] + delta_n)
            
            if self._n_asset[asset] == 0.0:
                self.avg_price[asset] = 0.0
        self.total_tax    += tax
        self.portfolio_val = self.cash + sum(self._t_asset.values())
        self.portion       = dict([(asset,total/self.portfolio_val) for asset, total in self._t_asset.items() ])
        if self.mode == 'backtest':
            pass
        elif self.mode == 'investment':
            verbose(self._verbose, portfolio.k_error, 'This is not developed yet.')
        
    def get_history(self, start=None, end:date = date.today()):
        if start == None or start < self.history['date'].values[0]:
            start = self.history['date'].values[0]
        if start > end:
            verbose(self._verbose, portfolio.k_warning, '[portfolio:get_history] (start) is later than (end). Switching them.')
            dummy = start
            start = end
            end   = dummy
            del dummy
        # initialise portfolio and elapsing time
        # temporally makes it quite
        verbose(self._verbose, portfolio.k_print, '[portfolio:get_history] initialise portfolio agains to get history.')
        self._verbose = portfolio.k_error
        self.init_portfolio(init_date = self.init_date
                            ,init_val  = self.init_val
                            ,tax_rate  = self.tax_rate
                            ,assets    = self.assets
                            ,weights   = self.weights
                            ,rebal_period = self.rebal_period
                            ,rebal_gauge  = self.rebal_gauge
                            ,lookback_period = self.lookback_period
                            ,storage_dir  = self.storage_dir
                            ,risk_free_rate= self.risk_free_rate
                            ,allow_frac= self.allow_frac
                            ,veto_negative = self.veto_negative
                            ,eval_bench= self.eval_bench
                            )
        self._verbose = portfolio.k_warning
        self.elapse(end-self.init_date)
    
        dates   = self.history['date'].values
        # get the index of history corresponding to the start of the time interval.
        i_start = np.where(dates==start)[0]
        while len(i_start) == 0:
            if start - td(days=1) < dates[0]:
                verbose(self._verbose, portfolio.k_error, '[portfolio:get_history] There is no day included in the interval.')
                return None
            else:
                start = start - td(days=1)
                i_start = np.where(dates==start)[0]
        # get the index of history corresponding to the end of the time interval.
        i_end = np.where(dates==end)[0]
        while len(i_end) == 0:
            if end - td(days=1) < dates[0]:
                verbose(self._verbose, portfolio.k_error, '[portfolio:get_history] There is no day included in the interval.')
                return None
            else:
                end = end - td(days=1)
                i_end = np.where(dates==end)[0]

        # make slice of the history corresponding the time interval
        result = self.history.iloc[i_start[0]:i_end[0]+1]
        result.index = range(len(result))
        return result

    def fw_rebal(self):
        self.dates_from_rebal = td(days=0)
        # length of the lookback period 
        lb_len = int(np.ceil(self.lookback_period/td(days=1)))
        # mean prices during the lookback period
        mean_price = {}
        for asset, data in self.asset_data.items():
            index = np.where(data['날짜'].values == self.date)[0][0]
            mean_price[asset] = np.mean(data.loc[max(0,index-lb_len):index+1,'종가'].values)
        mean_price = dict(sorted(mean_price.items(), key=lambda x:x[1], reverse=True))
        # evaluate the updated portions of the assets
        updated_portion = dict([ (asset, self.weights[it]) for it, asset in enumerate(mean_price.keys()) ])
        return updated_portion

    def mom_rebal(self):
        self.dates_from_rebal = td(days=0)
        # length of the lookback period 
        lb_len = int(np.ceil(self.lookback_period/td(days=1)))

        # time-averaged returns of assets in the lookback period
        avg_returns = dict([ (asset, np.product(returns[max(0,len(returns)-lb_len):]) )\
                                                for asset, returns in self._r_asset.items() \
                                            ])
        avg_returns = dict(sorted(avg_returns.items(), key=lambda x:x[1], reverse=True))

        # time-averaged return of the risk-free asset
        avg_rf = np.product(self._rf_yield[max(0,len(self._rf_yield)-lb_len):])
        #	evaluate the updated portions of the assets

        updated_portion = {}
        for it, asset in enumerate(avg_returns.keys()):
            if self.veto_negative and avg_returns[asset] < avg_rf:
                updated_portion[asset] = 0.0
            else:
                updated_portion[asset] = self.weights[it]

        if sum(updated_portion.values()) == 0.0:
            verbose(self._verbose, portfolio.k_warning, '[portfolio:rebalancing-momentum] {d}, all assets have returns lower than risk-free asset.'.format(d=self.date))
        else:
            renorm_factor = 1.0/float(sum(updated_portion.values()))
            for asset in updated_portion.keys():
                    updated_portion[asset] = renorm_factor*updated_portion[asset]

        return updated_portion

    def maxSR_rebal(self):
        self.dates_from_rebal = td(days=0)
        # length of the lookback period 
        lb_len = int(np.ceil(self.lookback_period/td(days=1)))
        # rebalancing gauge, unit time of evaluating measures
        r_gauge= int(np.ceil(self.rebal_gauge/td(days=1)))
        # compress returns of assets corrsponding to [self.rebal_gauge] and [self.lookback_period]
        returns = dict([(asset\
                        ,np.array([ np.product(data[it:it+r_gauge])\
                                    if it + r_gauge <= len(data) else\
                                    np.power(np.product(data[it:]), float(r_gauge)/float(it+r_gauge-len(data)))\
                                    for it in range(max(0,len(data)-lb_len),len(data),r_gauge)\
                                ])\
                        )\
                        for asset, data in self._r_asset.items()\
                 ])
        # compress returns of risk-free asset corrsponding to [self.rebal_gauge] and [self.lookback_period]
        rf_return = np.array([ np.product(self._rf_yield[it:it+r_gauge])\
                              if it + r_gauge <= len(self._rf_yield) else\
                            np.power(np.product(self._rf_yield[it:]),float(r_gauge)/float(it+r_gauge-len(self._rf_yield)))\
                            for it in range(max(0,len(self._rf_yield)-lb_len),len(self._rf_yield),r_gauge)\
                            ])
        rf_mean   = np.mean(rf_return)
        # sort returns of assets in descending order with respect to the Sharpe ratios.
        returns   = dict(sorted( returns.items()\
                                ,key=lambda x:   np.arctan2(np.mean(x[1])-rf_mean,np.std(x[1]))\
                                ,reverse=True\
                                )\
                        )

        # evaluate the updated portions of assets to maximise the Sharpe ratio
        updated_portion = dict([(asset, 0) for asset in returns.keys() ])
        updated_portion[list(returns.keys())[0]] = 1.0
        covariance = np.cov(np.array( list(returns.values()) ))
        for it_0, asset_0 in enumerate(returns.keys()):
            if it_0 == 0:
                continue
            r1, var1, cov = 0.0, 0.0, 0.0
            for it_1 in range(it_0):
                asset_1 = list(returns.keys())[it_1]
                r1 += updated_portion[asset_1]*np.mean(returns[asset_1])
                cov+= updated_portion[asset_1]*covariance[it_0][it_1]
                for it_2 in range(it_0):
                    asset_2 = list(returns.keys())[it_2]
                    var1 += updated_portion[asset_1]*updated_portion[asset_2]*covariance[it_1][it_2]
            
            r2, var2 = np.mean(returns[asset_0]), covariance[it_0][it_0]
            [maxSR, w1, w2] = get_maxSR(rf_mean, r1, r2, var1, var2, cov)
            for it_1 in range(it_0):
                asset_1 = list(returns.keys())[it_1]
                updated_portion[asset_1] = updated_portion[asset_1]*w1
            updated_portion[asset_0] = w2

        if maxSR < 0.0 and self.veto_negative:
            verbose(self._verbose, portfolio.k_warning, '[portfolio:rebalancing - maximiseSR] {d}, Optimised portfolio has negative SR. Reject all assets.'\
                            .format(d=self.date))
            updated_portion = dict([(asset, 0) for asset in returns.keys() ])
        
        return updated_portion

