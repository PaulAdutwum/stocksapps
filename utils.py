import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3

def get_stock_data(symbol, period='1y', interval='1d'):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period, interval=interval)
        return df, stock.info
    except Exception as e:
        return None, None

def create_candlestick_chart(df, symbol, chart_type='candlestick'):
    if chart_type == 'candlestick':
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'])])
    elif chart_type == 'line':
        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], mode='lines')])
    elif chart_type == 'area':
        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], fill='tozeroy')])

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

def get_company_info(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            'Name': info.get('longName', ''),
            'Sector': info.get('sector', ''),
            'Industry': info.get('industry', ''),
            'Website': info.get('website', ''),
            'Description': info.get('longBusinessSummary', ''),
            'PE Ratio': info.get('trailingPE', 'N/A'),
            'Market Cap': info.get('marketCap', 0),
            '52 Week High': info.get('fiftyTwoWeekHigh', 0),
            '52 Week Low': info.get('fiftyTwoWeekLow', 0),
            'Volume': info.get('volume', 0),
            'Avg Volume': info.get('averageVolume', 0)
        }
    except:
        return None

def get_trending_stocks():
    trending = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM', 'V', 'WMT']
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
        } for article in news[:5]]
    except:
        return []

def calculate_technical_indicators(df):
    if df is None or len(df) == 0:
        return None

    # Basic indicators
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()

    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    df['BB_middle'] = df['Close'].rolling(window=20).mean()
    df['BB_upper'] = df['BB_middle'] + 2 * df['Close'].rolling(window=20).std()
    df['BB_lower'] = df['BB_middle'] - 2 * df['Close'].rolling(window=20).std()

    return df

def init_watchlist_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS watchlist
                 (email TEXT, symbol TEXT,
                  PRIMARY KEY (email, symbol))''')
    conn.commit()
    conn.close()

def add_to_watchlist(email, symbol):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO watchlist (email, symbol) VALUES (?, ?)',
                 (email, symbol))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def remove_from_watchlist(email, symbol):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('DELETE FROM watchlist WHERE email = ? AND symbol = ?',
             (email, symbol))
    conn.commit()
    conn.close()

def get_watchlist(email):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT symbol FROM watchlist WHERE email = ?', (email,))
    result = c.fetchall()
    conn.close()
    return [r[0] for r in result]