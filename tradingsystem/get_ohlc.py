import win32com.client
import pandas as pd

cp_status = win32com.client.Dispatch('CpUtil.CpCybos')
cp_trade_util = win32com.client.Dispatch('CpTrade.CpTdUtil')
cp_ohlc = win32com.client.Dispatch('CpSysDib.StockChart')


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

def get_ohlc(code, qty):
    cp_ohlc.SetInputValue(0, code)
    cp_ohlc.SetInputValue(1, ord('2'))
    cp_ohlc.SetInputValue(4, qty)
    cp_ohlc.SetInputValue(5, [0, 2, 3, 4, 5])
    cp_ohlc.SetInputValue(6, ord('D'))
    cp_ohlc.SetInputValue(9, ord('1'))
    cp_ohlc.BlockRequest()

    count = cp_ohlc.GetHeaderValue(3)
    columns = ['open', 'high', 'low', 'close']
    index = []
    rows = []
    for i in range(count):
        index.append(cp_ohlc.GetDataValue(0,i))
        rows.append([cp_ohlc.GetDataValue(1,i), cp_ohlc.GetDataValue(2,i), cp_ohlc.GetDataValue(3,i), cp_ohlc.GetDataValue(4,i)])

    df = pd.DataFrame(rows, columns=columns, index=index)
    return df

print(get_ohlc('A035720', 10))