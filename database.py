import sqlite3
import pandas as pd
from datetime import datetime

conn = sqlite3.connect("expenses.db", check_same_thread=False)

class ExpenseManager:
    def __init__(self):
        self.conn = conn
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                user TEXT, category TEXT, amount REAL, date TEXT
            )
        ''')
        self.conn.commit()

    def add_expense(self, user, cat, amt, dt_str):
        if cat and amt > 0:
            self.conn.execute("INSERT INTO expenses VALUES (?,?,?,?)", (user, cat, amt, dt_str))
            self.conn.commit()

    def get_expenses(self, user, year_month=None):
        if year_month:
            like_pattern = f"{year_month}%"
            return self.conn.execute(
                "SELECT * FROM expenses WHERE user=? AND date LIKE ?", (user, like_pattern)
            ).fetchall()
        else:
            return self.conn.execute("SELECT * FROM expenses WHERE user=?", (user,)).fetchall()

    def delete_expense(self, user, idx):
        rows = self.conn.execute("SELECT rowid,* FROM expenses WHERE user=?", (user,)).fetchall()
        if 0 <= idx < len(rows):
            rid = rows[idx][0]
            self.conn.execute("DELETE FROM expenses WHERE rowid=?", (rid,))
            self.conn.commit()

    def reset_current_month(self, user):
        """Reset only current month's data"""
        current_month = datetime.now().strftime("%Y-%m")
        like_pattern = f"{current_month}%"
        self.conn.execute("DELETE FROM expenses WHERE user=? AND date LIKE ?", (user, like_pattern))
        self.conn.commit()
    
    def delete_all_user_data(self, user):
        """Delete ALL expense data for user (permanent)"""
        self.conn.execute("DELETE FROM expenses WHERE user=?", (user,))
        self.conn.commit()

class IncomeManager:
    def __init__(self):
        self.conn = conn
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS income (
                user TEXT, amount REAL, date TEXT
            )
        ''')
        self.conn.commit()

    def add_income(self, user, amt, dt_str):
        if amt > 0:
            self.conn.execute("INSERT INTO income VALUES (?,?,?)", (user, amt, dt_str))
            self.conn.commit()

    def get_income(self, user, year_month=None):
        if year_month:
            like_pattern = f"{year_month}%"
            return self.conn.execute(
                "SELECT * FROM income WHERE user=? AND date LIKE ?", (user, like_pattern)
            ).fetchall()
        else:
            return self.conn.execute("SELECT * FROM income WHERE user=?", (user,)).fetchall()

    def delete_income(self, user, idx):
        rows = self.conn.execute("SELECT rowid,* FROM income WHERE user=?", (user,)).fetchall()
        if 0 <= idx < len(rows):
            rid = rows[idx][0]
            self.conn.execute("DELETE FROM income WHERE rowid=?", (rid,))
            self.conn.commit()

    def reset_current_month(self, user):
        """Reset only current month's income data"""
        current_month = datetime.now().strftime("%Y-%m")
        like_pattern = f"{current_month}%"
        self.conn.execute("DELETE FROM income WHERE user=? AND date LIKE ?", (user, like_pattern))
        self.conn.commit()
    
    def delete_all_user_data(self, user):
        """Delete ALL income data for user (permanent)"""
        self.conn.execute("DELETE FROM income WHERE user=?", (user,))
        self.conn.commit()

class SpendingAnalyzer:
    def __init__(self, connection):
        self.conn = connection
        
    def detect_spending_patterns(self, user):
        """Analyze user spending patterns and detect anomalies"""
        expenses = self.conn.execute("SELECT * FROM expenses WHERE user=?", (user,)).fetchall()
        if not expenses:
            return {
                'peak_spending_day': 'N/A',
                'avg_daily_spend': 0,
                'top_category': 'N/A',
                'spending_trend': 1,
                'unusual_expenses': []
            }
        
        df = pd.DataFrame(expenses, columns=['user', 'category', 'amount', 'date'])
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
    
    def _calculate_trend(self, data):
        """Calculate spending trend"""
        if len(data) < 2:
            return 1
        recent = data.tail(len(data)//2)['amount'].mean()
        older = data.head(len(data)//2)['amount'].mean()
        return recent / older if older > 0 else 1
    
    def _detect_anomalies(self, data):
        """Detect unusual spending using statistical methods"""
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
