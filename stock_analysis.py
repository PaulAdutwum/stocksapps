import streamlit as st
import plotly.express as px
from utils import (
    get_stock_data, create_candlestick_chart, get_trending_stocks,
    get_stock_news, calculate_technical_indicators, get_company_info,
    init_watchlist_db, add_to_watchlist, remove_from_watchlist, get_watchlist
)
from datetime import datetime

def render_footer():
    st.markdown("""
        <div class="footer">
            <div class="footer-content">
                <div class="footer-section">
                    <h4>Market Data</h4>
                    <p>Powered by Yahoo Finance</p>
                </div>
                <div class="footer-section">
                    <h4>Real-time Updates</h4>
                    <p>Last updated: {}</p>
                </div>
                <div class="footer-section">
                    <h4>Support</h4>
                    <p>Contact: support@stockanalysis.com</p>
                </div>
            </div>
        </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)

def render_stock_card(stock, is_clickable=True):
    # Pre-define onclick attribute to avoid backslash issues
    onclick_attr = 'onclick="window.parent.location.href=\'#\'"' if is_clickable else ''

    card_html = f"""
        <div class="stock-card" {onclick_attr}>
            <h3>{stock['Name']} ({stock['Symbol']})</h3>
            <p style='font-size: 1.5rem; margin: 0;'>${stock['Price']:.2f}</p>
            <p style='color: {"green" if stock['Change'] > 0 else "red"};'>
                {stock['Change']:.2f}%
            </p>
            <p>Vol: {stock['Volume']:,.0f}</p>
        </div>
    """
    return st.markdown(card_html, unsafe_allow_html=True)

def render_stock_analysis():
    # Initialize watchlist
    init_watchlist_db()

    st.markdown("""
        <h2 style='text-align: center; color: #1E88E5;'>Stock Market Analysis Dashboard</h2>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown("## Analysis Options")

    # Search with autocomplete
    symbol = st.sidebar.text_input(
        "Enter Stock Symbol",
        value="AAPL",
        help="Enter a stock symbol (e.g., AAPL for Apple)"
    ).upper()

    # Chart settings
    chart_type = st.sidebar.selectbox(
        "Chart Type",
        ["candlestick", "line", "area"],
        help="Select the type of chart visualization"
    )

    timeframe = st.sidebar.selectbox(
        "Timeframe",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=4,
        help="Select the time period for analysis"
    )

    interval = "1d"
    if timeframe in ["1d", "5d"]:
        interval = st.sidebar.selectbox(
            "Interval",
            ["1m", "5m", "15m", "30m", "60m"],
            help="Select the time interval for intraday data"
        )

    # Watchlist section in sidebar
    st.sidebar.markdown("## My Watchlist")
    watchlist = get_watchlist(st.session_state.email)

    if watchlist:
        for watch_symbol in watchlist:
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                st.write(f"📈 {watch_symbol}")
            with col2:
                if st.button("❌", key=f"remove_{watch_symbol}"):
                    remove_from_watchlist(st.session_state.email, watch_symbol)
                    st.rerun()
    else:
        st.sidebar.info("Your watchlist is empty")

    # Store the selected stock in session state
    if 'selected_stock' not in st.session_state:
        st.session_state.selected_stock = None

    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Chart Analysis", 
        "Company Info",
        "Technical Indicators", 
        "News & Updates", 
        "Market Overview"
    ])

    with tab1:
        # Use either the clicked stock or the manually entered symbol
        current_symbol = st.session_state.selected_stock or symbol
        if current_symbol:
            df, info = get_stock_data(current_symbol, timeframe, interval)
            if df is not None and info is not None:
                # Add to watchlist button
                if current_symbol not in watchlist:
                    if st.button("➕ Add to Watchlist"):
                        add_to_watchlist(st.session_state.email, current_symbol)
                        st.success(f"Added {current_symbol} to watchlist!")
                        st.rerun()

                # Stock Info Section
                st.markdown(f"### {info.get('shortName', current_symbol)} Analysis")

                # Price metrics in a modern container
                st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(
                        "Current Price",
                        f"${info.get('currentPrice', 0):.2f}",
                        f"{info.get('regularMarketChangePercent', 0):.2f}%"
                    )
                with col2:
                    st.metric(
                        "Day High",
                        f"${info.get('dayHigh', 0):.2f}"
                    )
                with col3:
                    st.metric(
                        "Day Low",
                        f"${info.get('dayLow', 0):.2f}"
                    )
                with col4:
                    st.metric(
                        "Volume",
                        f"{info.get('volume', 0):,.0f}"
                    )
                st.markdown('</div>', unsafe_allow_html=True)

                # Chart
                st.plotly_chart(
                    create_candlestick_chart(df, current_symbol, chart_type),
                    use_container_width=True
                )

    with tab2:
        if symbol:
            company_info = get_company_info(symbol)
            if company_info:
                st.markdown(f"### About {company_info['Name']}")
                st.markdown(company_info['Description'])

                st.markdown("### Key Statistics")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Sector", company_info['Sector'])
                    st.metric("P/E Ratio", company_info['PE Ratio'])
                    st.metric("52 Week High", f"${company_info['52 Week High']:.2f}")

                with col2:
                    st.metric("Industry", company_info['Industry'])
                    st.metric("Market Cap", f"${company_info['Market Cap']/1e9:.2f}B")
                    st.metric("52 Week Low", f"${company_info['52 Week Low']:.2f}")

                with col3:
                    st.metric("Website", company_info['Website'])
                    st.metric("Volume", f"{company_info['Volume']:,.0f}")
                    st.metric("Avg Volume", f"{company_info['Avg Volume']:,.0f}")

    with tab3:
        if symbol and df is not None:
            st.markdown("### Technical Analysis")

            # Analysis explanation
            with st.expander("📊 Understanding Technical Indicators"):
                st.markdown("""
                    - **Moving Averages**: Help identify trends
                        - MA20: Short-term trend
                        - MA50: Medium-term trend
                        - MA200: Long-term trend

                    - **RSI (Relative Strength Index)**:
                        - Above 70: Potentially overbought
                        - Below 30: Potentially oversold

                    - **MACD (Moving Average Convergence Divergence)**:
                        - Signals potential trend changes
                        - When MACD crosses above Signal Line: Bullish
                        - When MACD crosses below Signal Line: Bearish

                    - **Bollinger Bands**:
                        - Help identify volatility and potential price levels
                        - Price near upper band: Potentially overbought
                        - Price near lower band: Potentially oversold
                """)

            df_technical = calculate_technical_indicators(df)
            if df_technical is not None:
                # Moving Averages
                fig_ma = px.line(df_technical, x=df_technical.index,
                                  y=['Close', 'MA20', 'MA50', 'MA200'],
                                  title='Price and Moving Averages')
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
                    fig_macd = px.line(df_technical, x=df_technical.index,
                                       y=['MACD', 'Signal_Line'],
                                       title='MACD and Signal Line')
                    fig_macd.update_layout(template='plotly_dark',
                                           plot_bgcolor='rgba(19,47,76,0.8)',
                                           paper_bgcolor='rgba(19,47,76,0.8)')
                    st.plotly_chart(fig_macd, use_container_width=True)

                # Bollinger Bands
                fig_bb = px.line(df_technical, x=df_technical.index,
                                  y=['Close', 'BB_upper', 'BB_middle', 'BB_lower'],
                                  title='Bollinger Bands')
                fig_bb.update_layout(template='plotly_dark',
                                      plot_bgcolor='rgba(19,47,76,0.8)',
                                      paper_bgcolor='rgba(19,47,76,0.8)')
                st.plotly_chart(fig_bb, use_container_width=True)

    with tab4:
        if symbol:
            st.markdown("### Latest News & Analysis")
            news_articles = get_stock_news(symbol)
            if news_articles:
                for article in news_articles:
                    with st.expander(f"📰 {article['title']}"):
                        st.markdown(f"""
                            **Published**: {article['published']}  
                            **Source**: {article['publisher']}  

                            {article['summary']}  

                            [Read full article]({article['link']})
                        """)
            else:
                st.info("No recent news articles found for this stock.")

    with tab5:
        st.markdown("### Market Overview")
        st.markdown("""
            <div class="metrics-container">
                This section provides a comprehensive view of market performance:
                - Click on any stock card to view detailed analysis
                - Track major market indices
                - Monitor top trending stocks
                - Analyze market movers
            </div>
        """, unsafe_allow_html=True)

        # Display trending stocks in a modern card layout
        st.subheader("🔥 Trending Stocks")
        trending_df = get_trending_stocks()

        for i in range(0, len(trending_df), 2):
            col1, col2 = st.columns(2)

            # First stock in the pair
            with col1:
                stock = trending_df.iloc[i]
                # Make the stock card clickable
                if st.button(f"View {stock['Symbol']}", key=f"view_{stock['Symbol']}"):
                    st.session_state.selected_stock = stock['Symbol']
                    st.rerun()
                render_stock_card(stock)

            # Second stock in the pair (if exists)
            if i + 1 < len(trending_df):
                with col2:
                    stock = trending_df.iloc[i + 1]
                    if st.button(f"View {stock['Symbol']}", key=f"view_{stock['Symbol']}_2"):
                        st.session_state.selected_stock = stock['Symbol']
                        st.rerun()
                    render_stock_card(stock)

        # Market Indices
        st.subheader("📈 Major Indices")
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

    # Render footer
    render_footer()