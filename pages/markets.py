import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import time
import random
from datetime import datetime

def markets_page():
    st.header("📈 Markets")
    
    # Investment platform links (unchanged)
    INVESTMENT_PLATFORMS = {
        "🇮🇳 India": {
            "Zerodha": "https://zerodha.com/",
            "Groww": "https://groww.in/",
            "Angel One": "https://www.angelone.in/",
            "Upstox": "https://upstox.com/",
            "INDmoney": "https://www.indmoney.com/"
        },
        "🇺🇸 US": {
            "Robinhood": "https://www.robinhood.com/",
            "Public": "https://public.com/",
            "M1 Finance": "https://www.m1.com/",
            "Fidelity": "https://www.fidelity.com/",
            "Charles Schwab": "https://www.schwab.com/"
        },
        "Crypto": {
            "Coinbase": "https://www.coinbase.com/",
            "Binance": "https://www.binance.com/",
            "WazirX": "https://wazirx.com/",
            "CoinDCX": "https://coindcx.com/",
            "Kraken": "https://www.kraken.com/"
        }
    }
    
    # Enhanced connection test with better rate limiting
    def test_connection_with_backoff():
        # Check if we recently failed due to rate limiting
        if 'last_rate_limit' in st.session_state:
            time_since_limit = time.time() - st.session_state.last_rate_limit
            if time_since_limit < 300:  # Wait 5 minutes after rate limit
                remaining_time = 300 - int(time_since_limit)
                st.warning(f"⏳ Rate limited. Please wait {remaining_time} seconds before retrying.")
                return False, f"Rate limited. Try again in {remaining_time} seconds."
        
        test_symbols = ["AAPL"]  # Use only one reliable symbol for testing
        
        try:
            with st.spinner("Testing connection (with rate limiting)..."):
                # Add random delay to avoid hitting rate limits
                time.sleep(random.uniform(1, 3))
                
                ticker = yf.Ticker(test_symbols[0])
                test_data = ticker.history(period="1d", interval="1h")
                
                if not test_data.empty:
                    # Clear any previous rate limit flags on success
                    if 'last_rate_limit' in st.session_state:
                        del st.session_state.last_rate_limit
                    return True, f"✅ Connected successfully"
                else:
                    return False, "❌ No data received from server"
                    
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "too many requests" in error_msg:
                st.session_state.last_rate_limit = time.time()
                return False, "❌ Rate limited by Yahoo Finance. Please wait a few minutes."
            else:
                return False, f"❌ Connection failed: {str(e)}"
    
    # Test connection with improved handling
    with st.spinner("Checking market data availability..."):
        connected, status_msg = test_connection_with_backoff()
        
        if connected:
            st.success(status_msg)
        else:
            st.error(status_msg)
            
            # Show rate limit specific help
            if "rate limit" in status_msg.lower():
                st.error("**Yahoo Finance Rate Limit Reached**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.warning("""
                    **🕐 What happened:**
                    - Too many requests to Yahoo Finance
                    - Server temporarily blocked your IP
                    - This is a common protective measure
                    """)
                
                with col2:
                    st.info("""
                    **⏳ What to do:**
                    - Wait 5-10 minutes before trying again
                    - Avoid refreshing the page repeatedly  
                    - Use investment platforms below in the meantime
                    """)
                
                # Countdown timer for rate limit
                if 'last_rate_limit' in st.session_state:
                    time_since_limit = time.time() - st.session_state.last_rate_limit
                    remaining = max(0, 300 - int(time_since_limit))
                    if remaining > 0:
                        st.info(f"⏱️ Estimated wait time: {remaining} seconds")
                        
                        # Auto-refresh countdown
                        if st.button("🔄 Check Again", disabled=remaining > 30):
                            st.rerun()
            
            # Show investment platforms even when rate limited
            st.markdown("---")
            st.subheader("💰 Investment Platforms (Always Available)")
            
            region = st.selectbox("Choose investment region", list(INVESTMENT_PLATFORMS.keys()))
            platforms = INVESTMENT_PLATFORMS[region]
            
            cols = st.columns(len(platforms))
            for idx, (platform_name, platform_url) in enumerate(platforms.items()):
                with cols[idx]:
                    if st.button(f"📱 {platform_name}", key=f"invest_offline_{platform_name}"):
                        st.success(f"🚀 Opening {platform_name}...")
                        st.markdown(f'<a href="{platform_url}" target="_blank">🔗 Open {platform_name}</a>', unsafe_allow_html=True)
            
            return  # Exit early if connection fails

    # Rest of your markets code with enhanced rate limiting
    universe = {
        "🇺🇸 US": ["AAPL", "TSLA", "MSFT", "AMZN", "^GSPC"],
        "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
        "🇮🇳 India": ["RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "TATAMOTORS.NS", "^NSEI"],
        "🇪🇺 EU": ["ASML.AS", "SAP.DE", "NESN.SW", "^STOXX50E"],
        "🇯🇵 JP": ["7203.T", "6758.T", "^N225"],
        "Commodities": ["GC=F", "SI=F", "CL=F"],
    }
    
    region = st.selectbox("Pick region / asset class", list(universe.keys()))
    symbols = universe[region]
    
    # Investment platforms section
    st.markdown("---")
    st.subheader(f"💰 Start Investing in {region}")
    
    platform_key = region
    if region in ["🇪🇺 EU", "🇯🇵 JP", "Commodities"]:
        platform_key = "🇺🇸 US"
    
    platforms = INVESTMENT_PLATFORMS.get(platform_key, INVESTMENT_PLATFORMS["🇺🇸 US"])
    
    cols = st.columns(len(platforms))
    for idx, (platform_name, platform_url) in enumerate(platforms.items()):
        with cols[idx]:
            if st.button(f"📱 {platform_name}", key=f"invest_{platform_name}"):
                st.success(f"🚀 Opening {platform_name}...")
                st.markdown(f'<a href="{platform_url}" target="_blank">🔗 Open {platform_name}</a>', unsafe_allow_html=True)
    
    # Create tabs with rate-limited data fetching
    symbol_names = [s.replace(".NS", "").replace(".T", "").replace("^", "").replace("-USD", "").replace("=F", "") for s in symbols]
    tabs = st.tabs(symbol_names)

    for tab, sym in zip(tabs, symbols):
        with tab:
            st.subheader(f"📊 {sym}")
            
            # Enhanced data fetching with longer delays
            def fetch_data_with_rate_limiting(symbol):
                periods_to_try = ["5d", "1mo"]  # Reduced attempts
                intervals_map = {"5d": ["1d"], "1mo": ["1d"]}  # Simpler intervals
                
                for period in periods_to_try:
                    intervals = intervals_map.get(period, ["1d"])
                    
                    for interval in intervals:
                        try:
                            # Add significant delay between requests
                            time.sleep(random.uniform(2, 5))
                            
                            with st.spinner(f"Loading {symbol} data (please wait)..."):
                                ticker = yf.Ticker(symbol)
                                df = ticker.history(period=period, interval=interval)
                                
                                if not df.empty and len(df) >= 1:
                                    return df, period, interval, None
                                
                        except Exception as e:
                            if "rate limit" in str(e).lower():
                                return None, None, None, "Rate limited"
                            continue
                
                return None, None, None, "No data available"
            
            # Fetch data with rate limiting
            df, period, interval, error = fetch_data_with_rate_limiting(sym)
            
            if df is not None:
                # Success! Display the data
                st.success(f"✅ Loaded {len(df)} data points")
                
                # Create simplified chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df["Close"],
                    mode='lines',
                    name='Price',
                    line=dict(color='#26a69a', width=2)
                ))
                
                fig.update_layout(
                    title=f"{sym} - {period.upper()} Price Chart",
                    template="plotly_dark",
                    height=400,
                    xaxis_title="Date",
                    yaxis_title="Price"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Display metrics
                latest = df.iloc[-1]
                earliest = df.iloc[0]
                change = (latest.Close - earliest.Close) / earliest.Close * 100
                
                col1, col2, col3, col4 = st.columns(4)
                currency = "₹" if ".NS" in sym else "$"
                col1.metric("Current Price", f"{currency}{latest.Close:.2f}")
                col2.metric("Change", f"{change:+.2f}%")
                col3.metric("High", f"{currency}{latest.High:.2f}")
                col4.metric("Low", f"{currency}{latest.Low:.2f}")
                
                # Investment buttons
                st.markdown("---")
                st.subheader(f"💳 Invest in {sym}")
                
                invest_cols = st.columns(3)
                top_platforms = list(platforms.items())[:3]
                
                for idx, (platform_name, platform_url) in enumerate(top_platforms):
                    with invest_cols[idx]:
                        if st.button(f"🛒 Buy on {platform_name}", key=f"buy_{sym}_{platform_name}"):
                            st.balloons()
                            st.success(f"🎯 Opening {platform_name} for {sym}")
                            st.markdown(f'<a href="{platform_url}" target="_blank">🔗 Open {platform_name}</a>', unsafe_allow_html=True)
            
            elif error == "Rate limited":
                st.error(f"❌ Rate limited while fetching {sym} data")
                st.info("⏳ Yahoo Finance is protecting against too many requests. Try again in a few minutes.")
            else:
                st.warning(f"⚠️ No data available for {sym}")
                st.info("This might be due to market closure or temporary server issues.")
