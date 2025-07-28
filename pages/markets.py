import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime
import pandas as pd

def markets_page():
    st.header("📈 Markets")
    
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

    # Manual search section
    st.markdown("---")
    st.subheader("🔍 Manual Symbol Search")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_symbol = st.text_input(
            "Enter any stock symbol",
            placeholder="e.g., RELIANCE.NS, AAPL, BTC-USD",
            help="Use .NS for Indian stocks (RELIANCE.NS), -USD for crypto (BTC-USD)"
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
                    
                    break
            else:
                st.error(f"❌ No data found for {symbol}")
                st.info("**Tips:**\n- Check symbol spelling\n- Add .NS for Indian stocks\n- Try -USD for cryptocurrencies")
                
        except Exception as e:
            st.error(f"Search failed: {str(e)}")

    # Footer with status
    st.markdown("---")
    st.caption("💡 If you're seeing 'No data' errors, try switching to US stocks or crypto which have more reliable data availability.")
