import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime
import time

def markets_page():
    st.header("📈 Markets")
    
    # Connection test with retry logic
    def test_connection():
        max_retries = 3
        test_symbols = ["AAPL", "BTC-USD", "^GSPC"]  # Reliable symbols
        
        for attempt in range(max_retries):
            for symbol in test_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    test_data = ticker.history(period="1d", interval="1h")
                    if not test_data.empty:
                        return True, f"✅ Connected via {symbol}"
                    time.sleep(1)  # Add delay between requests
                except Exception as e:
                    continue
            
            if attempt < max_retries - 1:
                st.warning(f"Connection attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
        
        return False, "❌ Unable to connect to Yahoo Finance servers"
    
    # Test connection
    with st.spinner("Testing connection to market data service..."):
        connected, status_msg = test_connection()
        
        if connected:
            st.success(status_msg)
        else:
            st.error(status_msg)
            st.error("**Possible Solutions:**")
            st.info("""
            1. **Check Internet Connection** - Ensure you have stable internet
            2. **Yahoo Finance Server Issues** - Try again in a few minutes
            3. **Rate Limiting** - You may have made too many requests
            4. **Firewall/Proxy Issues** - Check if your network blocks Yahoo Finance
            5. **Library Issues** - The yfinance library may need updating
            """)
            
            # Show manual retry button
            if st.button("🔄 Retry Connection", type="primary"):
                st.experimental_rerun()
            
            return  # Exit early if connection fails

    universe = {
        "🇺🇸 US": ["AAPL", "TSLA", "MSFT", "AMZN", "^GSPC"],  # Start with most reliable
        "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
        "🇮🇳 India": ["RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "TATAMOTORS.NS", "^NSEI"],
        "🇪🇺 EU": ["ASML.AS", "SAP.DE", "NESN.SW", "^STOXX50E"],
        "🇯🇵 JP": ["7203.T", "6758.T", "^N225"],
        "Commodities": ["GC=F", "SI=F", "CL=F"],
    }
    
    region = st.selectbox("Pick region / asset class", list(universe.keys()))
    symbols = universe[region]
    
    # Create tabs
    symbol_names = []
    for s in symbols:
        name = s.replace(".NS", "").replace(".T", "").replace("^", "").replace("-USD", "").replace("=F", "")
        symbol_names.append(name)
    
    tabs = st.tabs(symbol_names)

    for tab, sym in zip(tabs, symbols):
        with tab:
            st.subheader(f"📊 {sym}")
            
            # Enhanced data fetching with retries
            def fetch_data_with_retry(symbol, max_retries=3):
                periods_to_try = ["1d", "5d", "1mo"]
                intervals_map = {"1d": ["1h"], "5d": ["1h"], "1mo": ["1d"]}
                
                for attempt in range(max_retries):
                    for period in periods_to_try:
                        intervals = intervals_map.get(period, ["1d"])
                        
                        for interval in intervals:
                            try:
                                ticker = yf.Ticker(symbol)
                                df = ticker.history(period=period, interval=interval)
                                
                                if not df.empty and len(df) >= 1:
                                    return df, period, interval, None
                                
                                time.sleep(0.5)  # Rate limiting
                                
                            except Exception as e:
                                error_msg = str(e)
                                continue
                    
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retry
                
                return None, None, None, "All fetch attempts failed"
            
            # Fetch data
            with st.spinner(f"Loading {sym} data..."):
                df, period, interval, error = fetch_data_with_retry(sym)
                
                if df is not None:
                    # Success! Display the data
                    st.success(f"✅ Loaded {len(df)} data points")
                    
                    # Create chart
                    if len(df) > 1:
                        fig = go.Figure(
                            data=[
                                go.Candlestick(
                                    x=df.index,
                                    open=df["Open"],
                                    high=df["High"],
                                    low=df["Low"],
                                    close=df["Close"],
                                    increasing_line_color="#26a69a",
                                    decreasing_line_color="#ef5350",
                                )
                            ]
                        )
                        fig.update_layout(
                            title=f"{sym} - {period.upper()} Chart",
                            template="plotly_dark",
                            height=400,
                            margin=dict(l=10, r=10, t=40, b=10),
                            xaxis_rangeslider_visible=False,
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # Display metrics
                        latest = df.iloc[-1]
                        earliest = df.iloc[0]
                        change = (latest.Close - earliest.Open) / earliest.Open * 100
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        currency = "₹" if ".NS" in sym else "$"
                        col1.metric("Current Price", f"{currency}{latest.Close:.2f}")
                        col2.metric("Change", f"{change:+.2f}%")
                        col3.metric("High", f"{currency}{latest.High:.2f}")
                        col4.metric("Low", f"{currency}{latest.Low:.2f}")
                        
                        st.caption(f"📅 Period: {period} | Interval: {interval}")
                    
                else:
                    # Failed to get data
                    st.error(f"❌ No data available for {sym}")
                    
                    if ".NS" in sym:
                        st.info("**NSE stocks** may have limited data availability outside market hours (9:15 AM - 3:30 PM IST)")
                    
                    st.caption("Try refreshing or selecting a different region")

    # Simple search section
    st.markdown("---")
    st.subheader("🔍 Quick Test")
    
    test_symbol = st.text_input("Test any symbol", value="AAPL", help="Try: AAPL, BTC-USD, MSFT")
    
    if st.button("Test Symbol", type="primary"):
        try:
            ticker = yf.Ticker(test_symbol)
            df = ticker.history(period="5d")
            
            if not df.empty:
                st.success(f"✅ {test_symbol} data available!")
                st.line_chart(df["Close"])
            else:
                st.error(f"❌ No data for {test_symbol}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
