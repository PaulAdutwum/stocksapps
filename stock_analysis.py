import streamlit as st
import plotly.express as px
from utils import get_stock_data, create_candlestick_chart, get_trending_stocks

def render_stock_analysis():
    st.markdown("""
        <h2 style='text-align: center; color: #1E88E5;'>Stock Analysis Dashboard</h2>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown("## Analysis Options")
    symbol = st.sidebar.text_input("Enter Stock Symbol", value="AAPL").upper()
    period = st.sidebar.selectbox(
        "Select Time Period",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
    )
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["Stock Analysis", "Trending Stocks", "Market Overview"])
    
    with tab1:
        if symbol:
            df, info = get_stock_data(symbol, period)
            if df is not None:
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
            else:
                st.error("Error fetching stock data. Please check the symbol.")
    
    with tab2:
        st.markdown("### Trending Stocks")
        trending_df = get_trending_stocks()
        
        for _, row in trending_df.iterrows():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{row['Name']} ({row['Symbol']})**")
            with col2:
                st.write(f"${row['Price']:.2f}")
            with col3:
                color = "green" if row['Change'] > 0 else "red"
                st.markdown(f"<span style='color: {color}'>{row['Change']:.2f}%</span>",
                          unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### Market Overview")
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
