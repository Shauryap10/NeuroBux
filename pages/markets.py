import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time

def get_stock_data(symbol, period="30d"):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        if df.empty:
            return None, f"No data found for {symbol}"
        return df, None
    except Exception as e:
        return None, str(e)

def markets_page():
    st.header("📈 Markets")

    INVESTMENT_PLATFORMS = {
        "🇮🇳 India": {
            "Zerodha": "https://zerodha.com/",
            "Groww": "https://groww.in/",
            "Angel One": "https://www.angelone.in/",
            "Upstox": "https://upstox.com/",
            "INDmoney": "https://www.indmoney.com/"
        },
        "🇺🇸 US": {
            "Robinhood": "https://robinhood.com/",
            "Public": "https://public.com/",
            "M1 Finance": "https://m1.com/",
            "Fidelity": "https://fidelity.com/",
            "Charles Schwab": "https://schwab.com/"
        },
        "🇪🇺 EU": {
            "eToro": "https://etoro.com/",
            "Trading 212": "https://trading212.com/",
            "Degiro": "https://degiro.com/",
            "Interactive Brokers": "https://interactivebrokers.com/",
            "Saxo Bank": "https://home.saxo/"
        },
        "🇯🇵 Japan": {
            "SBI Securities": "https://sbisec.co.jp/",
            "Rakuten Securities": "https://rakuten-sec.co.jp/",
            "Monex": "https://monex.co.jp/",
            "Matsui Securities": "https://matsui.co.jp/",
            "Interactive Brokers": "https://interactivebrokers.com/"
        },
        "Crypto": {
            "Coinbase": "https://coinbase.com/",
            "Binance": "https://binance.com/",
            "WazirX": "https://wazirx.com/",
            "CoinDCX": "https://coindcx.com/",
            "Kraken": "https://kraken.com/"
        },
        "Commodities": {
            "TD Ameritrade": "https://tdameritrade.com/",
            "E*TRADE": "https://etrade.com/",
            "Interactive Brokers": "https://interactivebrokers.com/",
            "Charles Schwab": "https://schwab.com/",
            "Fidelity": "https://fidelity.com/"
        }
    }

    universe = {
        "🇮🇳 India": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS"],
        "🇺🇸 US": ["AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "NVDA", "META"],
        "🇪🇺 EU": ["SAP.DE", "ASML.AS", "NESN.SW", "MC.PA"],
        "🇯🇵 Japan": ["7203.T", "6758.T", "9984.T", "6861.T", "8306.T"],
        "Crypto": ["BTC-USD", "ETH-USD", "ADA-USD", "DOT-USD", "SOL-USD"],
        "Commodities": ["GC=F", "SI=F", "CL=F", "NG=F", "HG=F"],
        "Popular ETFs": ["SPY", "QQQ", "VTI", "VOO", "IWM"]
    }

    region = st.selectbox("Pick region / asset class", list(universe.keys()))
    symbols = universe[region]

    st.markdown(f"### Investment Platforms in {region}")
    platforms = INVESTMENT_PLATFORMS.get(region, INVESTMENT_PLATFORMS["🇺🇸 US"])
    cols = st.columns(len(platforms))
    for idx, (name, url) in enumerate(platforms.items()):
        with cols[idx]:
            if st.button(name, key=f"platform_{region}_{name}"):
                st.markdown(f"[Open {name}]({url}){{target=\"_blank\"}}", unsafe_allow_html=True)

    symbol_names = [s.replace('.NS', '').replace('.DE', '').replace('.AS', '').replace('.SW', '').replace('.PA', '').replace('.T', '').replace('-USD', '') for s in symbols]
    tabs = st.tabs(symbol_names)

    currency_mapping = {
        "🇮🇳 India": "₹",
        "🇺🇸 US": "$",
        "🇪🇺 EU": "€",
        "🇯🇵 Japan": "¥",
    }
    currency = currency_mapping.get(region, "$")

    for tab, symbol in zip(tabs, symbols):
        with tab:
            st.subheader(f"{symbol}")
            with st.spinner(f"Loading {symbol} data..."):
                df, error = get_stock_data(symbol)
                time.sleep(1)

            if error:
                st.error(error)
                st.info("You can still access investment platforms below.")
            else:
                fig = go.Figure(data=[go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name=symbol,
                    increasing_line_color='#26a69a',
                    decreasing_line_color='#ef5350'
                )])
                fig.update_layout(
                    title=f"{symbol} - 30-Day Chart",
                    template="plotly_dark",
                    height=450,
                    xaxis_title="Date",
                    yaxis_title=f"Price ({currency})",
                    xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)

                latest = df.iloc[-1]
                previous = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
                change = (latest.Close - previous.Close) / previous.Close * 100

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Current Price", f"{currency}{latest.Close:.2f}")
                col2.metric("Daily Change", f"{change:+.2f}%")
                col3.metric("High", f"{currency}{latest.High:.2f}")
                col4.metric("Low", f"{currency}{latest.Low:.2f}")

            st.markdown("---")
            st.subheader(f"Invest in {symbol}")
            invest_cols = st.columns(min(3, len(platforms)))
            top_platforms = list(platforms.items())[:3]
            for idx, (platform_name, platform_url) in enumerate(top_platforms):
                with invest_cols[idx]:
                    if st.button(f"Buy on {platform_name}", key=f"buy_{symbol}_{platform_name}"):
                        st.success(f"Opening {platform_name} for {symbol}...")
                        st.markdown(f"[Invest via {platform_name}]({platform_url})", unsafe_allow_html=True)

if __name__ == "__main__":
    markets_page()
