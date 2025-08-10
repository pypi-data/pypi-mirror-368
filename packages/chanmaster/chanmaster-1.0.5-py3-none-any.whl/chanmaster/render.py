import sys

from chart import *
import kService

import akshare as ak

import datetime


def getSymbolWithName(symbol):
    f=open('./list',encoding='utf8')
    myList=eval(f.read())
    f.close()

    companyName=myList.get(symbol[2:])
    if companyName==None:
        company=ak.stock_individual_info_em(symbol=symbol[2:])
        companyName=company.query('item=="股票简称"').iloc[0].get('value')

        myList[symbol[2:]]=companyName
        f=open('./list','w',encoding='utf8')
        f.write(str(myList))
        f.close()

    return symbol+'_'+companyName

def render_embed(kSet,freq=Freq.D,isEnding=False):
    k=K(symbol=kSet[0][0], freq=freq)

    for item in kSet[:]:
        k.addRawBar(item[1],item[2],item[3],item[4],item[5],item[6],item[7])

    kService.updateK(k)

    chart=draw(k)
    
    return chart.render_embed()

def getData(symbol,freq,isIndex,isAdjust):
    adjust='qfq' if isAdjust else ''
    if isIndex:
        symbolWithName=symbol+'_index'
    else:
        symbolWithName=getSymbolWithName(symbol)

    kSet=[]
    if freq=='d':
        now=datetime.datetime.now()
        startDate=(now+datetime.timedelta(days=-4000)).strftime('%Y%m%d')
        endDate=now.strftime('%Y%m%d')
        
        if isIndex:
            df=ak.stock_zh_index_daily_em(symbol=symbol,start_date=startDate,end_date=endDate)    
            for index, row in df.iterrows():
                data=(symbolWithName,row['date'],float(row['open']),float(row['close']),float(row['high']),float(row['low']),float(row['volume']),float(row['amount']))
                kSet.append(data)
        else:        
            df=ak.stock_zh_a_hist(symbol=symbol[2:],period='daily',adjust=adjust,start_date=startDate,end_date=endDate)    
            for index, row in df.iterrows():
                data=(symbolWithName,row['日期'],float(row['开盘']),float(row['收盘']),float(row['最高']),float(row['最低']),float(row['成交量']),float(row['成交额']))
                kSet.append(data)
    else:
        df=ak.stock_zh_a_minute(symbol=symbol,period=str(freq),adjust=adjust)    
        for index, row in df.iterrows():
            data=(symbolWithName,row['day'],float(row['open']),float(row['close']),float(row['high']),float(row['low']),float(row['volume']),'')
            kSet.append(data)

    return kSet


if __name__ == "__main__":
    symbol=sys.argv[1]
    freq=sys.argv[2]
    output=sys.argv[3]
    
    kSet=getData(symbol,freq,False,False)
    result=render_embed(kSet,freq)

    f=open(output,'w')
    f.write(result)
    f.close()
