from pykrx import stock
import pandas as pd
import matplotlib.pyplot as plt
import datetime

begin_date = '2019-01-01' #어차피 분봉이 2년치밖에 없으니 2019년부터 돌림
end_date = '2020-12-31'
data_dir_name = begin_date+'_'+end_date
k = 0.5     #목표가 = 당일 시가 + (전일 종가 - 전일 시가) * k
initial_cash = 100000000
n = 10     #stock universe 구성시 상위 n개 종목


#당일 상장 종목 가져오기  (이전에는 코스피로만 돌렸는데 코스닥도 넣어서 해보자!)
today = datetime.datetime.now().strftime("%Y%m%d")
tickers = stock.get_market_ticker_list(today, market= 'ALL')

#상위 10종목 뽑을 criterion(거래대금/시가총액) 일별로 모아보기
crt = pd.DataFrame()
for ticker in tickers:
    csv_name = begin_date + '_' + end_date + '_' + stock.get_market_ticker_name(ticker) + '_' + ticker + '.csv'
    df = pd.read_csv('volatility strategy/' + data_dir_name + '/' + csv_name , index_col='date')[['trading_value','market_cap']]
    df[ticker] = df['trading_value']/df['market_cap']
    crt = pd.concat([crt, df[ticker]], axis=1)

#criterion기준으 상위 10개 종목으로 stock_universe 구성
universe={}
dates = crt.index.values.tolist()
for i, date in enumerate(dates):
    top10 =crt.iloc[i].dropna().sort_values(ascending=False)[:n].index.values.tolist()
    universe[date] = top10

#매일의 stock_universe에 대해 분별로 모으기
by_min = pd.DataFrame()
for date in dates:
    if not date.startswith('2018'):  #이거는 내가 받아온 일별 csv에 2018년부터 있어서 그거 거르려고 넣은 구문임!
        for i, ticker in enumerate(universe[date]):
            csv_name = begin_date + '_' + end_date + '_' + stock.get_market_ticker_name(ticker) + '_' + ticker + '.csv'
            tmp2 = pd.read_csv('volatility strategy/' + data_dir_name + '/' + csv_name , index_col='datetime')[['open', 'high', 'low']]   #목표가 계산을 위해 일별 데이터 가져옴
            a = tmp2.index.values.tolist().index(date)
            tmp = pd.read_csv('volatility strategy/1min_price/A' + ticker + '.csv')[['date', 'close']]
            tmp['goal_price'] = tmp2['open'].iloc[a] + (tmp2['high'].iloc[a-1] - tmp2['low'].iloc[a-1]) * k     #뒤에서 어차피 해당 date에 있는 열만 가져갈거라 그냥 상수처럼 열로 만들어버림
            tmp['ticker'] = ticker
            for date2 in tmp['date']:           #데이터 타입 설명: date = '2019-01-02'/ date2 = 201901020901(분봉csv에서 가져옴) /date3='20190102'
                date3 = date.replace('-', '')
                if str(date2).startswith(date3):            #즉, tmp(분봉데이터프레임)에 있는 20190102****인 열만 추가하기
                    by_min =by_min.append(tmp[tmp['date'] == date2])
                    print(date)

by_min = by_min.sort_values(by=['date'], ascending=True)    #이건 티커별로 정리되어있으므로 날짜별로 정렬
by_min.to_csv('volatility strategy\\stock_universe_by_min.csv', index=False)

#매수매도
#by_min1 = pd.read_csv('volatility strategy/stock_universe_by_min.csv')

portfolio = {'cash': initial_cash}
trade_log = pd.DataFrame(columns=['date', 'ticker', 'amount', 'price', 'buyorsell'])
portfolio_ret = pd.DataFrame(columns=['date','value'])
portfolio_ret.loc[0] = [begin_date, initial_cash]

for i, date in enumerate(by_min.date.values):
    if not str(date).endswith('1530'):   #매수
        price = by_min.close.values[i]
        ticker = by_min.ticker.values[i]
        if ticker not in portfolio.keys() and int(price) > by_min.goal_price.values[i]:  #해당 티커가 포트폴리오에 없는데 현재가가 목표가보다 높을때 매수
            date = str(date)[:4]+'-'+str(date)[4:6]+'-'+str(date)[6:8]
            amount = int((portfolio['cash'] / 10)/ price)

            #트레이딩 로그에 추가
            trade_log = trade_log.append(pd.Series([date, ticker, amount, price, 'buy'], index=trade_log.columns), ignore_index=True)

            #포트폴리오에 추가
            portfolio[ticker] = [amount, price]
            portfolio['cash'] = portfolio['cash'] - amount * price

    elif str(date).endswith('1530'):      #종가 일괄 매도
        ticker = by_min.ticker.values[i]
        if ticker in portfolio.keys():    #해당 티커가 포트폴리오에 있으면 매도
            date = str(date)[:4] + '-' + str(date)[4:6] + '-' + str(date)[6:8]
            amount = portfolio[ticker][0]
            price = by_min.close.values[i]

            #트레이딩 로그에 추가
            trade_log = trade_log.append(pd.Series([date, ticker, amount, price, 'sell'], index=trade_log.columns), ignore_index=True)

            #포트폴리오에서 제거
            portfolio['cash'] = portfolio['cash'] + amount * price
            del portfolio[ticker]

            #장마감에 포트폴리오 수익률 계산
            if len(portfolio.keys()) == 1:
                portfolio_ret = portfolio_ret.append(pd.Series([date, portfolio['cash']], index=portfolio_ret.columns), ignore_index=True)
                print(portfolio_ret)


portfolio_ret['daily_ret'] = portfolio_ret['value'].pct_change() * 100                  #일별수익률
portfolio_ret['cum_ret'] = portfolio_ret['value'] / portfolio_ret['value'].iloc[0] -1   #누적수익률

plt.plot(portfolio_ret['date'], portfolio_ret['value'])
plt.title('Porfolio Return')
plt.xlabel('Date')
plt.ylabel('Return')
plt.savefig('volatility strategy\\return_plot.png')
plt.show()

trade_log.to_csv('volatility strategy\\tradeing_log.csv', index=False)
portfolio_ret.to_csv('volatility strategy\\portfolio_value.csv', index=False
                     )