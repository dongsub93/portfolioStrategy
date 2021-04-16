import win32com.client
import sendslackchat



cpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
cpTradeUtil = win32com.client.Dispatch('CpTrade.CpTdUtil')
cpBalance = win32com.client.Dispatch('CpTrade.CpTd6033')
cpCode = win32com.client.Dispatch('CpUtil.CpStockCode')

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

def getBalance(code):
    cpTradeUtil.TradeInit()
    acc = cpTradeUtil.AccountNumber[0]
    accFlag = cpTradeUtil.GoodsList(acc, 1)
    cpBalance.SetInputValue(0, acc)
    cpBalance.SetInputValue(1, accFlag[0])
    cpBalance.SetInputValue(2, 50)
    cpBalance.BlockRequest()

    if code == 'ALL':
        sendslackchat.sendSlackChat('계좌명: ' + str(cpBalance.GetHeaderValue(0)))
        sendslackchat.sendSlackChat('결제잔고수량: ' + str(cpBalance.GetHeaderValue(1)))
        sendslackchat.sendSlackChat('평가금액: ' + str(cpBalance.GetHeaderValue(3)))
        sendslackchat.sendSlackChat('평가손익: ' + str(cpBalance.GetHeaderValue(4)))
        sendslackchat.sendSlackChat('종목수: ' + str(cpBalance.GetHeaderValue(7)))

    stocks = []
    for i in range(cpBalance.GetHeaderValue(7)):
        stockCode = cpBalance.GetDataValue(12, i)
        stockName = cpBalance.GetDataValue(0, i)
        stockQty = cpBalance.GetDataValue(15, i)
        if code == 'ALL':
            sendslackchat.sendSlackChat(str(i+1)+' '+stockCode+' ('+stockName+')'+':'+str(stockQty))
            stocks.append({'code': stockCode, 'name': stockName, 'qty': stockQty})
        if stockCode == code:
            return stockName, stockQty

    if code == 'ALL':
        return stocks
    else:
        stockName = cpCode.CodeToName(code)
        return stockName, 0


print(getBalance('A305080'))