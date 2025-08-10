import streamlit as st
import pandas as pd
import plotly.express as px

def portfolio_tracker_page():
    st.header("💼 Portfolio Tracker")

    # Professional Intro
    with st.expander("ℹ️ About the Portfolio Tracker", expanded=True):
        st.write("""
        The **Portfolio Tracker** helps you monitor your investments in one place.
        You can track stocks, mutual funds, ETFs, or any other assets.
        
        **Key Features:**
        - Add holdings with quantity, buy price, and current price.
        - See real-time gain/loss in both value and percentage.
        - Visualize asset allocation with an interactive pie chart.
        - Get a quick overview of your total invested amount and returns.

        **Tip:** Always keep your data updated to get accurate performance metrics.
        """)

    # Load initial state
    if 'portfolio' not in st.session_state:
        st.session_state['portfolio'] = []

    st.subheader("➕ Add a Holding")
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("Asset Symbol (e.g., AAPL, INFY, BTC-USD)")
        qty = st.number_input("Quantity", min_value=0.0, step=0.01)
        buy_price = st.number_input("Buy Price per Unit", min_value=0.0, step=0.01)
    with col2:
        name = st.text_input("Company/Fund Name")
        current_price = st.number_input("Current Price per Unit", min_value=0.0, step=0.01)

    add_btn = st.button("📥 Add to Portfolio", use_container_width=True)

    if add_btn and symbol and qty > 0 and buy_price > 0 and current_price > 0:
        st.session_state['portfolio'].append({
            "Symbol": symbol.upper(),
            "Name": name,
            "Quantity": qty,
            "Buy Price": buy_price,
            "Current Price": current_price
        })
        st.success(f"✅ Added {qty} units of {symbol.upper()} to your portfolio.")

    # Portfolio Table
    if st.session_state['portfolio']:
        df = pd.DataFrame(st.session_state['portfolio'])
        df["Current Value"] = df["Quantity"] * df["Current Price"]
        df["Invested"] = df["Quantity"] * df["Buy Price"]
        df["Gain/Loss"] = df["Current Value"] - df["Invested"]
        df["Gain/Loss %"] = (df["Gain/Loss"] / df["Invested"]) * 100

        st.subheader("📊 Your Portfolio")
        st.dataframe(df, use_container_width=True)

        # Allocation chart
        st.subheader("📈 Portfolio Allocation")
        fig = px.pie(df, values="Current Value", names="Symbol", title="Asset Allocation")
        st.plotly_chart(fig, use_container_width=True)

        # Total metrics
        total_invested = df["Invested"].sum()
        total_value = df["Current Value"].sum()
        total_gain = df["Gain/Loss"].sum()
        st.markdown(f"""
        **💰 Total Invested:** ₹{total_invested:.2f}  
        **📈 Current Value:** ₹{total_value:.2f}  
        **📊 Total Gain/Loss:** ₹{total_gain:+.2f}
        """)

    else:
        st.info("Your portfolio is empty. Add a holding above.")

    # Investing disclaimer
    st.markdown("""
    ---
    ⚠️ *Investing involves risk of loss. Please consider your financial goals and risk tolerance before investing.*  
    *Past performance is no guarantee of future results.*
    """)

if __name__ == "__main__":
    portfolio_tracker_page()