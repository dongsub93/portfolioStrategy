import win32com.client

cp_status = win32com.client.Dispatch('CpUtil.CpCybos')
cp_tradeUtil = win32com.client.Dispatch('CpTrade.CpTdUtil')
cp_stock = win32com.client.Dispatch('DsCbo1.StockMst')

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




def get_current_price(code):
    cp_stock.SetInputValue(0, code)
    cp_stock.Blockrequest()

    item = {}
    item['cur_price'] = cp_stock.GetHeaderValue(11)
    item['ask'] = cp_stock.GetHeaderValue(16)
    item['bid'] = cp_stock.GetHeaderValue(17)

    return item['cur_price'], item['ask'], item['bid']

print(get_current_price('A305080'))