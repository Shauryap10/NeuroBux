import streamlit as st
from datetime import datetime

def view_expenses_page(exp_mgr, inc_mgr):
    st.header("View Expenses")

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
                st.rerun()
            else:
                st.session_state.confirm_reset_view = True
                st.warning("Click again to confirm")
    
    with col2:
        if st.button("🗑️ Delete Selected Month", key="delete_selected_month"):
            if st.session_state.get('confirm_delete_month', False):
                # Updated for Supabase - use date range deletion
                start_date = f"{selected_month}-01"
                end_date = f"{selected_month}-31"
                
                # Delete expenses for the month using Supabase
                exp_mgr.supabase.table("expenses").delete().eq("user_email", st.session_state.user_email).gte("date", start_date).lte("date", end_date).execute()
                
                # Delete income for the month using Supabase
                inc_mgr.supabase.table("income").delete().eq("user_email", st.session_state.user_email).gte("date", start_date).lte("date", end_date).execute()
                
                st.success(f"All data for {selected_month} deleted!")
                st.session_state.confirm_delete_month = False
                st.rerun()
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
                st.rerun()
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

    # --- EXPENSES SECTION WITH SUPABASE ID-BASED DELETION ---
    st.subheader("💸 Expenses")
    
    try:
        # Get expenses with full database information including IDs from Supabase
        if selected_month:
            start_date = f"{selected_month}-01"
            end_date = f"{selected_month}-31"
            exp_result = exp_mgr.supabase.table("expenses").select("*").eq("user_email", st.session_state.user_email).gte("date", start_date).lte("date", end_date).order("date", desc=True).execute()
        else:
            exp_result = exp_mgr.supabase.table("expenses").select("*").eq("user_email", st.session_state.user_email).order("date", desc=True).execute()
        
        exp_full_data = exp_result.data
        
        if exp_full_data:
            for row in exp_full_data:
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                col1.text(row['category'])
                col2.text(f"₹{row['amount']:.2f}")
                col3.text(row['date'])
                col4.empty()
                
                # Use the actual database ID for deletion
                if col5.button("❌", key=f"del_exp_{row['id']}"):
                    if exp_mgr.delete_expense(st.session_state.user_email, row['id']):
                        st.success("Expense deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete expense")
        else:
            st.info(f"No expenses logged for {selected_month}.")
            
    except Exception as e:
        st.error(f"Error loading expenses: {str(e)}")

    st.markdown("---")
    
    # --- INCOME SECTION WITH SUPABASE ID-BASED DELETION ---
    st.subheader("💰 Income")
    
    try:
        # Get income with full database information including IDs from Supabase
        if selected_month:
            start_date = f"{selected_month}-01"
            end_date = f"{selected_month}-31"
            inc_result = inc_mgr.supabase.table("income").select("*").eq("user_email", st.session_state.user_email).gte("date", start_date).lte("date", end_date).order("date", desc=True).execute()
        else:
            inc_result = inc_mgr.supabase.table("income").select("*").eq("user_email", st.session_state.user_email).order("date", desc=True).execute()
        
        inc_full_data = inc_result.data
        
        if inc_full_data:
            for row in inc_full_data:
                col1, col2, col3 = st.columns([3, 2, 1])
                col1.text(f"₹{row['amount']:.2f}")
                col2.text(row['date'])
                
                # Use the actual database ID for deletion
                if col3.button("❌", key=f"del_inc_{row['id']}"):
                    if inc_mgr.delete_income(st.session_state.user_email, row['id']):
                        st.success("Income deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete income")
        else:
            st.info(f"No income logged for {selected_month}.")
            
    except Exception as e:
        st.error(f"Error loading income: {str(e)}")

