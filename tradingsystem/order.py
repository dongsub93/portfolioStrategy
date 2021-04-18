import ctypes
import win32com.client
import balance

cpt_util = win32com.client.Dispatch("CpTrade.CpTdUtil")
cpt_order = win32com.client.Dispatch("CpTrade.CpTd0311")

cpt_util.TradeInit()
acc = cpt_util.AccountNumber[0]
acc_flac = cpt_util.GoodsList(acc, 1)


def order(position, code, amount, price, condition=None):
    



    if position == 'sell' or 'short':
        cpt_order.SetInputValue(0, '1')     # 1: sell 2: buy
    elif position == 'buy' or 'long':
        cpt_order.SetInputValue(0, '2')
    else:
        print('ERROR: Cannot understand the requested trading position.')
        
    cpt_order.SetInputValue(1, acc)         # account
    cpt_order.SetInputValue(2, acc_flac[0]) # security class - 0th of stocks
    cpt_order.SetInputValue(3, code)        # company code
    cpt_order.SetInputValue(4, amount)      # order amount

    if condition == None:
        cpt_order.SetInputValue(7, '0')     # order condition, 0: default 1: IOC 2:FOK
    elif condition == 'ioc' or 'IOC':
        cpt_order.SetInputValue(7, '1')
    elif condition == 'fok' or 'FOK':
        cpt_order.SetInputValue(7, '2')
    else:
        print('ERROR: Cannot understand the requested conditional order.')
    
    if type(price) == int:
        cpt_order.SetInputValue(8, '01')    # order price, 01: default (manually specified) 03: market order
        cpt_order.SetInputValue(5, price)   # manual order price
    elif price == 'market':
        cpt_order.SetInputValue(8, '03')
    else:
        print('ERROR: The input price is not a form of integer, or the requested order is not a market order.')

    rq = cpt_order.BlockRequest()

    stock_name = balance.get_balance(code)[0]
    print('order: ' + position + ' ' + str(amount) + ' shares of ' + stock_name + '(' + str(code) ') at ' + str(price) + ' (price). -> ', rq )

order('long','A035720',1,'market')