import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import export_df_to_csv, export_df_to_pdf

def dashboard_page(exp_mgr, inc_mgr):
    st.header("📊 Dashboard")

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
        key="month_selector_dashboard"
    )
    st.session_state.selected_month = selected_month

    exp_data = exp_mgr.get_expenses(st.session_state.user_email, year_month=selected_month)
    inc_data = inc_mgr.get_income(st.session_state.user_email, year_month=selected_month)

    df_exp = pd.DataFrame(exp_data, columns=["User", "Category", "Amount", "Date"])
    df_inc = pd.DataFrame(inc_data, columns=["User", "Amount", "Date"])

    if df_exp.empty:
        df_exp = pd.DataFrame(columns=["User", "Category", "Amount", "Date"])
    if df_inc.empty:
        df_inc = pd.DataFrame(columns=["User", "Amount", "Date"])

    total_spent = df_exp["Amount"].sum()
    total_income = df_inc["Amount"].sum()
    net = total_income - total_spent

    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total Spent", f"₹{total_spent:,.2f}")
    col2.metric("💵 Total Income", f"₹{total_income:,.2f}")
    col3.metric("💰 Net", f"₹{net:,.2f}")

    if not df_exp.empty:
        df_exp["Date"] = pd.to_datetime(df_exp["Date"], errors='coerce')
        fig = px.bar(df_exp, x="Date", y="Amount", color="Category", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    if not df_exp.empty or not df_inc.empty:
        df_exp_plot = df_exp[["Date", "Amount"]].copy()
        df_exp_plot["Type"] = "Expense"
        df_inc_plot = df_inc[["Date", "Amount"]].copy()
        df_inc_plot["Type"] = "Income"
        df_combined = pd.concat([df_exp_plot, df_inc_plot], ignore_index=True)
        if not df_combined.empty:
            df_combined["Date"] = pd.to_datetime(df_combined["Date"], errors='coerce')
            fig2 = px.bar(df_combined, x="Date", y="Amount", color="Type", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

    # --- EXPORT Buttons ---
    st.markdown("---")
    st.subheader("📤 Export Data")

    col1, col2 = st.columns(2)
    
    with col1:
        if not df_exp.empty and len(df_exp) > 0:
            try:
                # Remove User column if it exists and ensure data is clean
                export_df_exp = df_exp.drop(columns=["User"], errors='ignore')
                
                csv_bytes_exp = export_df_to_csv(export_df_exp)
                pdf_bytes_exp = export_df_to_pdf(export_df_exp, title=f"Expenses for {selected_month}")

                st.download_button(
                    "📄 Export Expenses as CSV",
                    data=csv_bytes_exp,
                    file_name=f"expenses_{selected_month}.csv",
                    mime="text/csv",
                )

                st.download_button(
                    "📄 Export Expenses as PDF",
                    data=pdf_bytes_exp,
                    file_name=f"expenses_{selected_month}.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"Error exporting expenses: {str(e)}")
        else:
            st.info("No expense data to export for this month.")

    with col2:
        if not df_inc.empty and len(df_inc) > 0:
            try:
                # Remove User column if it exists and ensure data is clean
                export_df_inc = df_inc.drop(columns=["User"], errors='ignore')
                
                csv_bytes_inc = export_df_to_csv(export_df_inc)
                pdf_bytes_inc = export_df_to_pdf(export_df_inc, title=f"Incomes for {selected_month}")

                st.download_button(
                    "📄 Export Income as CSV",
                    data=csv_bytes_inc,
                    file_name=f"income_{selected_month}.csv",
                    mime="text/csv",
                )

                st.download_button(
                    "📄 Export Income as PDF",
                    data=pdf_bytes_inc,
                    file_name=f"income_{selected_month}.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"Error exporting income: {str(e)}")
        else:
            st.info("No income data to export for this month.")

    # --- DATA MANAGEMENT SECTION ---
    st.markdown("---")
    st.subheader("🗂️ Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reset Current Month", help="Clear only this month's data", type="secondary"):
            if st.session_state.get('confirm_reset_month', False):
                exp_mgr.reset_current_month(st.session_state.user_email)
                inc_mgr.reset_current_month(st.session_state.user_email)
                st.success("✅ Current month's data has been reset!")
                st.session_state.confirm_reset_month = False
                st.rerun()  # ✅ UPDATED: Changed from st.experimental_rerun()
            else:
                st.session_state.confirm_reset_month = True
                st.warning("⚠️ Click again to confirm reset of current month's data")
    
    with col2:
        if st.button("🗑️ Delete All Data", help="Permanently delete ALL your data", type="secondary"):
            if st.session_state.get('confirm_delete_all', False):
                exp_mgr.delete_all_user_data(st.session_state.user_email)
                inc_mgr.delete_all_user_data(st.session_state.user_email)
                st.success("✅ All data has been permanently deleted!")
                st.session_state.confirm_delete_all = False
                st.rerun()  # ✅ UPDATED: Changed from st.experimental_rerun()
            else:
                st.session_state.confirm_delete_all = True
                st.error("🚨 Click again to PERMANENTLY delete ALL your data")
    
    with col3:
        if st.button("❌ Cancel", help="Cancel any pending operations"):
            st.session_state.confirm_reset_month = False
            st.session_state.confirm_delete_all = False
            st.info("Operation cancelled")
