"""
필요 데이터
20년치 전종목 일별 OHLCV --> 일단 연습이니까 100개종목 5년치만 받아오도록 하겠다!
"""
from pykrx import stock
import pandas as pd
import os

tickers = stock.get_market_ticker_list('20201230', market= 'KOSPI')

begin_date = '2019-01-01'
end_date = '2020-12-31'
data_dir_name = begin_date+'_'+end_date

if data_dir_name not in os.listdir():
    os.mkdir(data_dir_name)


,#종목별로 일별 ohlcv + 거래대금 + 시가총액 DataFrame csv로 저장하기
for i, ticker in enumerate(tickers):
    csv_name = begin_date + '_' + end_date + '_' + stock.get_market_ticker_name(ticker) + '_' + ticker
    df = stock.get_market_ohlcv_by_date(begin_date.replace('-',''), end_date.replace('-',''), ticker)
    df.index.name = 'datetime'
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df2 = stock.get_market_cap_by_date(begin_date.replace('-',''), end_date.replace('-',''), ticker)
    df['trading_value'] = df2['거래대금']
    df['market_cap'] = df2['시가총액']
    df.to_csv(data_dir_name + '\\' + csv_name +'.csv')
    if (i+1)%10==0:
        print(f'{i+1}th data download complete (total: {len(tickers)})')
print('download complete')