import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import calendar

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase_url"]
        key = st.secrets["supabase_key"]
        supabase: Client = create_client(url, key)
        return supabase
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {str(e)}")
        return None

supabase = init_supabase()

def _get_month_date_range(year_month_str):
    """
    Helper function to get the correct start and end date for a month string (e.g., "2025-09").
    """
    # <<<--- DEBUG MESSAGE TO PROVE THE NEW CODE IS RUNNING ---<<<
    st.toast("✅ Using correct date range function!", icon="🎉")
    
    year, month = map(int, year_month_str.split('-'))
    _, num_days = calendar.monthrange(year, month)
    start_date = f"{year_month_str}-01"
    end_date = f"{year_month_str}-{num_days}"
    return start_date, end_date

class ExpenseManager:
    def __init__(self):
        self.supabase = supabase

    def get_expenses(self, user, year_month=None):
        if not self.supabase:
            return []
        
        try:
            query = self.supabase.table("expenses").select("*").eq("user_email", user)
            
            if year_month:
                start_date, end_date = _get_month_date_range(year_month)
                query = query.gte("date", start_date).lte("date", end_date)
            
            result = query.order("date", desc=True).execute()
            
            expenses = []
            for row in result.data:
                expenses.append((row['user_email'], row['category'], row['amount'], row['date']))
            return expenses
        except Exception as e:
            st.error(f"Error fetching expenses: {str(e)}")
            return []

    def reset_current_month(self, user):
        if not self.supabase:
            return False
        
        current_month_str = datetime.now().strftime("%Y-%m")
        try:
            start_date, end_date = _get_month_date_range(current_month_str)
            result = self.supabase.table("expenses").delete().eq("user_email", user).gte("date", start_date).lte("date", end_date).execute()
            return True
        except Exception as e:
            st.error(f"Error resetting current month: {str(e)}")
            return False
    # ... (rest of your unchanged methods like add_expense, delete_expense, etc.)

class IncomeManager:
    def __init__(self):
        self.supabase = supabase

    def get_income(self, user, year_month=None):
        if not self.supabase:
            return []
        
        try:
            query = self.supabase.table("income").select("*").eq("user_email", user)
            
            if year_month:
                start_date, end_date = _get_month_date_range(year_month)
                query = query.gte("date", start_date).lte("date", end_date)
            
            result = query.order("date", desc=True).execute()
            
            income = []
            for row in result.data:
                income.append((row['user_email'], row['amount'], row['date']))
            return income
        except Exception as e:
            st.error(f"Error fetching income: {str(e)}")
            return []

    def reset_current_month(self, user):
        if not self.supabase:
            return False
        
        current_month_str = datetime.now().strftime("%Y-%m")
        try:
            start_date, end_date = _get_month_date_range(current_month_str)
            result = self.supabase.table("income").delete().eq("user_email", user).gte("date", start_date).lte("date", end_date).execute()
            return True
        except Exception as e:
            st.error(f"Error resetting current month income: {str(e)}")
            return False
    # ... (rest of your unchanged methods in IncomeManager)

# ... (rest of your file, including SpendingAnalyzer class, which needs no changes)

