import ctypes
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

def get_ohlcvs(code, qty):
    """return daily open, high, low, close, volume (monetary unit), market capitalization of the stock (code) for the most recent qty unit period."""
    cp_ohlc.SetInputValue(0, code)                    # stock code
    cp_ohlc.SetInputValue(1, ord('2'))                # 1: given interval (unit: day), 2: most recent periods (unit: variable)
    cp_ohlc.SetInputValue(4, qty)                     # number of look-back unit period
    cp_ohlc.SetInputValue(5, [0, 2, 3, 4, 5, 9, 13])  # array data 0: date, 2-5:OHLC, 9: volume (unit of won), 13: market capitalization
    cp_ohlc.SetInputValue(6, ord('D'))                # dimension of unit period
    cp_ohlc.SetInputValue(9, ord('1'))                # 0: uncorrected price, 1: corrected price
    cp_ohlc.BlockRequest()

    count = cp_ohlc.GetHeaderValue(3)
    columns = ['open', 'high', 'low', 'close', 'volume', 'market cap']
    index = []
    rows = []
    for i in range(count):
        index.append(cp_ohlc.GetDataValue(0,i))
        rows.append([cp_ohlc.GetDataValue(1,i), cp_ohlc.GetDataValue(2,i), cp_ohlc.GetDataValue(3,i), cp_ohlc.GetDataValue(4,i), cp_ohlc.GetDataValue(5,i)//1000000, cp_ohlc.GetDataValue(6,i)//1000000])

    df = pd.DataFrame(rows, columns=columns, index=index)
    return df

print(get_ohlcvs('A035720',20))
