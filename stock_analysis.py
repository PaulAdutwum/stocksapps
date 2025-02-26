import streamlit as st
import plotly.express as px
from utils import get_stock_data, create_candlestick_chart, get_trending_stocks, get_stock_news, calculate_technical_indicators

def render_stock_analysis():
    st.markdown("""
        <h2 style='text-align: center; color: #1E88E5;'>Stock Analysis Dashboard</h2>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown("## Analysis Options")
    symbol = st.sidebar.text_input("Enter Stock Symbol", value="AAPL").upper()
    period = st.sidebar.selectbox(
        "Select Time Period",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        help="Choose the time period for historical data analysis"
    )

    # Main content
    tab1, tab2, tab3, tab4 = st.tabs([
        "Stock Analysis", 
        "Technical Indicators", 
        "News & Updates", 
        "Market Overview"
    ])

    with tab1:
        if symbol:
            df, info = get_stock_data(symbol, period)
            if df is not None and info is not None:
                # Stock Info Section
                st.markdown(f"### {info.get('shortName', symbol)} Analysis")
                st.markdown("""
                    This chart shows the stock's price movement over time using candlesticks:
                    - Green candlesticks indicate price increase
                    - Red candlesticks indicate price decrease
                    - The wicks show the high and low prices
                """)

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.plotly_chart(create_candlestick_chart(df, symbol),
                                  use_container_width=True)

                with col2:
                    st.metric(
                        label="Current Price",
                        value=f"${info.get('currentPrice', 0):.2f}",
                        delta=f"{info.get('regularMarketChangePercent', 0):.2f}%"
                    )

                    st.metric(
                        label="Market Cap",
                        value=f"${info.get('marketCap', 0)/1e9:.2f}B"
                    )

                    st.metric(
                        label="Volume",
                        value=f"{info.get('volume', 0):,}"
                    )

                    if info.get('dividendYield'):
                        st.metric(
                            label="Dividend Yield",
                            value=f"{info.get('dividendYield', 0)*100:.2f}%"
                        )

    with tab2:
        if symbol and df is not None:
            st.markdown("### Technical Indicators")
            st.markdown("""
                Technical indicators help analyze price trends and patterns:
                - Moving Average (MA): Shows the average price over 20 days
                - RSI: Measures overbought (>70) or oversold (<30) conditions
                - MACD: Shows momentum and potential trend changes
            """)

            df_technical = calculate_technical_indicators(df)
            if df_technical is not None:
                # MA Chart
                fig_ma = px.line(df_technical, x=df_technical.index, y=['Close', 'MA20'],
                               title='Price and 20-day Moving Average')
                fig_ma.update_layout(template='plotly_dark',
                                   plot_bgcolor='rgba(19,47,76,0.8)',
                                   paper_bgcolor='rgba(19,47,76,0.8)')
                st.plotly_chart(fig_ma, use_container_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    # RSI Chart
                    fig_rsi = px.line(df_technical, x=df_technical.index, y='RSI',
                                    title='Relative Strength Index (RSI)')
                    fig_rsi.update_layout(template='plotly_dark',
                                        plot_bgcolor='rgba(19,47,76,0.8)',
                                        paper_bgcolor='rgba(19,47,76,0.8)')
                    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                    st.plotly_chart(fig_rsi, use_container_width=True)

                with col2:
                    # MACD Chart
                    fig_macd = px.line(df_technical, x=df_technical.index, y=['MACD', 'Signal_Line'],
                                     title='MACD and Signal Line')
                    fig_macd.update_layout(template='plotly_dark',
                                         plot_bgcolor='rgba(19,47,76,0.8)',
                                         paper_bgcolor='rgba(19,47,76,0.8)')
                    st.plotly_chart(fig_macd, use_container_width=True)

    with tab3:
        if symbol:
            st.markdown("### Latest News")
            news_articles = get_stock_news(symbol)
            if news_articles:
                for article in news_articles:
                    with st.expander(article['title']):
                        st.markdown(f"""
                            **Published**: {article['published']}  
                            **Source**: {article['publisher']}  

                            {article['summary']}  

                            [Read more]({article['link']})
                        """)
            else:
                st.info("No recent news articles found for this stock.")

    with tab4:
        st.markdown("### Market Overview")
        st.markdown("""
            This section shows key market indices and trending stocks:
            - Major indices performance
            - Top trending stocks by market activity
            - Key market indicators
        """)

        # Display trending stocks
        st.subheader("Trending Stocks")
        trending_df = get_trending_stocks()

        for _, row in trending_df.iterrows():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"**{row['Name']} ({row['Symbol']})**")
            with col2:
                st.write(f"${row['Price']:.2f}")
            with col3:
                color = "green" if row['Change'] > 0 else "red"
                st.markdown(f"<span style='color: {color}'>{row['Change']:.2f}%</span>",
                          unsafe_allow_html=True)
            with col4:
                st.write(f"Vol: {row['Volume']:,.0f}")

        # Market Indices
        st.subheader("Major Indices")
        indices = ['^GSPC', '^DJI', '^IXIC']
        names = ['S&P 500', 'Dow Jones', 'NASDAQ']

        for idx, name in zip(indices, names):
            df, _ = get_stock_data(idx, '1mo')
            if df is not None:
                fig = px.line(df, y='Close', title=name)
                fig.update_layout(
                    template='plotly_dark',
                    plot_bgcolor='rgba(19,47,76,0.8)',
                    paper_bgcolor='rgba(19,47,76,0.8)'
                )
                st.plotly_chart(fig, use_container_width=True)