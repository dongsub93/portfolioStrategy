"""
    This code is for crowling the list of coorporates in KOSPI.
    It downloads the data from KIND.
    One can get the information of KOSDAQ, by replacing the 'marketType' key from the url.
"""

import sys, os
import pandas as pd
import numpy as np
import urllib, requests
import time, datetime
from pandas import Series, DataFrame
from bs4 import BeautifulSoup


def downloadMarketList(marketName:str):
    """
        This fuction takes the market name as the argument, band
        downloads the name of coorporates and their code in marekts.
        The downloaded result is saved under ./00_data in CSV format
    """
    try:
        _targetUrl = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=stockMkt'
        _rawDataDf = pd.read_html(_targetUrl,header=0,converters={'종목코드':str})[0]
        _marketDf  = _rawDataDf.loc[:,['회사명','종목코드']]
        _marketDf.to_csv('./00_data/00_0_marketList/kospi.csv', encoding='UTF-8-SIG')
        return True
    except:
        print ('downloadMarketList:Fail to creat the dataFrame from the url : {url}'.format(url=_targetUrl))
        return False

def getMarketDict(marketName:str):
    _marketList = pd.read_csv('./00_data/00_0_marketList/{market}.csv'.format(market=marketName)\
                                ,dtype=str,index_col=0)
    return dict(zip(_marketList.values[:,0],_marketList.values[:,1]))
    
def strToDate(dateStr:str):
    """
        It returns the the date in 'datetime.date' class from the argument which is the date string in
        'yyyy.mm.dd'
    """
    _ymdList = dateStr.rsplit('.')
    return datetime.date(int(_ymdList[0]),int(_ymdList[1]),int(_ymdList[2]))
  
def getPrice(coorpCode:str\
            , start:datetime.date=datetime.date.today()-datetime.timedelta(days=365)\
            , end:datetime.date=datetime.date.today()):
    """
        This function downloads the price data of the stock having the 'coorpCode' from NAVER.
        It requires total 3 arguments, (1) code of the stock, (2) the fisrt date and (3) and the last date.
        The first and the last date indicate two edges of time interval in which we want to know its price. 
    """
    # Insert below header if one cannot access to the URL page.
    _headers={'User-Agent':\
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}
    _naverURL = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=str(coorpCode))

    # Access to the front page of URL having price information. It would gives the total number of pages of price informations.
    try:
        _queResult= requests.get(_naverURL,headers=_headers)
    except Exception:
        print ('getPrice:Request to the URL failed. (URL = {url})'.format(url=_naverURL))
        return 0
    _htmlResult = BeautifulSoup(_queResult.text,'lxml')
    # Try to find the number of page.
    try:
        _pageMax = _htmlResult.find('table', class_='Nnavi') \
                    .find('td',class_='pgRR') \
                    .a.get('href').rsplit('&')[1] \
                    .rsplit('=')[1]#
    except Exception:
        print ('getPrice:HTML code from the URL has no related contents.')
        return 0

    _priceDf = pd.DataFrame()
    # Iterate over pages and to collect all information lying on the [date.start,date.end] interval.
    for _page in range(1,int(_pageMax)+1):
        _pageURL = _naverURL+'&page={page}'.format(page=_page)
        # Try to access to the '_page'-th page of the URL.
        try:
            _queResult = requests.get(_pageURL,headers=_headers)
            _tempDf = pd.read_html(str(BeautifulSoup(_queResult.text,'lxml').find('table')),header=0)[0].dropna()
        except Exception:
            print ('getPrice:Cannot load page {page} from URL {url}'.format(page=_page,url=_naverURL))
            return 0
        # Reject the data outside the time interval [date.start,date.end]
        _Imin,_Imax = 0,_tempDf.shape[0]
        while strToDate(_tempDf.iloc[_Imin]['날짜'])>end and _Imin < _Imax-1:
            _Imin += 1
        while strToDate(_tempDf.iloc[_Imax-1]['날짜'])<start and _Imax > _Imin+1:
            _Imax -= 1

        _priceDf = pd.concat([_priceDf,_tempDf.iloc[_Imin:_Imax]],ignore_index=True)
        # If we found the ealiest date then breaks the iteration.
        if _Imax < _tempDf.shape[0]:
            break
    # It returns the information in 'pandas.DataFrame' format.
    return _priceDf

def getFiance(coorpCode:str):
    """
        This function returns pandas.DataFrame of financial information of the company having [cooprCode] code in the market.
    """
    # Insert below header if one cannot access to the URL page.
    _headers={'User-Agent':\
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}
    _naverURL = 'http://finance.naver.com/item/main.nhn?code={code}'.format(code=str(coorpCode))
    # Access to the front page of URL having price information. It would gives the total number of pages of price informations.
    try:
        _queResult= requests.get(_naverURL,headers=_headers)
    except Exception:
        print ('getFinance:Request to the URL failed. (URL = {url})'.format(url=_naverURL))
        return 0
    _htmlResult = BeautifulSoup(_queResult.content,'html.parser')
    #return _htmlResult
    # Try to find the number of page.
    try:
        _contents = _htmlResult.select('div.section.cop_analysis div.sub_section')[0]
        _theads = np.array([ x.get_text().strip() for x in _contents.select('thead th')])
        _indexes= np.array([ x.get_text().strip() for x in _contents.select('th.h_th2')][3:])
        _finData= np.array([ x.get_text().strip() for x in _contents.select('td')])
    except Exception:
        print ('getFinance:Cannot parse URL to the HTML.')
        return 0
    _dateLabels = _theads[3:int((len(_theads)-3)/2)+3]
    for i in range(len(_dateLabels)):
        _dateLabels[i] = _dateLabels[i]+'(' +_theads[int((len(_theads)-3)/2)+3+i]+ ')'
    _finData.resize(len(_indexes),len(_dateLabels))

    return pd.DataFrame(data = _finData,columns=_dateLabels,index=_indexes)