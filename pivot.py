import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import datetime
import pandas_datareader as pdr


gdata=pd.DataFrame()
# To Calculate RSI of the Stock 
def rsiFunc(prices, n=14):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed >= 0].sum()/n
    down = -seed[seed < 0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    return rsi
#stockData['Rsi']=rsiFunc(stockData['Close'])

def getStockData(stockName):
    stockData=pdr.get_data_yahoo(stockName, start=start_date, end=end_date)
    stockData['Percent Change'] = stockData['Adj Close'].pct_change()
    stockData['Amount Change'] = stockData['Adj Close']-stockData['Adj Close'].shift()
    stockData['Change'] = stockData['Adj Close'].pct_change()*100
    stockData['rsi']=rsiFunc(stockData['Close'])
    sma=stockData.rolling(window=20).mean()
    ema_short = stockData.ewm(span=20, adjust=False).mean()
    rsi=stockData['rsi'].tail(1)[0]
    sma=sma.tail(1)['Close'][0]
    ema=ema_short.tail(1)['Close'][0]
    low = min(stockData["Close"][-260:]) 
    high = max(stockData["High"][-260:])
    dhl=stockData.tail(1)
    pp=(dhl['High'][0]+dhl['Low'][0]+dhl['Close'][0])/3
    r1=2*pp-dhl['Low'][0]
    s1=2*pp-dhl['High'][0]
    r2=pp+(r1-s1)
    s2=pp-(r1-s1)
    r3=pp+2*(dhl['High'][0]-dhl['Low'][0])
    s3=pp-2*(dhl['High'][0]-dhl['Low'][0])
    pivot={'r3': r3, 'r2':r2, 'r1':r1,'pp':pp,'s1':s1,'s2':s2,'s3':s3}
    pivot1=pd.DataFrame([['r3', r3], ['r2',r2], ['r1',r1],['pp',pp],['s1',s1],['s2',s2],['s3',s3]])
    today=dhl
    if(today['Close'][0]< today['Open'][0]):
        x=today['High'][0]+today['Low'][0]+today['Close'][0]+today['Low'][0]
        High=x/2-today['Close'][0]
        Low=x/2-today['High'][0]
    elif(today['Close'][0]> today['Open'][0]):
        x=today['High'][0]+today['Low'][0]+today['Close'][0]+today['High'][0]
        High=x/2-today['Low'][0]
        Low=x/2-today['High'][0] 
    elif(today['Close'][0]==today['Open'][0]):
        x=today['High'][0]+today['Low'][0]+today['Close'][0]+today['Close'][0]
        High=x/2-today['Low'][0]
        Low=x/2-today['High'][0] 
    predict={'low': Low, 'high': High}
    Y=(today['High'][0]+today['Low'][0]+today['Close'][0])*0.67
    
    fraction_theory={"R1": Y-today['Low'][0], "S1": Y-today['High'][0], "Buy": Y-today['Close'][0]}
    #stock_return = stockData['Percent Change'].sum() * 100 
    return {'aname':stockName,'pivot':pivot, 'predict': predict,'fraction_theory':fraction_theory,'ma_ema': ema, 'ma_sma': sma, 'rsi': rsi,'l52':low,'h52':high, 'today':today,'rowdata':stockData }
    #return {'aname':stockName,'pivot':pivot, 'predict': predict, 'ema': ema, 'sma': sma, 'rsi': rsi,'l52':low,'h52':high, 'today':today,'xdata': stockData }
    

start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()
tmrw=datetime.datetime.today()+datetime.timedelta(days=1)


stockdf=pd.DataFrame({'labels': ['^NSEI','^NSEBANK','RELIANCE.NS','BAJFINANCE.NS','SUNPHARMA.NS','HCLTECH.NS','TCS.NS','INFY.NS','INDUSINDBK.NS','AXISBANK.NS','ICICIBANK.NS']})

st.sidebar.header("Stock Pivots")
option = st.sidebar.selectbox(
    'Select any Stock',
     stockdf['labels'])

#'You selected: ', option

data=getStockData(option)
st.title(data['aname'])

if(data['today']['Change'].values[0]>0):
    st.markdown("<h4 style='margin-top:-10px'>{:.2f}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<small style='color:green;'>+{:.2f}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(+{:.2f}%)</small></h4>".format(data['today']['Close'].values[0],data['today']['Amount Change'].values[0],data['today']['Change'].values[0]),unsafe_allow_html=True)
    st.balloons()   
else:
    st.markdown("<h4 style='margin-top:-15px'>{:.2f}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<small style='color:red;'>{:.2f}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;({:.2f}%)</small></h4>".format(data['today']['Close'].values[0],data['today']['Amount Change'].values[0],data['today']['Change'].values[0]),unsafe_allow_html=True)

st.text("")
st.sidebar.table(data['today'].iloc[0])
r3=data['pivot']['r3']
r2=data['pivot']['r2']
r1=data['pivot']['r1']
pp=data['pivot']['pp']
s1=data['pivot']['s1']
s2=data['pivot']['s2']
s3=data['pivot']['s3']

html="<table><tr style='background-color:#ff8a80;color:white'><th>R3</th><td>{:.2f}</td></tr><tr style='background-color:#ff1744;color:white'><th>R2</th><td>{:.2f}</td></tr><tr style='background-color:#d50000;color:white'><th>R1</th><td>{:.2f}</td></tr><tr style='background-color:#2962ff;color:white'><th>PP</th><td>{:.2f}</td></tr><tr style='background-color:#1b5e20;color:white'><th>S1</th><td>{:.2f}</td></tr><tr style='background-color:#388e3c;color:white'><th>S2</th><td>{:.2f}</td></tr><tr style='background-color:#4caf50;color:white'><th>S3</th><td>{:.2f}</td></tr></table>".format(r3,r2,r1,pp,s1,s2,s3)
st.markdown(html,unsafe_allow_html=True)

st.text("")
st.text("52W Low : {:.2f}".format(data['l52']))
st.text("52W High: {:.2f}".format(data['h52']))
st.text("EMA     : {:.2f}".format(data['ma_ema']))
st.text("SMA     : {:.2f}".format(data['ma_sma']))

st.line_chart(data['rowdata']['Close'], use_container_width=True)
