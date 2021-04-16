import win32com.client
import slack_chat



cp_status = win32com.client.Dispatch('CpUtil.CpCybos')
cp_trade_util = win32com.client.Dispatch('CpTrade.CpTdUtil')
cp_balance = win32com.client.Dispatch('CpTrade.CpTd6033')
cp_code = win32com.client.Dispatch('CpUtil.CpStockCode')

def check_creon_system():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print('check_creon_system(): admin user -> FAILED')
        return False
    
    if (cp_status.IsConnect == 0):
        print('check_creon_system(): connect to server -> FAILED')
        return False

    if (cp_trade_util.TradeInit(0) != 0):
        print('check_creon_system(): init trade -> FAILED')
        return False
    
    return True

def get_balance(code):
    cp_trade_util.TradeInit()
    acc = cp_trade_util.AccountNumber[0]
    acc_flag = cp_trade_util.GoodsList(acc, 1)
    cp_balance.SetInputValue(0, acc)
    cp_balance.SetInputValue(1, acc_flag[0])
    cp_balance.SetInputValue(2, 50)
    cp_balance.BlockRequest()

    if code == 'ALL':
        slack_chat.send_slack_chat('계좌명: ' + str(cp_balance.GetHeaderValue(0)))
        slack_chat.send_slack_chat('결제잔고수량: ' + str(cp_balance.GetHeaderValue(1)))
        slack_chat.send_slack_chat('평가금액: ' + str(cp_balance.GetHeaderValue(3)))
        slack_chat.send_slack_chat('평가손익: ' + str(cp_balance.GetHeaderValue(4)))
        slack_chat.send_slack_chat('종목수: ' + str(cp_balance.GetHeaderValue(7)))

    stocks = []
    for i in range(cp_balance.GetHeaderValue(7)):
        stock_code = cp_balance.GetDataValue(12, i)
        stock_name = cp_balance.GetDataValue(0, i)
        stock_qty = cp_balance.GetDataValue(15, i)
        if code == 'ALL':
            slack_chat.send_slack_chat(str(i+1)+' '+stock_code+' ('+stock_name+')'+':'+str(stock_qty))
            stocks.append({'code': stock_code, 'name': stock_name, 'qty': stock_qty})
        if stock_code == code:
            return stock_name, stock_qty

    if code == 'ALL':
        return stocks
    else:
        stock_name = cp_code.CodeToName(code)
        return stock_name, 0


print(get_balance('ALL'))