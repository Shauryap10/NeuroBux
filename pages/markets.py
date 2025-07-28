import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime
import pandas as pd

def markets_page():
    st.header("📈 Markets")
    
    # Investment platform links
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
    
    # Show connection status
    with st.spinner("Loading market data..."):
        # Test connection first
        try:
            test_ticker = yf.Ticker("AAPL")
            test_data = test_ticker.history(period="1d", interval="1h")
            if test_data.empty:
                st.error("⚠️ Unable to connect to market data service")
                return
            else:
                st.success("✅ Connected to market data service")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")
            st.info("Please check your internet connection and try again")
            return

    universe = {
        "🇮🇳 India": ["RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "TATAMOTORS.NS", "^NSEI"],
        "🇺🇸 US": ["AAPL", "TSLA", "MSFT", "AMZN", "^GSPC"],
        "🇪🇺 EU": ["ASML.AS", "SAP.DE", "NESN.SW", "^STOXX50E"],
        "🇯🇵 JP": ["7203.T", "6758.T", "^N225"],
        "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
        "Commodities": ["GC=F", "SI=F", "CL=F"],
    }
    
    region = st.selectbox("Pick region / asset class", list(universe.keys()))
    symbols = universe[region]
    
    # Investment platforms section for selected region
    st.markdown("---")
    st.subheader(f"💰 Start Investing in {region}")
    
    # Get appropriate platforms
    platform_key = region
    if region == "🇪🇺 EU" or region == "🇯🇵 JP" or region == "Commodities":
        platform_key = "🇺🇸 US"  # Use US platforms for international markets
    
    platforms = INVESTMENT_PLATFORMS.get(platform_key, INVESTMENT_PLATFORMS["🇺🇸 US"])
    
    # Display investment platform buttons
    cols = st.columns(len(platforms))
    for idx, (platform_name, platform_url) in enumerate(platforms.items()):
        with cols[idx]:
            if st.button(f"📱 {platform_name}", key=f"invest_{platform_name}", use_container_width=True):
                st.success(f"🚀 Opening {platform_name}...")
                st.markdown(f'<a href="{platform_url}" target="_blank">🔗 Click here if not redirected automatically</a>', unsafe_allow_html=True)
                # JavaScript redirect
                st.components.v1.html(f"""
                <script>
                window.open('{platform_url}', '_blank');
                </script>
                """, height=0)
    
    st.caption("💡 Click any platform above to start investing. Links open in new tab.")
    
    # Create tabs
    symbol_names = []
    for s in symbols:
        name = s.replace(".NS", "").replace(".T", "").replace("^", "").replace("-USD", "").replace("=F", "")
        symbol_names.append(name)
    
    tabs = st.tabs(symbol_names)

    for tab, sym in zip(tabs, symbols):
        with tab:
            st.subheader(f"📊 {sym}")
            
            # Multiple fallback strategies
            periods_to_try = ["1d", "5d", "1mo"]
            intervals_map = {"1d": ["5m", "15m", "1h"], "5d": ["15m", "1h"], "1mo": ["1h", "1d"]}
            
            data_found = False
            error_messages = []
            
            for period in periods_to_try:
                if data_found:
                    break
                    
                intervals = intervals_map.get(period, ["1d"])
                
                for interval in intervals:
                    try:
                        with st.spinner(f"Fetching {sym} data ({period}, {interval})..."):
                            ticker = yf.Ticker(sym)
                            df = ticker.history(period=period, interval=interval)
                            
                            if not df.empty and len(df) >= 1:
                                # Success! Display the data
                                st.success(f"✅ Data loaded: {len(df)} data points")
                                
                                # Create chart
                                if len(df) > 1:
                                    # Candlestick chart for multiple data points
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
                                else:
                                    # Line chart for single data point
                                    fig = go.Figure()
                                    fig.add_trace(go.Scatter(
                                        x=df.index, 
                                        y=df["Close"],
                                        mode='lines+markers',
                                        name='Price'
                                    ))
                                    fig.update_layout(
                                        title=f"{sym} - Latest Price",
                                        template="plotly_dark",
                                        height=400
                                    )
                                
                                st.plotly_chart(fig, use_container_width=True)

                                # Display metrics
                                latest = df.iloc[-1]
                                earliest = df.iloc[0]
                                
                                # Calculate change
                                if len(df) > 1:
                                    change = (latest.Close - earliest.Open) / earliest.Open * 100
                                else:
                                    change = 0
                                
                                col1, col2, col3, col4 = st.columns(4)
                                
                                # Currency formatting
                                if ".NS" in sym:
                                    currency = "₹"
                                elif "USD" in sym or sym in ["BTC-USD", "ETH-USD", "SOL-USD"]:
                                    currency = "$"
                                elif sym in ["GC=F", "SI=F", "CL=F"]:
                                    currency = "$"
                                else:
                                    currency = "$"
                                
                                col1.metric("Current Price", f"{currency}{latest.Close:.2f}")
                                col2.metric("Change", f"{change:+.2f}%")
                                col3.metric("High", f"{currency}{latest.High:.2f}")
                                col4.metric("Low", f"{currency}{latest.Low:.2f}")
                                
                                # Additional info
                                if hasattr(latest, 'Volume') and latest.Volume > 0:
                                    st.info(f"📊 Volume: {latest.Volume:,.0f}")
                                
                                # Investment action buttons for individual stocks
                                st.markdown("---")
                                st.subheader(f"💳 Ready to Invest in {sym}?")
                                
                                # Show top 3 platforms for quick access
                                invest_cols = st.columns(3)
                                top_platforms = list(platforms.items())[:3]
                                
                                for idx, (platform_name, platform_url) in enumerate(top_platforms):
                                    with invest_cols[idx]:
                                        if st.button(f"🛒 Buy on {platform_name}", key=f"buy_{sym}_{platform_name}", type="primary"):
                                            st.balloons()  # Celebration animation
                                            st.success(f"🎯 Opening {platform_name} to invest in {sym}")
                                            st.markdown(f'<a href="{platform_url}" target="_blank">🔗 Click here to open {platform_name}</a>', unsafe_allow_html=True)
                                            # JavaScript redirect
                                            st.components.v1.html(f"""
                                            <script>
                                            window.open('{platform_url}', '_blank');
                                            </script>
                                            """, height=0)
                                
                                st.caption(f"📅 Data period: {period} | Interval: {interval} | Last updated: {latest.name.strftime('%Y-%m-%d %H:%M') if hasattr(latest.name, 'strftime') else 'N/A'}")
                                
                                data_found = True
                                break
                                
                    except Exception as e:
                        error_msg = f"{period}/{interval}: {str(e)}"
                        error_messages.append(error_msg)
                        continue
            
            # If no data found after all attempts
            if not data_found:
                st.error(f"❌ Unable to fetch data for {sym}")
                
                # Show specific help based on symbol type
                if ".NS" in sym:
                    st.warning("""
                    **Indian Stock (NSE) Issues:**
                    - Market hours: 9:15 AM - 3:30 PM IST (Monday-Friday)
                    - Weekends and holidays: No data available
                    - Try during market hours or use 5d/1mo period
                    """)
                elif "USD" in sym:
                    st.info("**Crypto markets are 24/7** - This might be a temporary API issue")
                else:
                    st.info("**Market might be closed** or experiencing temporary issues")
                
                # Show detailed errors in expander
                with st.expander("🔍 Debug Information"):
                    st.write("**Attempted data fetches:**")
                    for i, error in enumerate(error_messages, 1):
                        st.text(f"{i}. {error}")
                    
                    # Try to get basic info
                    try:
                        ticker = yf.Ticker(sym)
                        info = ticker.info
                        if info and 'longName' in info:
                            st.write(f"**Company:** {info['longName']}")
                        if info and 'regularMarketPrice' in info:
                            st.write(f"**Last Known Price:** ${info['regularMarketPrice']}")
                    except:
                        st.write("**Basic info:** Not available")

    # Manual search section with investment options
    st.markdown("---")
    st.subheader("🔍 Search & Invest")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_symbol = st.text_input(
            "Search any stock to invest",
            placeholder="e.g., RELIANCE.NS, AAPL, BTC-USD",
            help="Search any symbol and get investment options"
        )
    
    with col2:
        search_button = st.button("🔍 Search", type="primary")
    
    if search_symbol and (search_button or search_symbol):
        symbol = search_symbol.strip().upper()
        
        st.write(f"Searching for: **{symbol}**")
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Try multiple periods
            for period in ["1d", "5d", "1mo", "3mo"]:
                df = ticker.history(period=period)
                if not df.empty:
                    st.success(f"✅ Found data for {symbol}")
                    
                    # Simple line chart
                    st.line_chart(df["Close"])
                    
                    # Latest metrics
                    latest = df.iloc[-1]
                    previous = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
                    change = (latest.Close - previous.Close) / previous.Close * 100 if len(df) > 1 else 0
                    
                    col1, col2, col3 = st.columns(3)
                    currency = "₹" if ".NS" in symbol else "$"
                    col1.metric("Price", f"{currency}{latest.Close:.2f}")
                    col2.metric("Change", f"{change:+.2f}%")
                    col3.metric("Period", period.upper())
                    
                    # Investment options for searched symbol
                    st.markdown("---")
                    st.subheader(f"🚀 Invest in {symbol}")
                    
                    # Determine appropriate platforms based on symbol
                    if ".NS" in symbol:
                        relevant_platforms = INVESTMENT_PLATFORMS["🇮🇳 India"]
                    elif "USD" in symbol and any(crypto in symbol for crypto in ["BTC", "ETH", "SOL"]):
                        relevant_platforms = INVESTMENT_PLATFORMS["Crypto"]
                    else:
                        relevant_platforms = INVESTMENT_PLATFORMS["🇺🇸 US"]
                    
                    platform_cols = st.columns(len(relevant_platforms))
                    for idx, (name, url) in enumerate(relevant_platforms.items()):
                        with platform_cols[idx]:
                            if st.button(f"📈 {name}", key=f"search_invest_{name}_{symbol}"):
                                st.success(f"🎯 Opening {name} to invest in {symbol}")
                                st.markdown(f'<a href="{url}" target="_blank">🔗 Open {name}</a>', unsafe_allow_html=True)
                                # JavaScript redirect
                                st.components.v1.html(f"""
                                <script>
                                window.open('{url}', '_blank');
                                </script>
                                """, height=0)
                    
                    break
            else:
                st.error(f"❌ No data found for {symbol}")
                st.info("**Tips:**\n- Check symbol spelling\n- Add .NS for Indian stocks\n- Try -USD for cryptocurrencies")
                
        except Exception as e:
            st.error(f"Search failed: {str(e)}")

    # Investment disclaimer
    st.markdown("---")
    st.warning("""
    ⚠️ **Investment Disclaimer:** 
    - All investments carry risk and may lose value
    - Past performance doesn't guarantee future results  
    - Please research thoroughly before investing
    - Consider consulting a financial advisor
    - NeuroBux is not responsible for investment decisions
    """)

    # Footer with status
    st.caption("💡 If you're seeing 'No data' errors, try switching to US stocks or crypto which have more reliable data availability.")
