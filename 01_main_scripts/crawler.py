"""
    This code is for crowling the list of corporates in KOSPI.
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
from aux_functions import str_to_date

def crawler_version():
    return '0.0.1'

def get_market_list(marketName:str):
    """
        This fuction takes the market name as the argument, band
        downloads the name of corporates and their code in marekts.
        The downloaded result is saved under ./00_data in CSV format
    """
    try:
        _targetUrl = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=stockMkt'
        _rawDataDf = pd.read_html(_targetUrl,header=0,converters={'종목코드':str})[0]
        _marketDf  = _rawDataDf.loc[:,['회사명','종목코드']]
        _marketDf.to_csv('./00_data/0_marketList/kospi.csv', encoding='UTF-8-SIG')
        return True
    except:
        print ('get_market_list:Fail to creat the dataFrame from the url : {url}'.format(url=_targetUrl))
        return False

def get_price(corpCode:str\
            , start:datetime.date=datetime.date.today()-datetime.timedelta(days=365)\
            , end:datetime.date=datetime.date.today()):
    """
        This function downloads the price data of the stock having the 'corpCode' from NAVER.
        It requires total 3 arguments, (1) code of the stock, (2) the fisrt date and (3) and the last date.
        The first and the last date indicate two edges of time interval in which we want to know its price. 
    """
    # Insert below header if one cannot access to the URL page.
    _headers={'User-Agent':\
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}
    _naverURL = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=str(corpCode))

    # Access to the front page of URL having price information. It would gives the total number of pages of price informations.
    try:
        _queResult= requests.get(_naverURL,headers=_headers)
    except Exception:
        print ('get_price:Request to the URL failed. (URL = {url})'.format(url=_naverURL))
        return 0
    _htmlResult = BeautifulSoup(_queResult.text,'lxml')
    # Try to find the number of page.
    try:
        _pageMax = _htmlResult.find('table', class_='Nnavi') \
                    .find('td',class_='pgRR') \
                    .a.get('href').rsplit('&')[1] \
                    .rsplit('=')[1]#
    except Exception:
        print ('get_price:HTML code from the URL has no related contents.')
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
            print ('get_price:Cannot load page {page} from URL {url}'.format(page=_page,url=_naverURL))
            return 0
        # Reject the data outside the time interval [date.start,date.end]
        _Imin,_Imax = 0,_tempDf.shape[0]
        while str_to_date(_tempDf.iloc[_Imin]['날짜'])>end and _Imin < _Imax-1:
            _Imin += 1
        while str_to_date(_tempDf.iloc[_Imax-1]['날짜'])<start and _Imax > _Imin+1:
            _Imax -= 1

        _start = str_to_date(_tempDf.iloc[_Imax-1]['날짜'])
        _end   = str_to_date(_tempDf.iloc[_Imin]['날짜'])
        if not _priceDf.empty:
            _prev_page_start = str_to_date(_priceDf.iloc[len(_priceDf)-1]['날짜'])
        else:
            _prev_page_start = _end
        if (_prev_page_start - _end).days > 10:
            
            print (' prev. page : ',str_to_date(_priceDf.iloc[len(_priceDf)-1]['날짜']) , ' , ', ' current page : ', str_to_date(_tempDf.iloc[_Imin]['날짜']))
            print (' diff       : ',str_to_date(_priceDf.iloc[len(_priceDf)-1]['날짜']) - str_to_date(_tempDf.iloc[_Imin]['날짜']))
            
            print ('get_price: From {c}, detected huge separation between adjacent price data between {a} and {b}.'\
                .format(c=corpCode, a= _end,b=_prev_page_start))
            print ('           It will drop the data earlier than {b}.'.format(b=_prev_page_start))
            break
        if (_end - _start).days > 3*(_Imax-_Imin):
            
            print ('Imin, Imax : ', _Imin, ' , ', _Imax)
            print ('shape : ', _tempDf.shape)
            print ('minD, maxD : ',str_to_date(_tempDf.iloc[_Imin]['날짜']), ' , ',str_to_date(_tempDf.iloc[_Imax-1]['날짜']))
            print ('diff date : ',str_to_date(_tempDf.iloc[_Imin]['날짜'])-str_to_date(_tempDf.iloc[_Imax-1]['날짜']))
            print ('diff days : ',datetime.timedelta(days=3*(_Imax-_Imin)))
            print ('before : Imax = ',_Imax)
            
            while str_to_date(_tempDf.iloc[_Imin]['날짜'])-str_to_date(_tempDf.iloc[_Imax-1]['날짜'])\
                     >= datetime.timedelta(days=7+(_Imax-_Imin))\
                and _Imin < _Imax:
                _Imax-= 1
            #print ('after  : Imax = ',_Imax)
            print ('get_price: From {c}, detected huge separation between adjacent price data between {a} and {b}.'\
                .format(c=corpCode, a= _tempDf.iloc[_Imax]['날짜'],b=_tempDf.iloc[_Imax-1]['날짜']))
            print ('           It will drop the data earlier than {b}.'.format(b=_tempDf.iloc[_Imax-1]['날짜']))
        _priceDf = pd.concat([_priceDf,_tempDf.iloc[_Imin:_Imax]],ignore_index=True)
        # If we found the ealiest date then breaks the iteration.
        if _Imax < _tempDf.shape[0]:
            break
        
    adjust_factor = 1.0
    for i in range(len(_priceDf)-1):
        if _priceDf.iloc[i]['시가'] < _priceDf.iloc[i+1]['종가']*0.7\
            and _priceDf.iloc[i]['시가']*_priceDf.iloc[i+1]['종가'] != 0.0:
            """
            print ('{a} 종가 : {ap}(거래량 : {an}), {b} 시가 : {bp}(거래량 : {bn})'.\
                format(a=_priceDf.iloc[i+1]['날짜'], ap=_priceDf.iloc[i+1]['종가']\
                    ,b=_priceDf.iloc[i]['날짜'], bp=_priceDf.iloc[i]['시가']\
                    ,an=_priceDf.iloc[i+1]['거래량'], bn=_priceDf.iloc[i]['거래량']\
                ))
            """
            adjust_factor = int(round(_priceDf.iloc[i+1]['종가']/_priceDf.iloc[i]['시가']))
            if adjust_factor == 1:
                continue
            print ('get_price: From {c}, detected {n}-to-1 split between {a} and {b}'\
                    .format(c=corpCode, n=adjust_factor, a=_priceDf.iloc[i+1]['날짜'],b=_priceDf.iloc[i]['날짜']))
            # 0 : 날짜, 1 : 종가, 2 : 전일비, 3 : 시가, 4 : 고가, 5 : 저가, 6 : 거래량
            _priceDf.iloc[i+1:,[1,2,3,4,5]] = _priceDf.iloc[i+1:,[1,2,3,4,5]]/float(adjust_factor)
            _priceDf.iloc[i+1:,6] = _priceDf.iloc[i+1:,6]*float(adjust_factor)
        else:
            continue
            
    # It returns the information in 'pandas.DataFrame' format.
    return _priceDf

def get_finance(corpCode:str):
    """
        This function returns pandas.DataFrame of financial information of the company having [corpCode] code in the market.
    """
    # Insert below header if one cannot access to the URL page.
    _headers={'User-Agent':\
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}
    _naverURL = 'http://finance.naver.com/item/main.nhn?code={code}'.format(code=str(corpCode))
    # Access to the front page of URL having price information. It would gives the total number of pages of price informations.
    try:
        _queResult= requests.get(_naverURL,headers=_headers)
    except Exception:
        print ('get_finance:Request to the URL failed. (URL = {url})'.format(url=_naverURL))
        return 0
    _htmlResult = BeautifulSoup(_queResult.content,'html.parser')
    # Try to find the number of page.
    try:
        _contents = _htmlResult.select('div.section.cop_analysis div.sub_section')[0]
        _theads = np.array([ x.get_text().strip() for x in _contents.select('thead th')])
        _indexes= np.array([ x.get_text().strip() for x in _contents.select('th.h_th2')][3:])
        _finData= np.array([ x.get_text().strip() for x in _contents.select('td')])
    except Exception:
        print ('get_finance:Cannot parse URL to the HTML.')
        return 0
    _dateLabels = _theads[3:int((len(_theads)-3)/2)+3]
    for i in range(len(_dateLabels)):
        _dateLabels[i] = _dateLabels[i]+'(' +_theads[int((len(_theads)-3)/2)+3+i]+ ')'
    _finData.resize(len(_indexes),len(_dateLabels))

    return pd.DataFrame(data = _finData,columns=_dateLabels,index=_indexes)
