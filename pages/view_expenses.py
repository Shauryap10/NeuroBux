import streamlit as st
from datetime import datetime

def view_expenses_page(exp_mgr, inc_mgr):
    st.header("📑 View Expenses")

    all_expenses = exp_mgr.get_expenses(st.session_state.user_email)

    # Extract unique months from expense dates
    months = sorted({e[3][:7] for e in all_expenses if e[3]}, reverse=True)
    if not months:
        months = [datetime.now().strftime("%Y-%m")]

    if "selected_month" not in st.session_state:
        st.session_state.selected_month = months[0]

    selected_month = st.selectbox(
        "Select Month",
        options=months,
        index=months.index(st.session_state.selected_month) if st.session_state.selected_month in months else 0,
        key="month_selector"
    )
    st.session_state.selected_month = selected_month

    exp_data = exp_mgr.get_expenses(st.session_state.user_email, year_month=selected_month)
    inc_data = inc_mgr.get_income(st.session_state.user_email, year_month=selected_month)

    if exp_data:
        for idx, row in enumerate(exp_data):
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
            col1.text(row[1])  # Category
            col2.text(f"₹{row[2]:.2f}")
            col3.text(row[3])  # Date
            col4.empty()
            if col5.button("❌", key=f"del_exp_{idx}"):
                exp_mgr.delete_expense(st.session_state.user_email, idx)
                st.experimental_rerun()
    else:
        st.info(f"No expenses logged for {selected_month}.")

    st.markdown("---")

    if inc_data:
        for idx, row in enumerate(inc_data):
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.text(f"₹{row[1]:.2f}")
            col2.text(row[2])
            if col3.button("❌", key=f"del_inc_{idx}"):
                inc_mgr.delete_income(st.session_state.user_email, idx)
                st.experimental_rerun()
    else:
        st.info(f"No income logged for {selected_month}.")
