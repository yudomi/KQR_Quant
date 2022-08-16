###눌림목 전략 데이트레이딩 

## 상승추세에서 일시적으로 주가가 하락했다가, 재차 상승하는 추세 이용 

##매수
# 양봉 -> 음봉 전환 & 20분 이평선 터치 시 매수 

##매도
# 1) 1%상승 매도, 
# 2) 1% 하락 손절매, 
# 3)장 마감 10분전 매도


import csv
import pandas as pd
import datetime
import time

# 데이터 인덱스 datetime으로 바꿔주기
df = pd.read_csv('삼성전자 2년치 분봉.csv', index_col='Unnamed: 0')
converted_idx = pd.Series(df.index).apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
df.index = converted_idx

# 1520다음 분봉이 1530이므로 모든 날짜에 대해 1530분봉은 제거
df = df.loc[df.index.time!=datetime.time(15,30,00)]

# 20분 이평선 구하기
MA_period = 20
df['20분이평선'] = df['종가'].rolling(MA_period).mean()

#20분 이평선 NaN 결측 행 제거 
df=df.dropna()

# df 넣으면 날짜별로 split 해서 list 에 저장해주기. 
datelist=pd.Series(pd.date_range('2018-12-28', freq='1d', periods=743))
daylist={}

# 일별 분봉 딕셔너리 생성
for date in datelist:
    day=date.strftime('%Y-%m-%d')
    if len(df.loc[day]) !=0:
        daylist[day]=df.loc[day]
# print(daylist)

#  양봉만 T, 음봉이랑 도지봉 F
def plus_check(data):
    try:
        start=data['시가'].item()
        finish=data['종가'].item()

        if start<finish:
            # print('true')
            return True

        elif start>finish:

            return False
            
        elif start==finish:
            # print("시가와 종가 동일, doji")
            return False

    except:
        print(f'{data} plus_check error')
        return False

# data는 daylist의 value list 에서 한 개씩 들어갈 것. 
# 넣었을 때 전후 row 반환
def pre(data):
    data=daylist[i].iloc[k]

    try:    
        if k>0:
            pre_stick=daylist[i].iloc[k-1]
            return True, pre_stick

        else:
            # print('장 시작!')
            return False,None

    except:
        print('pre data error')
        return False,None

def post(data):
    data=daylist[i].iloc[k]
    try:
        post_stick=daylist[i].iloc[k+1]
        return True,post_stick
    
    except:
        # print('장 마감!')
        return False,None

def nullim(data):
    data=daylist[i].iloc[k]
    
    low=data['저가'].item()
    ma=data['20분이평선'].item()

    if pre(data)[0]:
        pre_stick=pre(data)[1]

        if plus_check(pre_stick) ==True & plus_check(data) ==False:
            # print('양봉-> 음봉 전환')
            if low<=ma:
                print('눌림목!')
                return True
            else:
                # print('양봉 -> 음봉 전환 있지만 눌림목 아님')
                return False

        else: 
            # print('양봉 -> 음봉 전환 없음')
            return False

    else:
        print('장 시작!')
        return False

    # else:
    #     print('nullim error')
    #     return False

# data는 data.iloc[i]
def buy(data):
    global delta_return
    global total_yld
    global k
    data=daylist[i].iloc[k]
    finish_price=daylist[i].iloc[-1]['시가']

    if post(data)[0]:
        post_stick=post(data)[1]
        
        if nullim(data):
            # time=date.index.strpfime(data, '%H:%M:%S')
            buy_price=post_stick['시가'].item()
            target_price=buy_price*1.01
            sold_price=buy_price*0.99
            
            sell_price=0

            while k<l:
                k+=1
                if k==l:
                    sell_price=finish_price 
                    print('장 마감 전 매도!')
                    break

                elif target_price<=daylist[i].iloc[k]['고가']:
                    sell_price=target_price
                    print('목표가 매도!')
                    break
                
                # 2년동안 수익이 좋지 않다...손절매 하지 말고 기다려보자. 
                elif daylist[i].iloc[k]['저가']<=sold_price:
                    sell_price=sold_price
                    print('손절매 !')
                    break

                else:
                    continue

            delta=sell_price-buy_price
            yld=sell_price/buy_price

            delta_return+=delta
            total_yld*=yld
            print(f'매수가: {buy_price}')
            print(f'매도가: {sell_price}')
            return True

    else:
        print('장 마감!')
        return False

    # else:
    #     print('buy error!')
    #     return False

if __name__=='__main__':
                
    day=list(daylist.keys())
    day_yld=[]
    delta_return=0
    total_yld=1
    for i in day:
        print(f'date={i}')
        l=len(daylist[i])
        for k in range(l):
            buy(daylist[i].iloc[k])

    print(f'2년 순실현 손익 :{delta_return}')
    print(f'2년 순이익률 :{total_yld}')

