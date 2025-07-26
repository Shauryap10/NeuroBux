import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import SpendingAnalyzer
from synbot import SmartBudgetAdvisor

def smart_analytics_page(exp_mgr, inc_mgr):
    st.header("🧠 Smart Budget Analytics")
    
    # Initialize analyzer
    analyzer = SpendingAnalyzer(exp_mgr.conn)
    advisor = SmartBudgetAdvisor(analyzer)
    
    # Get user data
    user = st.session_state.user_email
    patterns = analyzer.detect_spending_patterns(user)
    insights = advisor.generate_budget_insights(None, patterns)
    
    # Display insights cards
    st.subheader("💡 Personalized Insights")
    
    for insight in insights:
        if insight['type'] == 'warning':
            st.warning(f"**{insight['message']}**\n\n💡 {insight['suggestion']}")
        elif insight['type'] == 'alert':
            st.error(f"**{insight['message']}**\n\n💡 {insight['suggestion']}")
        else:
            st.info(f"**{insight['message']}**\n\n💡 {insight['suggestion']}")
    
    # Spending Pattern Visualization
    st.subheader("📊 Spending Pattern Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Peak spending day chart
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        exp_data = exp_mgr.get_expenses(user)
        if exp_data:
            df = pd.DataFrame(exp_data, columns=["User", "Category", "Amount", "Date"])
            df['Date'] = pd.to_datetime(df['Date'])
            df['DayOfWeek'] = df['Date'].dt.day_name()
            
            daily_spending = df.groupby('DayOfWeek')['Amount'].sum().reindex(days, fill_value=0)
            
            fig = px.bar(
                x=daily_spending.index, 
                y=daily_spending.values,
                title="Spending by Day of Week",
                color=daily_spending.values,
                color_continuous_scale="viridis"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category spending trend
        if exp_data:
            category_spending = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
            
            fig = px.pie(
                values=category_spending.values,
                names=category_spending.index,
                title="Spending Distribution by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Anomaly Detection Section
    if patterns['unusual_expenses']:
        st.subheader("🔍 Unusual Expenses Detected")
        
        anomaly_df = pd.DataFrame(patterns['unusual_expenses'])
        st.dataframe(
            anomaly_df.style.format({'amount': '₹{:.2f}'})
        )
        
        st.info("💡 These expenses are significantly different from your usual spending in these categories.")
    
    # Predictive Budget Forecast
    st.subheader("🔮 Monthly Budget Forecast")
    
    if exp_data:
        # Simple forecast based on current month's spending rate
        current_month = datetime.now().strftime("%Y-%m")
        current_day = datetime.now().day
        days_in_month = 30  # Simplified
        
        current_month_expenses = [e for e in exp_data if e[3].startswith(current_month)]
        current_spending = sum(e[2] for e in current_month_expenses)
        
        if current_day > 0:
            predicted_monthly = (current_spending / current_day) * days_in_month
        else:
            predicted_monthly = 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Month Spend", f"₹{current_spending:,.2f}")
        col2.metric("Predicted Month Total", f"₹{predicted_monthly:,.2f}")
        col3.metric("Daily Average", f"₹{current_spending/max(current_day, 1):,.2f}")
        
        # Progress bar for month
        progress = min(current_spending / predicted_monthly, 1.0) if predicted_monthly > 0 else 0
        st.progress(progress)
        st.caption(f"Month Progress: {current_day}/{days_in_month} days")
    else:
        st.info("No expense data available for analysis.")
