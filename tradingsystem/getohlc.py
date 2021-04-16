import win32com.client
import pandas as pd

cpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
cpTradeUtil = win32com.client.Dispatch('CpTrade.CpTdUtil')
cpOhlc = win32com.client.Dispatch('CpSysDib.StockChart')


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

def getOhlc(code, qty):
    cpOhlc.SetInputValue(0, code)
    cpOhlc.SetInputValue(1, ord('2'))
    cpOhlc.SetInputValue(4, qty)
    cpOhlc.SetInputValue(5, [0, 2, 3, 4, 5])
    cpOhlc.SetInputValue(6, ord('D'))
    cpOhlc.SetInputValue(9, ord('1'))
    cpOhlc.BlockRequest()

    count = cpOhlc.GetHeaderValue(3)
    columns = ['open', 'high', 'low', 'close']
    index = []
    rows = []
    for i in range(count):
        index.append(cpOhlc.GetDataValue(0,i))
        rows.append([cpOhlc.GetDataValue(1,i), cpOhlc.GetDataValue(2,i), cpOhlc.GetDataValue(3,i), cpOhlc.GetDataValue(4,i)])

    df = pd.DataFrame(rows, columns=columns, index=index)
    return df

print(getOhlc('A035720', 10))