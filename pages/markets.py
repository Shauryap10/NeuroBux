import streamlit as st
import plotly.graph_objects as go
import requests
import pandas as pd
import time
from datetime import datetime

def markets_page():
    st.header("📈 Markets")

    INVESTMENT_PLATFORMS = {
        "🇮🇳": {
            "Zerodha": "https://zerodha.com/",
            "Groww": "https://groww.in/",
            "Angel One": "https://www.angelone.in/",
            "Upstox": "https://upstox.com/",
            "INDmoney": "https://www.indmoney.com/"
        },
        "🇺🇸": {
            "Robinhood": "https://robinhood.com",
            "Public": "https://public.com",
            "M1 Finance": "https://m1.com",
            "Fidelity": "https://fidelity.com",
            "Charles Schwab": "https://schwab.com"
        },
        "🇪🇺": {
            "eToro": "https://etoro.com",
            "Trading 212": "https://trading212.com",
            "Degiro": "https://degiro.com",
            "Interactive Brokers": "https://interactivebrokers.com",
            "Saxo Bank": "https://home.saxo"
        },
        "🇯🇵": {
            "SBI Securities": "https://sbisec.co.jp",
            "Rakuten Securities": "https://rakuten-sec.co.jp",
            "Monex": "https://monex.co.jp",
            "Matsui": "https://matsui.co.jp",
            "Interactive Brokers": "https://interactivebrokers.com"
        },
        "Crypto": {
            "Coinbase": "https://coinbase.com",
            "Binance": "https://binance.com",
            "WazirX": "https://wazirx.com",
            "CoinDCX": "https://coindcx.com",
            "Kraken": "https://kraken.com"
        },
        "Commodities": {
            "TD Ameritrade": "https://tdameritrade.com",
            "E*TRADE": "https://etrade.com",
            "Interactive Brokers": "https://interactivebrokers.com",
            "Charles Schwab": "https://schwab.com",
            "Fidelity": "https://fidelity.com"
        }
    }

    def get_api_key():
        key = st.secrets.get("alpha_vantage_api_key")
        if not key:
            st.error("Alpha Vantage API key not configured in secrets.")
            st.stop()
        return key

    def get_stock_data(symbol):
        api_key = get_api_key()
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": api_key,
            "outputsize": "compact"
        }
        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            if "Time Series (Daily)" in data:
                df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
                df = df.rename(columns={
                    '1. open': 'Open',
                    '2. high': 'High',
                    '3. low': 'Low',
                    '4. close': 'Close',
                    '5. volume': 'Volume'
                })
                df.index = pd.to_datetime(df.index)
                df = df.astype(float).sort_index()
                return df.tail(30), None

            elif "Error Message" in data:
                return None, f"API Error: {data['Error Message']}"

            elif "Note" in data:
                return None, f"API Rate Limit: {data['Note']} Please wait and try again."

            elif "Information" in data:
                return None, f"API Info: {data['Information']}"

            else:
                return None, f"Unknown API response: {data}"

        except Exception as e:
            return None, f"Request error: {e}"

    def get_crypto_data(symbol):
        api_key = get_api_key()
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol.replace("-USD", ""),
            "market": "USD",
            "apikey": api_key
        }
        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            if "Time Series (Digital Currency Daily)" in data:
                df = pd.DataFrame.from_dict(data["Time Series (Digital Currency Daily)"], orient="index")
                df['Open'] = df['1a. open (USD)'].astype(float)
                df['High'] = df['2a. high (USD)'].astype(float)
                df['Low'] = df['3a. low (USD)'].astype(float)
                df['Close'] = df['4a. close (USD)'].astype(float)
                df['Volume'] = df['5. volume'].astype(float)
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                return df.tail(30)[['Open', 'High', 'Low', 'Close', 'Volume']], None

            elif "Error Message" in data:
                return None, f"API Error: {data['Error Message']}"

            else:
                return None, "Crypto data not available"

        except Exception as e:
            return None, f"Request error: {e}"

    # Test connection once
    connected, status_msg = None, None
    try:
        df_test, err_test = get_stock_data("AAPL")
        if df_test is not None:
            connected, status_msg = True, "✅ Connected to Alpha Vantage successfully."
        else:
            connected, status_msg = False, f"❌ Connection error: {err_test}"
    except Exception as e:
        connected, status_msg = False, f"❌ Connection exception: {str(e)}"

    if not connected:
        st.error(status_msg)
        st.warning("Please ensure your Alpha Vantage API key is valid and you are not hitting rate limits.")
        st.markdown("---")

    # Show investment platforms regardless
    st.subheader("Investment Platforms")
    region_for_platforms = st.selectbox("Choose platform region", list(INVESTMENT_PLATFORMS.keys()))
    platforms = INVESTMENT_PLATFORMS[region_for_platforms]
    cols = st.columns(len(platforms))
    for idx, (name, url) in enumerate(platforms.items()):
        with cols[idx]:
            if st.button(name, key=f"platform_{name}"):
                st.markdown(f"[Visit {name}]({url}){{:target='_blank'}}", unsafe_allow_html=True)

    if not connected:
        return

    # Select market region
    region = st.selectbox("Select Market Region", list([
        "🇮🇳", "🇺🇸", "🇪🇺", "🇯🇵", "Crypto", "Commodities", "Popular ETFs"
    ]))

    market_map = {
        "🇮🇳": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"],
        "🇺🇸": ["AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "NVDA", "META"],
        "🇪🇺": ["SAP.DE", "ASML.AS", "NESN.SW", "MC.PA"],
        "🇯🇵": ["7203.T", "6758.T", "9984.T"],
        "Crypto": ["BTC-USD", "ETH-USD", "ADA-USD", "DOT-USD", "SOL-USD"],
        "Commodities": ["GC=F", "SI=F", "CL=F", "NG=F", "HG=F"],
        "Popular ETFs": ["SPY", "QQQ", "VTI", "VOO", "IWM"]
    }

    symbols = market_map.get(region, ["AAPL"])

    cols = st.columns(len(symbols))
    for idx, symbol in enumerate(symbols):
        with cols[idx]:
            st.markdown(f"**{symbol}**")

    tabs = st.tabs([s.replace(".NS", "").replace(".DE", "").replace(".AS", "").replace(".SW", "").replace(".PA", "").replace(".T", "") for s in symbols])

    currency_map = {
        "🇮🇳": "₹",
        "🇺🇸": "$",
        "🇪🇺": "€",
        "🇯🇵": "¥",
        "Crypto": "$",
        "Commodities": "$",
        "Popular ETFs": "$"
    }
    currency = currency_map.get(region, "$")

    for tab, symbol in zip(tabs, symbols):
        with tab:
            st.subheader(f"{symbol}")
            with st.spinner(f"Loading data for {symbol}..."):
                if region == "Crypto":
                    df, err = get_crypto_data(symbol)
                else:
                    df, err = get_stock_data(symbol)

                time.sleep(12)  # be polite and avoid rate limit

                if err:
                    st.error(err)
                    continue

                fig = go.Figure(data=[go.Candlestick(
                    x=df.index,
                    open=df["Open"],
                    high=df["High"],
                    low=df["Low"],
                    close=df["Close"],
                    name=symbol
                )])

                fig.update_layout(
                    title=f"{symbol} Price Chart (Last 30 Days)",
                    xaxis_title="Date",
                    yaxis_title=f"Price ({currency})",
                    template="plotly_dark",
                    height=450,
                    xaxis_rangeslider_visible=False
                )
                st.plotly_chart(fig, use_container_width=True)

                latest = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
                change_pct = (latest["Close"] - prev["Close"]) / prev["Close"] * 100

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Price", f"{currency}{latest['Close']:.2f}")
                col2.metric("Change", f"{change_pct:+.2f}%")
                col3.metric("Day High", f"{currency}{latest['High']:.2f}")
                col4.metric("Day Low", f"{currency}{latest['Low']:.2f}")

                st.markdown("---")
                st.subheader("Invest via Platforms")
                inv_cols = st.columns(min(3, len(platforms)))
                for i, (plat_name, plat_url) in enumerate(list(platforms.items())[:3]):
                    with inv_cols[i]:
                        if st.button(f"Buy on {plat_name}", key=f"buy_{symbol}_{plat_name}"):
                            st.success(f"Redirecting to {plat_name} for {symbol}")
                            st.markdown(f"[Click here to invest on {plat_name}]({plat_url}){{:target='_blank'}}", unsafe_allow_html=True)

if __name__ == "__main__":
    markets_page()
