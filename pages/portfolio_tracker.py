import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

# Function to get live market price
def get_live_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.history(period="1d")["Close"].iloc[-1]
        return round(price, 2)
    except:
        return None

def portfolio_tracker_page():
    st.header("💼 Professional Portfolio Tracker")

    # Professional brief at the top
    st.markdown("""
    Welcome to the **Portfolio Tracker** — your personal investment dashboard.  
    Here, you can:
    - Track stocks, ETFs, mutual funds, or cryptocurrencies.
    - See real-time portfolio performance.
    - Visualize your asset allocation instantly.
    - Keep an eye on total gains, losses, and overall return percentage.

    _Tip: The more accurate your data, the better your insights._
    """)

    if 'portfolio' not in st.session_state:
        st.session_state['portfolio'] = []

    st.subheader("➕ Add a New Holding")
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("Asset Symbol (e.g., AAPL, INFY, BTC-USD)").upper()
        qty = st.number_input("Quantity", min_value=0.0, step=0.01)
        buy_price = st.number_input("Buy Price per Unit", min_value=0.0, step=0.01)
    with col2:
        name = st.text_input("Company/Fund Name")
        current_price = None
        if symbol:
            live_price = get_live_price(symbol)
            if live_price:
                st.success(f"Live Price: ₹{live_price}")
                current_price = live_price
            else:
                st.warning("Could not fetch live price. Please enter manually.")
                current_price = st.number_input("Current Price per Unit", min_value=0.0, step=0.01)

    if st.button("📥 Add to Portfolio", use_container_width=True):
        if symbol and qty > 0 and buy_price > 0 and current_price > 0:
            st.session_state['portfolio'].append({
                "Symbol": symbol,
                "Name": name,
                "Quantity": qty,
                "Buy Price": buy_price,
                "Current Price": current_price
            })
            st.success(f"Added {qty} units of {symbol} to portfolio.")
        else:
            st.error("Please fill all fields with valid values.")

    if st.session_state['portfolio']:
        df = pd.DataFrame(st.session_state['portfolio'])
        df["Current Value"] = df["Quantity"] * df["Current Price"]
        df["Invested"] = df["Quantity"] * df["Buy Price"]
        df["Gain/Loss"] = df["Current Value"] - df["Invested"]
        df["Gain/Loss %"] = (df["Gain/Loss"] / df["Invested"]) * 100

        total_invested = df["Invested"].sum()
        total_value = df["Current Value"].sum()
        total_gain = df["Gain/Loss"].sum()
        total_return_pct = (total_gain / total_invested) * 100 if total_invested > 0 else 0

        # Show metrics in dashboard style
        st.subheader("📊 Portfolio Overview")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Invested", f"₹{total_invested:,.2f}")
        col2.metric("Current Value", f"₹{total_value:,.2f}")
        col3.metric("Total Gain/Loss", f"₹{total_gain:,.2f}", f"{total_return_pct:.2f}%")
        col4.metric("Holdings Count", len(df))

        st.subheader("📈 Asset Allocation")
        fig = px.pie(df, values="Current Value", names="Symbol", title="Portfolio Allocation")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Detailed Holdings")
        st.dataframe(df, use_container_width=True)

    else:
        st.info("No holdings yet. Add your first investment above.")

    st.markdown("""
    ---
    ⚠️ **Disclaimer:** Investing involves risk. Past performance is not indicative of future results.  
    Always do your research before investing.
    """)

if __name__ == "__main__":
    portfolio_tracker_page()