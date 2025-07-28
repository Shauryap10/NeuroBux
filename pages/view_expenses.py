import streamlit as st
from datetime import datetime

def view_expenses_page(exp_mgr, inc_mgr):
    st.header("📑 View Expenses")

    all_expenses = exp_mgr.get_expenses(st.session_state.user_email)
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

    # --- DATA MANAGEMENT BUTTONS ---
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Reset Current Month", key="reset_month_view"):
            if st.session_state.get('confirm_reset_view', False):
                exp_mgr.reset_current_month(st.session_state.user_email)
                inc_mgr.reset_current_month(st.session_state.user_email)
                st.success("Current month reset!")
                st.session_state.confirm_reset_view = False
                st.rerun()  # ✅ UPDATED: Changed from st.experimental_rerun()
            else:
                st.session_state.confirm_reset_view = True
                st.warning("Click again to confirm")
    
    with col2:
        if st.button("🗑️ Delete Selected Month", key="delete_selected_month"):
            if st.session_state.get('confirm_delete_month', False):
                like_pattern = f"{selected_month}%"
                exp_mgr.conn.execute(
                    "DELETE FROM expenses WHERE user=? AND date LIKE ?", 
                    (st.session_state.user_email, like_pattern)
                )
                inc_mgr.conn.execute(
                    "DELETE FROM income WHERE user=? AND date LIKE ?", 
                    (st.session_state.user_email, like_pattern)
                )
                exp_mgr.conn.commit()
                inc_mgr.conn.commit()
                st.success(f"All data for {selected_month} deleted!")
                st.session_state.confirm_delete_month = False
                st.rerun()  # ✅ UPDATED: Changed from st.experimental_rerun()
            else:
                st.session_state.confirm_delete_month = True
                st.warning(f"Click again to delete ALL data for {selected_month}")
    
    with col3:
        if st.button("🗑️ Delete All Data", key="delete_all_view"):
            if st.session_state.get('confirm_delete_all_view', False):
                exp_mgr.delete_all_user_data(st.session_state.user_email)
                inc_mgr.delete_all_user_data(st.session_state.user_email)
                st.success("All data permanently deleted!")
                st.session_state.confirm_delete_all_view = False
                st.rerun()  # ✅ UPDATED: Changed from st.experimental_rerun()
            else:
                st.session_state.confirm_delete_all_view = True
                st.error("Click again to PERMANENTLY delete ALL data")
    
    with col4:
        if st.button("❌ Cancel", key="cancel_view"):
            st.session_state.confirm_reset_view = False
            st.session_state.confirm_delete_month = False
            st.session_state.confirm_delete_all_view = False
            st.info("Cancelled")

    st.markdown("---")

    exp_data = exp_mgr.get_expenses(st.session_state.user_email, year_month=selected_month)
    inc_data = inc_mgr.get_income(st.session_state.user_email, year_month=selected_month)

    st.subheader("💸 Expenses")
    if exp_data:
        for idx, row in enumerate(exp_data):
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
            col1.text(row[1])  # Category
            col2.text(f"₹{row[2]:.2f}")
            col3.text(row[3])  # Date
            col4.empty()
            if col5.button("❌", key=f"del_exp_{idx}"):
                exp_mgr.delete_expense(st.session_state.user_email, idx)
                st.rerun()  # ✅ UPDATED: Changed from st.experimental_rerun()
    else:
        st.info(f"No expenses logged for {selected_month}.")

    st.markdown("---")
    st.subheader("💰 Income")
    if inc_data:
        for idx, row in enumerate(inc_data):
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.text(f"₹{row[1]:.2f}")
            col2.text(row[2])
            if col3.button("❌", key=f"del_inc_{idx}"):
                inc_mgr.delete_income(st.session_state.user_email, idx)
                st.rerun()  # ✅ UPDATED: Changed from st.experimental_rerun()
    else:
        st.info(f"No income logged for {selected_month}.")

