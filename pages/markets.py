import streamlit as st
import plotly.graph_objects as go
import requests
import pandas as pd
import time
from datetime import datetime

def markets_page():
    st.header("📈 Markets")
    
    # Investment platform links WITHOUT logos - simple URL structure
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
    
    # Alpha Vantage API functions - SECURE VERSION
    def get_stock_data_alpha_vantage(symbol):
        """Get stock data using Alpha Vantage API"""
        api_key = st.secrets.get("alpha_vantage_api_key")
        
        if not api_key:
            return None, "API key not configured"
        
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": api_key,
                "outputsize": "compact"
            }
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if "Time Series (Daily)" in data:
                time_series = data["Time Series (Daily)"]
                df = pd.DataFrame.from_dict(time_series, orient='index')
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                df.index = pd.to_datetime(df.index)
                df = df.astype(float)
                df = df.sort_index()
                return df.tail(30), None  # Last 30 days
            elif "Error Message" in data:
                return None, data["Error Message"]
            elif "Note" in data:
                return None, "API rate limit reached. Please wait a minute."
            else:
                return None, "Unknown error occurred"
                
        except Exception as e:
            return None, str(e)
    
    def get_crypto_data_alpha_vantage(symbol):
        """Get crypto data using Alpha Vantage"""
        api_key = st.secrets.get("alpha_vantage_api_key")
        
        if not api_key:
            return None, "API key not configured"
        
        try:
            # Convert BTC-USD to BTC format
            crypto_symbol = symbol.replace("-USD", "")
            
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "DIGITAL_CURRENCY_DAILY",
                "symbol": crypto_symbol,
                "market": "USD",
                "apikey": api_key
            }
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if "Time Series (Digital Currency Daily)" in data:
                time_series = data["Time Series (Digital Currency Daily)"]
                df = pd.DataFrame.from_dict(time_series, orient='index')
                
                # Use USD prices
                df['Close'] = df['4a. close (USD)'].astype(float)
                df['Open'] = df['1a. open (USD)'].astype(float)
                df['High'] = df['2a. high (USD)'].astype(float)
                df['Low'] = df['3a. low (USD)'].astype(float)
                df['Volume'] = df['5. volume'].astype(float)
                
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                return df[['Open', 'High', 'Low', 'Close', 'Volume']].tail(30), None
            elif "Error Message" in data:
                return None, data["Error Message"]
            else:
                return None, "Crypto data not available"
                
        except Exception as e:
            return None, str(e)
    
    # Test Alpha Vantage connection - SECURE VERSION
    def test_alpha_vantage_connection():
        """Test Alpha Vantage API connection"""
        try:
            with st.spinner("Testing Alpha Vantage connection..."):
                df, error = get_stock_data_alpha_vantage("AAPL")
                
                if df is not None:
                    return True, "✅ Alpha Vantage connected successfully"
                else:
                    return False, f"❌ Alpha Vantage error: {error}"
                    
        except Exception as e:
            return False, f"❌ Connection failed: {str(e)}"
    
    # Test connection
    with st.spinner("Connecting to Alpha Vantage..."):
        connected, status_msg = test_alpha_vantage_connection()
        
        if connected:
            st.success(status_msg)
            st.info("🚀 **No Rate Limiting!** Powered by Alpha Vantage API")
        else:
            st.error(status_msg)
            
            if "API key not configured" in status_msg:
                st.error("**Alpha Vantage API Key Missing**")
                st.info("Please add your Alpha Vantage API key to Streamlit secrets and redeploy.")
                st.code('alpha_vantage_api_key = "YOUR_API_KEY_HERE"')
            
            # Show investment platforms even when data fails
            st.markdown("---")
            st.subheader("💰 Investment Platforms (Always Available)")
            
            region = st.selectbox("Choose investment region", list(INVESTMENT_PLATFORMS.keys()))
            platforms = INVESTMENT_PLATFORMS[region]
            
            cols = st.columns(len(platforms))
            for idx, (platform_name, platform_url) in enumerate(platforms.items()):
                with cols[idx]:
                    if st.button(f"📱 {platform_name}", key=f"offline_{platform_name}"):
                        st.success(f"🚀 Opening {platform_name}...")
                        st.markdown(f'<a href="{platform_url}" target="_blank">🔗 Open {platform_name}</a>', unsafe_allow_html=True)
            return

    # Markets universe - Alpha Vantage compatible symbols
    universe = {
        "🇺🇸 US": ["AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "NVDA", "META"],
        "Crypto": ["BTC-USD", "ETH-USD", "ADA-USD", "DOT-USD"],
        "🇪🇺 EU": ["SAP", "ASML", "NESN"],  # Limited international support
        "Popular ETFs": ["SPY", "QQQ", "VTI", "VOO", "IWM"]
    }
    
    region = st.selectbox("Pick region / asset class", list(universe.keys()))
    symbols = universe[region]
    
    # Investment platforms section WITHOUT logos
    st.markdown("---")
    st.subheader(f"💰 Start Investing in {region}")
    
    platform_key = region
    if region in ["🇪🇺 EU", "Popular ETFs"]:
        platform_key = "🇺🇸 US"
    elif "Crypto" in region:
        platform_key = "Crypto"
    else:
        platform_key = region
    
    platforms = INVESTMENT_PLATFORMS.get(platform_key, INVESTMENT_PLATFORMS["🇺🇸 US"])
    
    cols = st.columns(len(platforms))
    for idx, (platform_name, platform_url) in enumerate(platforms.items()):
        with cols[idx]:
            if st.button(f"📱 {platform_name}", key=f"invest_{platform_name}"):
                st.success(f"🚀 Opening {platform_name}...")
                st.markdown(f'<a href="{platform_url}" target="_blank">🔗 Open {platform_name}</a>', unsafe_allow_html=True)
    
    # Create tabs for symbols
    symbol_names = [s.replace("-USD", "").replace("^", "") for s in symbols]
    tabs = st.tabs(symbol_names)

    for tab, sym in zip(tabs, symbols):
        with tab:
            st.subheader(f"📊 {sym}")
            
            # Fetch data with Alpha Vantage
            with st.spinner(f"Loading {sym} data from Alpha Vantage..."):
                if "-USD" in sym:  # Crypto
                    df, error = get_crypto_data_alpha_vantage(sym)
                else:  # Stocks
                    df, error = get_stock_data_alpha_vantage(sym)
                
                # Respect API rate limits
                time.sleep(1)
            
            if df is not None and not df.empty:
                st.success(f"✅ Loaded {len(df)} days of Alpha Vantage data")
                
                # Create enhanced chart
                fig = go.Figure()
                
                # Add candlestick chart
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name=sym,
                    increasing_line_color='#26a69a',
                    decreasing_line_color='#ef5350'
                ))
                
                fig.update_layout(
                    title=f"{sym} - 30-Day Chart (Alpha Vantage)",
                    template="plotly_dark",
                    height=450,
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    xaxis_rangeslider_visible=False
                )
                st.plotly_chart(fig, use_container_width=True)

                # Display comprehensive metrics
                latest = df.iloc[-1]
                previous = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
                change = (latest.Close - previous.Close) / previous.Close * 100
                
                col1, col2, col3, col4 = st.columns(4)
                currency = "$"
                col1.metric("Current Price", f"{currency}{latest.Close:.2f}")
                col2.metric("Daily Change", f"{change:+.2f}%")
                col3.metric("Day High", f"{currency}{latest.High:.2f}")
                col4.metric("Day Low", f"{currency}{latest.Low:.2f}")
                
                # Investment buttons WITHOUT logos
                st.markdown("---")
                st.subheader(f"💳 Ready to Invest in {sym}?")
                
                invest_cols = st.columns(3)
                top_platforms = list(platforms.items())[:3]
                
                for idx, (platform_name, platform_url) in enumerate(top_platforms):
                    with invest_cols[idx]:
                        if st.button(f"🛒 Buy {sym}", key=f"buy_{sym}_{platform_name}", type="primary"):
                            st.balloons()
                            st.success(f"🎯 Opening {platform_name} to invest in {sym}")
                            st.info(f"💡 Current price: ${latest.Close:.2f}")
                            st.markdown(f'<a href="{platform_url}" target="_blank">🔗 Open {platform_name}</a>', unsafe_allow_html=True)
            
            else:
                st.error(f"❌ Unable to load data for {sym}")
                if error:
                    st.error(f"Error: {error}")
                    
                    if "rate limit" in error.lower():
                        st.warning("⏳ Alpha Vantage rate limit reached (5 calls per minute). Please wait a moment.")
                    elif "invalid api call" in error.lower():
                        st.info(f"💡 Symbol {sym} may not be available on Alpha Vantage.")

    # Footer - SECURE VERSION
    st.markdown("---")
    st.success("🚀 **Powered by Alpha Vantage** - No more Yahoo Finance rate limiting!")
    st.caption("💡 Professional financial data with 500 free API calls per day")
