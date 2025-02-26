import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

def get_stock_data(symbol, period='1y'):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        return df, stock.info
    except Exception as e:
        return None, None

def create_candlestick_chart(df, symbol):
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])
    
    fig.update_layout(
        title=f'{symbol} Stock Price',
        yaxis_title='Price',
        template='plotly_dark',
        plot_bgcolor='rgba(19,47,76,0.8)',
        paper_bgcolor='rgba(19,47,76,0.8)',
        xaxis_rangeslider_visible=False
    )
    return fig

def get_trending_stocks():
    trending = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
    data = []
    for symbol in trending:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            data.append({
                'Symbol': symbol,
                'Name': info.get('shortName', ''),
                'Price': info.get('currentPrice', 0),
                'Change': info.get('regularMarketChangePercent', 0)
            })
        except:
            continue
    return pd.DataFrame(data)
