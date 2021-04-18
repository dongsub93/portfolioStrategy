from datetime import datetime 
import ohlc, slack_chat

def get_moving_average(code, window):
    """return window-day moving average of the stock price"""
    try: 
        time_now = datetime.now()
        str_today = time_now.strftime('%Y%m%d')
        ohlc = ohlc.get_ohlc(code, 40)
        if str_today == str(ohlc.iloc[0].name):
            last_day = ohlc.iloc[1].name
        else:
            last_day = ohlc.iloc[0].name
        closes = ohlc['close'].sort_index()
        ma = closes.rolling(window=window).mean()
        return ma.loc[last_day]

    except Exception as e:
        slack_chat.send_slack_chat('get_moving_average() -> exception! ' + str(e) + "'")
        return None
