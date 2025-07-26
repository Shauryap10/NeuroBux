import streamlit as st
import plotly.graph_objects as go
import yfinance as yf

def markets_page():
    st.header("📈 Markets")

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
    tabs = st.tabs([s.replace(".NS", "").replace(".T", "") for s in symbols])

    for tab, sym in zip(tabs, symbols):
        with tab:
            ticker = yf.Ticker(sym)
            df = ticker.history(period="1d", interval="1m")
            if df.empty:
                st.warning(f"No data for {sym}")
                continue
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
                template="plotly_dark",
                height=320,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_rangeslider_visible=False,
            )
            st.plotly_chart(fig, use_container_width=True)

            last = df.iloc[-1]
            change = (last.Close - last.Open) / last.Open * 100
            st.metric("Price", f"{last.Close:.2f}", f"{change:+.2f}%")

    st.subheader("Search any ticker")
    ticker_input = st.text_input("Symbol (e.g., AAPL, BTC-USD)", "")
    if ticker_input.strip():
        try:
            df = yf.Ticker(ticker_input.strip()).history(period="1mo")
            if not df.empty:
                st.line_chart(df["Close"])
            else:
                st.error("No data found")
        except Exception as e:
            st.error(str(e))
