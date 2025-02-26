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
        xaxis_rangeslider_visible=False,
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif"
        )
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
                'Change': info.get('regularMarketChangePercent', 0),
                'Volume': info.get('volume', 0),
                'Market Cap': info.get('marketCap', 0)
            })
        except:
            continue
    return pd.DataFrame(data)

def get_stock_news(symbol):
    try:
        stock = yf.Ticker(symbol)
        news = stock.news
        return [{
            'title': article.get('title', ''),
            'publisher': article.get('publisher', ''),
            'link': article.get('link', ''),
            'published': datetime.fromtimestamp(article.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M'),
            'summary': article.get('summary', '')
        } for article in news[:5]]  # Get latest 5 news articles
    except:
        return []

def calculate_technical_indicators(df):
    if df is None or len(df) == 0:
        return None

    # Calculate 20-day moving average
    df['MA20'] = df['Close'].rolling(window=20).mean()

    # Calculate RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Calculate MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

    return df