import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
import time

def get_stock_data_yfinance(symbol, period="30d"):
    """
    Fetch stock data from Yahoo Finance using yfinance.
    Args:
        symbol (str): Ticker symbol, e.g., 'AAPL', 'RELIANCE.NS'
        period (str): Data period, e.g., '30d', '1mo', '1y'
    Returns:
        pd.DataFrame or None, error message or None
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        if df.empty:
            return None, f"No data available for {symbol} from Yahoo Finance."
        else:
            return df, None
    except Exception as e:
        return None, f"Failed to fetch data for {symbol}: {str(e)}"

def markets_page():
    st.header("📈 Markets (Yahoo Finance)")

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
        "🇪🇺 EU": {
            "eToro": "https://www.etoro.com/",
            "Trading 212": "https://www.trading212.com/",
            "Degiro": "https://www.degiro.com/",
            "Interactive Brokers": "https://www.interactivebrokers.com/",
            "Saxo Bank": "https://www.home.saxo/"
        },
        "🇯🇵 Japan": {
            "SBI Securities": "https://www.sbisec.co.jp/",
            "Rakuten Securities": "https://www.rakuten-sec.co.jp/",
            "Monex": "https://www.monex.co.jp/",
            "Matsui Securities": "https://www.matsui.co.jp/",
            "Interactive Brokers": "https://www.interactivebrokers.com/"
        },
        "Crypto": {
            "Coinbase": "https://www.coinbase.com/",
            "Binance": "https://www.binance.com/",
            "WazirX": "https://wazirx.com/",
            "CoinDCX": "https://coindcx.com/",
            "Kraken": "https://www.kraken.com/"
        },
        "Commodities": {
            "TD Ameritrade": "https://www.tdameritrade.com/",
            "E*TRADE": "https://www.etrade.com/",
            "Interactive Brokers": "https://www.interactivebrokers.com/",
            "Charles Schwab": "https://www.schwab.com/",
            "Fidelity": "https://www.fidelity.com/"
        }
    }

    universe = {
        "🇮🇳 India": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS"],
        "🇺🇸 US": ["AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "NVDA", "META"],
        "🇪🇺 EU": ["ASML.AS", "SAP.DE", "NESN.SW", "MC.PA", "RDSA.AS"],
        "🇯🇵 Japan": ["7203.T", "6758.T", "9984.T", "6861.T", "8306.T"],
        "Crypto": ["BTC-USD", "ETH-USD", "ADA-USD", "DOT-USD", "SOL-USD"],
        "Commodities": ["GC=F", "SI=F", "CL=F", "NG=F", "HG=F"],
        "Popular ETFs": ["SPY", "QQQ", "VTI", "VOO", "IWM"]
    }

    region = st.selectbox("Pick region / asset class", list(universe.keys()))
    symbols = universe[region]

    st.markdown(f"### 💰 Investment Platforms in {region}")
    platforms = INVESTMENT_PLATFORMS.get(region, INVESTMENT_PLATFORMS["🇺🇸 US"])
    cols = st.columns(len(platforms))
    for idx, (platform_name, platform_url) in enumerate(platforms.items()):
        with cols[idx]:
            if st.button(platform_name, key=f"platform_{platform_name}"):
                st.markdown(f"[Open {platform_name}]({platform_url}){{target=\"_blank\"}}", unsafe_allow_html=True)

    symbol_names = [s.replace(".NS", "").replace(".AS", "").replace(".DE", "").replace(".SW", "").replace(".PA", "").replace(".T", "").replace("-USD","") for s in symbols]
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

            with st.spinner(f"Loading {symbol} data from Yahoo Finance..."):
                df, error = get_stock_data_yfinance(symbol)
                time.sleep(1)  # gentle delay to avoid rate limiting

            if error:
                st.error(error)
                continue

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
            col3.metric("Day High", f"{currency}{latest.High:.2f}")
            col4.metric("Day Low", f"{currency}{latest.Low:.2f}")

            st.markdown("---")
            st.subheader(f"💳 Ready to Invest in {symbol}?")

            invest_cols = st.columns(min(3, len(platforms)))
            top_platforms = list(platforms.items())[:3]

            for idx, (platform_name, platform_url) in enumerate(top_platforms):
                with invest_cols[idx]:
                    if st.button(f"Buy on {platform_name}", key=f"buy_{symbol}_{platform_name}"):
                        st.balloons()
                        st.success(f"🚀 Opening {platform_name} to invest in {symbol}")
                        st.markdown(f'<a href="{platform_url}" target="_blank">Open {platform_name}</a>', unsafe_allow_html=True)

if __name__ == "__main__":
    markets_page()
