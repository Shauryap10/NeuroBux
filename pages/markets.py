import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import time
import random
from datetime import datetime

def markets_page():
    st.header("📈 Markets")
    
    # Investment platform links WITH LOGOS
    INVESTMENT_PLATFORMS = {
        "🇮🇳 India": {
            "Zerodha": {
                "url": "https://zerodha.com/",
                "logo": "https://zerodha.com/static/images/logo.svg",
                "fallback": "⚡"
            },
            "Groww": {
                "url": "https://groww.in/",
                "logo": "https://assets.groww.in/web-assets/favicon/favicon-192.png",
                "fallback": "🌱"
            },
            "Angel One": {
                "url": "https://www.angelone.in/",
                "logo": "https://www.angelone.in/images/logo.png",
                "fallback": "👼"
            },
            "Upstox": {
                "url": "https://upstox.com/",
                "logo": "https://upstox.com/app/themes/upstox/dist/img/logo.svg",
                "fallback": "📈"
            },
            "INDmoney": {
                "url": "https://www.indmoney.com/",
                "logo": "https://www.indmoney.com/favicon.ico",
                "fallback": "💰"
            }
        },
        "🇺🇸 US": {
            "Robinhood": {
                "url": "https://www.robinhood.com/",
                "logo": "https://robinhood.com/us/en/_next/static/images/3x_RH_favicon-39dc52836d0d5fd6bdcc5a0a29d7b42e.png",
                "fallback": "🏹"
            },
            "Public": {
                "url": "https://public.com/",
                "logo": "https://public.com/favicon.ico",
                "fallback": "🏛️"
            },
            "M1 Finance": {
                "url": "https://www.m1.com/",
                "logo": "https://www.m1.com/favicon.ico",
                "fallback": "Ⓜ️"
            },
            "Fidelity": {
                "url": "https://www.fidelity.com/",
                "logo": "https://www.fidelity.com/favicon.ico",
                "fallback": "🏦"
            },
            "Charles Schwab": {
                "url": "https://www.schwab.com/",
                "logo": "https://www.schwab.com/favicon.ico",
                "fallback": "🏛️"
            }
        },
        "Crypto": {
            "Coinbase": {
                "url": "https://www.coinbase.com/",
                "logo": "https://www.coinbase.com/favicon.ico",
                "fallback": "🪙"
            },
            "Binance": {
                "url": "https://www.binance.com/",
                "logo": "https://bin.bnbstatic.com/static/images/common/favicon.ico",
                "fallback": "🔶"
            },
            "WazirX": {
                "url": "https://wazirx.com/",
                "logo": "https://wazirx.com/favicon.ico",
                "fallback": "🇮🇳"
            },
            "CoinDCX": {
                "url": "https://coindcx.com/",
                "logo": "https://coindcx.com/favicon.ico",
                "fallback": "💎"
            },
            "Kraken": {
                "url": "https://www.kraken.com/",
                "logo": "https://www.kraken.com/favicon.ico",
                "fallback": "🐙"
            }
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
    
    # Function to display platform with logo
    def display_platform_button(platform_name, platform_data, key_suffix=""):
        """Display platform button with logo and fallback"""
        col1, col2 = st.columns([1, 4])
        
        with col1:
            try:
                st.image(platform_data["logo"], width=40)
            except:
                st.markdown(f"### {platform_data['fallback']}")
        
        with col2:
            if st.button(f"{platform_name}", key=f"platform_{platform_name}_{key_suffix}", use_container_width=True):
                st.success(f"🚀 Opening {platform_name}...")
                st.markdown(f'<a href="{platform_data["url"]}" target="_blank">🔗 Open {platform_name}</a>', unsafe_allow_html=True)
                st.balloons()
                return True
        return False
    
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
            for idx, (platform_name, platform_data) in enumerate(platforms.items()):
                with cols[idx]:
                    display_platform_button(platform_name, platform_data, "offline")
            
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
    
    # Investment platforms section with logos
    st.markdown("---")
    st.subheader(f"💰 Start Investing in {region}")
    
    platform_key = region
    if region in ["🇪🇺 EU", "🇯🇵 JP", "Commodities"]:
        platform_key = "🇺🇸 US"
    
    platforms = INVESTMENT_PLATFORMS.get(platform_key, INVESTMENT_PLATFORMS["🇺🇸 US"])
    
    # Enhanced platform display with logos
    cols = st.columns(len(platforms))
    for idx, (platform_name, platform_data) in enumerate(platforms.items()):
        with cols[idx]:
            # Platform card with logo
            with st.container():
                # Logo and name section
                st.markdown(f"""
                <div style='text-align: center; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 10px; margin: 5px 0;'>
                """, unsafe_allow_html=True)
                
                try:
                    st.image(platform_data["logo"], width=50)
                except:
                    st.markdown(f"## {platform_data['fallback']}")
                
                st.markdown(f"**{platform_name}**")
                
                if st.button(f"Open {platform_name}", key=f"invest_{platform_name}_main", use_container_width=True, type="primary"):
                    st.success(f"🚀 Opening {platform_name}...")
                    st.markdown(f'<a href="{platform_data["url"]}" target="_blank">🔗 Open {platform_name}</a>', unsafe_allow_html=True)
                    st.balloons()
                
                st.markdown("</div>", unsafe_allow_html=True)
    
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
                
                # Investment buttons with logos
                st.markdown("---")
                st.subheader(f"💳 Ready to Invest in {sym}?")
                
                invest_cols = st.columns(3)
                top_platforms = list(platforms.items())[:3]
                
                for idx, (platform_name, platform_data) in enumerate(top_platforms):
                    with invest_cols[idx]:
                        # Small logo above button
                        try:
                            st.image(platform_data["logo"], width=30)
                        except:
                            st.markdown(f"### {platform_data['fallback']}")
                        
                        st.markdown(f"**{platform_name}**")
                        
                        if st.button(f"Buy on {platform_name}", key=f"buy_{sym}_{platform_name}", type="primary", use_container_width=True):
                            st.balloons()
                            st.success(f"🎯 Opening {platform_name} to invest in {sym}")
                            st.markdown(f'<a href="{platform_data["url"]}" target="_blank">🔗 Open {platform_name}</a>', unsafe_allow_html=True)
            
            elif error == "Rate limited":
                st.error(f"❌ Rate limited while fetching {sym} data")
                st.info("⏳ Yahoo Finance is protecting against too many requests. Try again in a few minutes.")
            else:
                st.warning(f"⚠️ No data available for {sym}")
                st.info("This might be due to market closure or temporary server issues.")
