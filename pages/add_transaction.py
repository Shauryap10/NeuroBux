import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import StringIO

def add_transaction_page(exp_mgr, inc_mgr):
    st.header("➕ Add Transaction")

    # Month Selector
    all_expenses = exp_mgr.get_expenses(st.session_state.user_email)
    months = sorted({e[3][:7] for e in all_expenses if e[3]}, reverse=True)
    if not months:
        months = [datetime.now().strftime("%Y-%m")]

    if "selected_month" not in st.session_state:
        st.session_state.selected_month = months[0]

    selected_month = st.selectbox(
        "Select Month for viewing expenses:",
        options=months,
        index=months.index(st.session_state.selected_month) if st.session_state.selected_month in months else 0,
        key="month_selector_add"
    )
    st.session_state.selected_month = selected_month

    # REMOVED: Auto-reset check block

    # --- Import CSV Section ---
    st.subheader("📥 Import from CSV")

    uploaded_file = st.file_uploader("Upload CSV file for Import", type=["csv"], help="CSV for expenses should have columns: Category, Amount, Date. For income: Amount, Date")

    if uploaded_file:
        try:
            file_content = StringIO(uploaded_file.getvalue().decode("utf-8"))
            df_import = pd.read_csv(file_content)
            
            # Determine if import is expense or income by presence of 'Category' column
            if "Category" in df_import.columns:
                # Treat as Expenses
                required_cols = {"Category", "Amount", "Date"}
                if not required_cols.issubset(set(df_import.columns)):
                    st.error("Expense import must have columns: Category, Amount, Date")
                else:
                    count_added = 0
                    for _, row in df_import.iterrows():
                        try:
                            category = str(row['Category'])
                            amount = float(row['Amount'])
                            date_str = str(row['Date'])
                            exp_mgr.add_expense(st.session_state.user_email, category, amount, date_str)
                            count_added += 1
                        except Exception as e:
                            continue
                    st.success(f"Imported {count_added} expense records successfully.")
            elif {"Amount", "Date"}.issubset(set(df_import.columns)):
                # Treat as Income
                count_added = 0
                for _, row in df_import.iterrows():
                    try:
                        amount = float(row['Amount'])
                        date_str = str(row['Date'])
                        inc_mgr.add_income(st.session_state.user_email, amount, date_str)
                        count_added += 1
                    except:
                        continue
                st.success(f"Imported {count_added} income records successfully.")
            else:
                st.error("CSV format not recognized for import.")
        except Exception as e:
            st.error(f"Error processing file: {e}")

    # --- Add Transaction Form ---
    st.subheader("➕ Manual Entry")
    option = st.radio("Type", ["Expense", "Income"], horizontal=True)

    with st.form("tx_form"):
        if option == "Expense":
            category = st.text_input("Category")
            amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
        else:
            category = None
            amount = st.number_input("Income Amount", min_value=0.01, step=0.01, format="%.2f")

        tx_date = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("Save")

        if submitted:
            if option == "Expense":
                if not category:
                    st.error("Please enter a category.")
                elif amount <= 0:
                    st.error("Amount must be greater than zero.")
                else:
                    exp_mgr.add_expense(st.session_state.user_email, category, amount, str(tx_date))
                    st.success("Expense saved!")
            else:
                if amount <= 0:
                    st.error("Income amount must be greater than zero.")
                else:
                    inc_mgr.add_income(st.session_state.user_email, amount, str(tx_date))
                    st.success("Income saved!")
