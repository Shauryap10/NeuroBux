import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import SpendingAnalyzer
from synbot import SmartBudgetAdvisor

def smart_analytics_page(exp_mgr, inc_mgr):
    st.header("Smart Budget Analytics")
    
    # Initialize analyzer with Supabase client (updated from SQLite conn)
    analyzer = SpendingAnalyzer(exp_mgr.supabase)  # ✅ Changed from exp_mgr.conn
    advisor = SmartBudgetAdvisor(analyzer)
    
    # Get user data
    user = st.session_state.user_email
    patterns = analyzer.detect_spending_patterns(user)
    insights = advisor.generate_budget_insights(None, patterns)
    
    # Connection status check
    if not exp_mgr.supabase:
        st.error("❌ Database connection unavailable. Please check your Supabase configuration.")
        return
    
    # Display insights cards
    st.subheader("💡 Personalized Insights")
    
    if insights:
        for insight in insights:
            if insight['type'] == 'warning':
                st.warning(f"**{insight['message']}**\n\n💡 {insight['suggestion']}")
            elif insight['type'] == 'alert':
                st.error(f"**{insight['message']}**\n\n💡 {insight['suggestion']}")
            elif insight['type'] == 'positive':
                st.success(f"**{insight['message']}**\n\n💡 {insight['suggestion']}")
            else:
                st.info(f"**{insight['message']}**\n\n💡 {insight['suggestion']}")
    else:
        st.info("🔍 Add more expenses to generate personalized insights!")
    
    # Spending Pattern Visualization
    st.subheader("📊 Spending Pattern Analysis")
    
    # Get expense data directly from Supabase
    try:
        expense_result = exp_mgr.supabase.table("expenses").select("*").eq("user_email", user).execute()
        exp_data = expense_result.data
        
        if exp_data:
            df = pd.DataFrame(exp_data)
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = df['amount'].astype(float)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Peak spending day chart
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                df['day_name'] = df['date'].dt.day_name()
                
                daily_spending = df.groupby('day_name')['amount'].sum().reindex(days, fill_value=0)
                
                fig = px.bar(
                    x=daily_spending.index, 
                    y=daily_spending.values,
                    title="💳 Spending by Day of Week",
                    color=daily_spending.values,
                    color_continuous_scale="viridis",
                    labels={'x': 'Day', 'y': 'Amount (₹)'}
                )
                fig.update_layout(
                    template="plotly_dark",
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Category spending pie chart
                category_spending = df.groupby('category')['amount'].sum().sort_values(ascending=False)
                
                fig = px.pie(
                    values=category_spending.values,
                    names=category_spending.index,
                    title="🏷️ Spending Distribution by Category"
                )
                fig.update_layout(
                    template="plotly_dark",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Monthly spending trend
            st.subheader("📈 Monthly Spending Trends")
            df['month_year'] = df['date'].dt.to_period('M').astype(str)
            monthly_spending = df.groupby('month_year')['amount'].sum().sort_index()
            
            if len(monthly_spending) > 1:
                fig = px.line(
                    x=monthly_spending.index,
                    y=monthly_spending.values,
                    title="📊 Monthly Spending Trend",
                    markers=True
                )
                fig.update_layout(
                    template="plotly_dark",
                    height=400,
                    xaxis_title="Month",
                    yaxis_title="Amount (₹)"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📅 Add expenses from multiple months to see spending trends")
            
            # Top spending categories
            st.subheader("🔝 Top Spending Categories")
            top_categories = df.groupby('category')['amount'].sum().sort_values(ascending=False).head(10)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(
                    x=top_categories.values,
                    y=top_categories.index,
                    orientation='h',
                    title="💰 Top 10 Categories by Spending",
                    color=top_categories.values,
                    color_continuous_scale="reds"
                )
                fig.update_layout(
                    template="plotly_dark",
                    height=400,
                    xaxis_title="Amount (₹)",
                    yaxis_title="Category"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 📋 Category Summary")
                for idx, (category, amount) in enumerate(top_categories.head(5).items(), 1):
                    percentage = (amount / top_categories.sum()) * 100
                    st.metric(
                        f"{idx}. {category}",
                        f"₹{amount:,.2f}",
                        f"{percentage:.1f}% of total"
                    )
        
        else:
            st.info("📝 No expense data available for analysis. Start by adding some expenses!")
            
    except Exception as e:
        st.error(f"Error loading expense data: {str(e)}")
    
    # Anomaly Detection Section
    if patterns['unusual_expenses']:
        st.subheader("🔍 Unusual Expenses Detected")
        
        anomaly_df = pd.DataFrame(patterns['unusual_expenses'])
        
        # Display anomalies in a nice format
        for _, anomaly in anomaly_df.iterrows():
            severity_color = "🔴" if anomaly['severity'] == 'high' else "🟡"
            st.warning(f"""
            {severity_color} **Unusual Expense Alert**
            - **Date:** {anomaly['date']}
            - **Category:** {anomaly['category']}
            - **Amount:** ₹{anomaly['amount']:,.2f}
            - **Severity:** {anomaly['severity'].upper()}
            """)
        
        st.info("💡 These expenses are significantly different from your usual spending in these categories. Review them to ensure accuracy.")
    
    # Predictive Budget Forecast
    st.subheader("🔮 Monthly Budget Forecast")
    
    try:
        # Get current month expenses from Supabase
        current_month = datetime.now().strftime("%Y-%m")
        current_day = datetime.now().day
        days_in_month = 30  # Simplified
        
        current_month_result = exp_mgr.supabase.table("expenses").select("amount").eq("user_email", user).gte("date", f"{current_month}-01").lte("date", f"{current_month}-31").execute()
        current_month_expenses = current_month_result.data
        
        if current_month_expenses:
            current_spending = sum(expense['amount'] for expense in current_month_expenses)
            
            if current_day > 0:
                predicted_monthly = (current_spending / current_day) * days_in_month
                daily_average = current_spending / current_day
            else:
                predicted_monthly = 0
                daily_average = 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("📊 Current Month Spend", f"₹{current_spending:,.2f}")
            col2.metric("🎯 Predicted Month Total", f"₹{predicted_monthly:,.2f}")
            col3.metric("📅 Daily Average", f"₹{daily_average:,.2f}")
            
            # Progress bar for month
            progress = min(current_spending / predicted_monthly, 1.0) if predicted_monthly > 0 else 0
            st.progress(progress)
            st.caption(f"Month Progress: {current_day}/{days_in_month} days ({(current_day/days_in_month)*100:.1f}%)")
            
            # Budget recommendations
            if predicted_monthly > 0:
                st.subheader("💡 Budget Recommendations")
                
                # Calculate recommended daily budget for rest of month
                remaining_days = days_in_month - current_day
                if remaining_days > 0:
                    recommended_daily = predicted_monthly / days_in_month
                    st.info(f"""
                    **Recommended Actions:**
                    - 📈 **Predicted monthly spending:** ₹{predicted_monthly:,.2f}
                    - 💰 **Recommended daily budget:** ₹{recommended_daily:,.2f}
                    - 📆 **Days remaining:** {remaining_days}
                    - 🎯 **Suggested daily limit:** ₹{(predicted_monthly - current_spending) / max(remaining_days, 1):,.2f}
                    """)
        else:
            st.info("📝 No expenses recorded for the current month yet.")
            
    except Exception as e:
        st.error(f"Error generating forecast: {str(e)}")
    
    # Savings Goal Tracker
    st.subheader("🎯 Savings Goal Tracker")
    
    try:
        # Get income data from Supabase
        income_result = inc_mgr.supabase.table("income").select("amount").eq("user_email", user).execute()
        income_data = income_result.data
        
        total_income = sum(income['amount'] for income in income_data) if income_data else 0
        total_expenses = sum(expense['amount'] for expense in exp_data) if exp_data else 0
        
        if total_income > 0:
            savings_rate = ((total_income - total_expenses) / total_income) * 100
            col1, col2, col3 = st.columns(3)
            
            col1.metric("💰 Total Income", f"₹{total_income:,.2f}")
            col2.metric("💸 Total Expenses", f"₹{total_expenses:,.2f}")
            col3.metric("📈 Savings Rate", f"{savings_rate:.1f}%")
            
            # Savings rate visualization
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = savings_rate,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Savings Rate (%)"},
                delta = {'reference': 20},  # Recommended 20% savings rate
                gauge = {
                    'axis': {'range': [None, 50]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 10], 'color': "lightgray"},
                        {'range': [10, 20], 'color': "yellow"},
                        {'range': [20, 50], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 20
                    }
                }
            ))
            fig.update_layout(
                template="plotly_dark",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Savings recommendations
            if savings_rate < 10:
                st.error("🚨 **Low Savings Rate!** Try to save at least 10% of your income.")
            elif savings_rate < 20:
                st.warning("⚠️ **Good but can improve!** Aim for 20% savings rate.")
            else:
                st.success("🎉 **Excellent savings rate!** You're on track for financial success.")
        else:
            st.info("💡 Add income data to track your savings rate.")
            
    except Exception as e:
        st.error(f"Error calculating savings: {str(e)}")
    
    # Quick Stats Summary
    st.markdown("---")
    st.subheader("📋 Quick Statistics")
    
    if exp_data:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_transaction = df['amount'].mean()
            st.metric("💳 Avg Transaction", f"₹{avg_transaction:.2f}")
        
        with col2:
            total_transactions = len(df)
            st.metric("📊 Total Transactions", f"{total_transactions:,}")
        
        with col3:
            max_expense = df['amount'].max()
            st.metric("📈 Largest Expense", f"₹{max_expense:,.2f}")
        
        with col4:
            unique_categories = df['category'].nunique()
            st.metric("🏷️ Categories Used", f"{unique_categories}")
    
    # Export Analytics Data
    st.markdown("---")
    if st.button("📊 Export Analytics Report", type="primary"):
        if exp_data:
            analytics_report = {
                "user_email": user,
                "generated_at": datetime.now().isoformat(),
                "spending_patterns": patterns,
                "total_expenses": sum(expense['amount'] for expense in exp_data),
                "total_income": sum(income['amount'] for income in income_data) if income_data else 0,
                "insights": insights
            }
            
            report_json = pd.Series(analytics_report).to_json(indent=2)
            st.download_button(
                "💾 Download Analytics Report (JSON)",
                data=report_json.encode('utf-8'),
                file_name=f"neurobux_analytics_{user}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
            st.success("📈 Analytics report ready for download!")
        else:
            st.info("📝 No data available to export.")

