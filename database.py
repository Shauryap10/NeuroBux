import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

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

class ExpenseManager:
    def __init__(self):
        self.supabase = supabase

    def add_expense(self, user, cat, amt, dt_str):
        if not self.supabase or not cat or amt <= 0:
            return False
        
        try:
            data = {
                "user_email": user,
                "category": cat,
                "amount": float(amt),
                "date": dt_str
            }
            result = self.supabase.table("expenses").insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Error adding expense: {str(e)}")
            return False

    def get_expenses(self, user, year_month=None):
        if not self.supabase:
            return []
        
        try:
            query = self.supabase.table("expenses").select("*").eq("user_email", user)
            
            if year_month:
                # Filter by year-month (e.g., "2025-01")
                start_date = f"{year_month}-01"
                # Get last day of month
                if year_month.endswith(('01', '03', '05', '07', '08', '10', '12')):
                    end_date = f"{year_month}-31"
                elif year_month.endswith(('04', '06', '09', '11')):
                    end_date = f"{year_month}-30"
                else:  # February
                    end_date = f"{year_month}-29"
                
                query = query.gte("date", start_date).lte("date", end_date)
            
            result = query.order("date", desc=True).execute()
            
            # Convert to the format expected by your app (user, category, amount, date)
            expenses = []
            for row in result.data:
                expenses.append((
                    row['user_email'],
                    row['category'],
                    row['amount'],
                    row['date']
                ))
            return expenses
        except Exception as e:
            st.error(f"Error fetching expenses: {str(e)}")
            return []

    def delete_expense(self, user, expense_id):
        if not self.supabase:
            return False
        
        try:
            result = self.supabase.table("expenses").delete().eq("id", expense_id).eq("user_email", user).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting expense: {str(e)}")
            return False

    def reset_current_month(self, user):
        if not self.supabase:
            return False
        
        current_month = datetime.now().strftime("%Y-%m")
        try:
            start_date = f"{current_month}-01"
            end_date = f"{current_month}-31"
            result = self.supabase.table("expenses").delete().eq("user_email", user).gte("date", start_date).lte("date", end_date).execute()
            return True
        except Exception as e:
            st.error(f"Error resetting current month: {str(e)}")
            return False

    def delete_all_user_data(self, user):
        if not self.supabase:
            return False
        
        try:
            result = self.supabase.table("expenses").delete().eq("user_email", user).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting all expenses: {str(e)}")
            return False

class IncomeManager:
    def __init__(self):
        self.supabase = supabase

    def add_income(self, user, amt, dt_str):
        if not self.supabase or amt <= 0:
            return False
        
        try:
            data = {
                "user_email": user,
                "amount": float(amt),
                "date": dt_str
            }
            result = self.supabase.table("income").insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Error adding income: {str(e)}")
            return False

    def get_income(self, user, year_month=None):
        if not self.supabase:
            return []
        
        try:
            query = self.supabase.table("income").select("*").eq("user_email", user)
            
            if year_month:
                start_date = f"{year_month}-01"
                if year_month.endswith(('01', '03', '05', '07', '08', '10', '12')):
                    end_date = f"{year_month}-31"
                elif year_month.endswith(('04', '06', '09', '11')):
                    end_date = f"{year_month}-30"
                else:
                    end_date = f"{year_month}-29"
                
                query = query.gte("date", start_date).lte("date", end_date)
            
            result = query.order("date", desc=True).execute()
            
            # Convert to expected format (user, amount, date)
            income = []
            for row in result.data:
                income.append((
                    row['user_email'],
                    row['amount'],
                    row['date']
                ))
            return income
        except Exception as e:
            st.error(f"Error fetching income: {str(e)}")
            return []

    def delete_income(self, user, income_id):
        if not self.supabase:
            return False
        
        try:
            result = self.supabase.table("income").delete().eq("id", income_id).eq("user_email", user).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting income: {str(e)}")
            return False

    def reset_current_month(self, user):
        if not self.supabase:
            return False
        
        current_month = datetime.now().strftime("%Y-%m")
        try:
            start_date = f"{current_month}-01"
            end_date = f"{current_month}-31"
            result = self.supabase.table("income").delete().eq("user_email", user).gte("date", start_date).lte("date", end_date).execute()
            return True
        except Exception as e:
            st.error(f"Error resetting current month income: {str(e)}")
            return False

    def delete_all_user_data(self, user):
        if not self.supabase:
            return False
        
        try:
            result = self.supabase.table("income").delete().eq("user_email", user).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting all income: {str(e)}")
            return False

class SpendingAnalyzer:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        
    def detect_spending_patterns(self, user):
        if not self.supabase:
            return self._empty_patterns()
        
        try:
            result = self.supabase.table("expenses").select("*").eq("user_email", user).execute()
            expenses = result.data
            
            if not expenses:
                return self._empty_patterns()
            
            df = pd.DataFrame(expenses)
            df['date'] = pd.to_datetime(df['date'])
            df['day_of_week'] = df['date'].dt.dayofweek
            
            patterns = {
                'peak_spending_day': df.groupby('day_of_week')['amount'].sum().idxmax(),
                'avg_daily_spend': df.groupby(df['date'].dt.date)['amount'].sum().mean(),
                'top_category': df.groupby('category')['amount'].sum().idxmax(),
                'spending_trend': self._calculate_trend(df),
                'unusual_expenses': self._detect_anomalies(df)
            }
            return patterns
        except Exception as e:
            st.error(f"Error analyzing spending patterns: {str(e)}")
            return self._empty_patterns()
    
    def _empty_patterns(self):
        return {
            'peak_spending_day': 'N/A',
            'avg_daily_spend': 0,
            'top_category': 'N/A',
            'spending_trend': 1,
            'unusual_expenses': []
        }
    
    def _calculate_trend(self, data):
        if len(data) < 2:
            return 1
        recent = data.tail(len(data)//2)['amount'].mean()
        older = data.head(len(data)//2)['amount'].mean()
        return recent / older if older > 0 else 1
    
    def _detect_anomalies(self, data):
        if len(data) < 3:
            return []
        
        category_means = data.groupby('category')['amount'].mean()
        category_stds = data.groupby('category')['amount'].std()
        
        anomalies = []
        for _, row in data.iterrows():
            std = category_stds[row['category']]
            if std > 0:
                z_score = (row['amount'] - category_means[row['category']]) / std
                if abs(z_score) > 2:
                    anomalies.append({
                        'date': row['date'].strftime('%Y-%m-%d'),
                        'category': row['category'],
                        'amount': row['amount'],
                        'severity': 'high' if abs(z_score) > 3 else 'medium'
                    })
        return anomalies
