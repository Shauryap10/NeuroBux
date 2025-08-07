import streamlit as st
import investpy
import plotly.graph_objects as go
import pandas as pd
import datetime
import time

# Cache Investpy data fetches to reduce repeated API calls and avoid rate limiting
@st.cache_data(ttl=900)
def get_stock_data_investpy(symbol, country, from_date, to_date):
    """
    Fetch stock data from Investpy (Investing.com)
    
    Args:
        symbol (str): Stock symbol (without suffixes)
        country (str): Country name as required by investpy
        from_date (str): Starting date in dd/mm/yyyy format
        to_date (str): Ending date in dd/mm/yyyy format
    
    Returns:
        DataFrame or None, error message or None
    """
    try:
        df = investpy.get_stock_historical_data(
            stock=symbol,
            country=country,
            from_date=from_date,
            to_date=to_date
        )
        if df.empty:
            return None, f"No data found for {symbol} in {country} via Investpy."
        return df, None
    except Exception as e:
        return None, f"Investpy error for {symbol}: {str(e)}"


def markets_page():
    st.header("📈 Markets (Powered by Investpy)")

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
            "Rakuten Securities": "https://www.rakuten-sec.co.jp/",
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

    # Universe of symbols mapped by region
    universe = {
        "🇮🇳 India": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BHARTIARTL"],
        "🇺🇸 US": ["AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "NVDA", "META"],
        "🇪🇺 EU": ["SAP", "ASML", "NESN", "MC"],
        "🇯🇵 Japan": ["7203", "6758", "9984", "6861", "8306"],
        # Investpy does not support crypto or commodities directly well, so these are removed
    }

    # Map Streamlit region keys to Investpy country names
    investpy_country_map = {
        "🇮🇳 India": "India",
        "🇺🇸 US": "United States",
        "🇪🇺 EU": "Germany",   # Set to Germany for EU demo; adjust as needed per symbol
        "🇯🇵 Japan": "Japan"
    }

    currency_mapping = {
        "🇮🇳 India": "₹",
        "🇺🇸 US": "$",
        "🇪🇺 EU": "€",
        "🇯🇵 Japan": "¥",
    }

    region = st.selectbox("Pick region / asset class", list(universe.keys()))
    symbols = universe[region]
    country = investpy_country_map.get(region, "United States")
    currency = currency_mapping.get(region, "$")

    st.markdown(f"### Investment Platforms in {region}")
    platforms = INVESTMENT_PLATFORMS.get(region, INVESTMENT_PLATFORMS["🇺🇸 US"])
    cols = st.columns(len(platforms))
    for idx, (name, url) in enumerate(platforms.items()):
        with cols[idx]:
            if st.button(name, key=f"platform_{region}_{name}"):
                st.markdown(f"[Open {name}]({url}){{target=\"_blank\"}}", unsafe_allow_html=True)

    # Convert symbols to Investpy style (remove suffixes like .NS, .T, etc. — we store clean names)
    tabs = st.tabs(symbols)

    today = datetime.date.today()
    from_date = (today - datetime.timedelta(days=30)).strftime('%d/%m/%Y')
    to_date = today.strftime('%d/%m/%Y')

    for tab, symbol in zip(tabs, symbols):
        with tab:
            st.subheader(symbol)
            with st.spinner(f"Loading {symbol} data from Investpy..."):
                df, error = get_stock_data_investpy(symbol, country, from_date, to_date)
                time.sleep(1)  # polite delay to avoid scraping limits

            if error:
                st.error(error)
                st.info("Investment platforms are still accessible below.")
            else:
                # Format and display candlestick chart
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
                    title=f"{symbol} - 30-Day Chart (Investpy)",
                    template="plotly_dark",
                    height=450,
                    xaxis_title="Date",
                    yaxis_title=f"Price ({currency})",
                    xaxis_rangeslider_visible=False
                )
                st.plotly_chart(fig, use_container_width=True)

                latest = df.iloc[-1]
                previous = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
                change_pct = (latest.Close - previous.Close) / previous.Close * 100

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Current Price", f"{currency}{latest.Close:.2f}")
                col2.metric("Daily Change", f"{change_pct:+.2f}%")
                col3.metric("Day High", f"{currency}{latest.High:.2f}")
                col4.metric("Day Low", f"{currency}{latest.Low:.2f}")

            st.markdown("---")
            st.subheader(f"Invest in {symbol}")
            invest_cols = st.columns(min(3, len(platforms)))
            top_platforms = list(platforms.items())[:3]
            for idx, (platform_name, platform_url) in enumerate(top_platforms):
                with invest_cols[idx]:
                    if st.button(f"Buy on {platform_name}", key=f"buy_{symbol}_{platform_name}"):
                        st.success(f"Opening {platform_name} for {symbol}...")
                        st.markdown(f"[Invest via {platform_name}]({platform_url})", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    *Investing involves risk of loss. Please consider your financial goals and risk tolerance before investing.
    Past performance is no guarantee of future results. Always do your due diligence or consult a financial adviser.*
    """)


if __name__ == "__main__":
    markets_page()
