import win32com.client

cpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
cpTradeUtil = win32com.client.Dispatch('CpTrade.CpTdUtil')
cpStock = win32com.client.Dispatch('DsCbo1.StockMst')

def checkCreonSystem():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print('checkCreonSystem(): admin user -> FAILED')
        return False
    
    if (cpStatus.IsConnect == 0):
        print('checkCreonSystem(): connect to server -> FAILED')
        return False

    if (cpTradeUtil.TradeInit(0) != 0):
        print('checkCreonSystem(): init trade -> FAILED')
        return False
    
    return True




def getCurrentPrice(code):
    cpStock.SetInputValue(0, code)
    cpStock.Blockrequest()

    item = {}
    item['curprice'] = cpStock.GetHeaderValue(11)
    item['ask'] = cpStock.GetHeaderValue(16)
    item['bid'] = cpStock.GetHeaderValue(17)

    return item['curprice'], item['ask'], item['bid']

print(getCurrentPrice('A305080'))