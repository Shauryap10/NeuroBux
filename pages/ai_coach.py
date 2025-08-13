import streamlit as st
import pandas as pd
from database import SpendingAnalyzer

def ai_coach_page(exp_mgr, inc_mgr, synbot):
    st.header(" NeuroBot ")
    st.markdown("*Get personalized financial advice based on your spending and income data*")

    # Get user's financial data
    exp_data = exp_mgr.get_expenses(st.session_state.user_email)
    inc_data = inc_mgr.get_income(st.session_state.user_email)

    df_exp = pd.DataFrame(exp_data, columns=["User", "Category", "Amount", "Date"])
    df_inc = pd.DataFrame(inc_data, columns=["User", "Amount", "Date"])

    if df_exp.empty:
        df_exp = pd.DataFrame(columns=["User", "Category", "Amount", "Date"])
    if df_inc.empty:
        df_inc = pd.DataFrame(columns=["User", "Amount", "Date"])

    # Get analytics data for enhanced context
    analytics_data = None
    if not df_exp.empty:
        try:
            analyzer = SpendingAnalyzer(exp_mgr.conn)
            patterns = analyzer.detect_spending_patterns(st.session_state.user_email)
            analytics_data = {
                'peak_day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][patterns.get('peak_spending_day', 0)],
                'trend': patterns.get('spending_trend', 1),
                'top_category': patterns.get('top_category', 'miscellaneous')
            }
        except Exception:
            analytics_data = None

    # Financial summary display
    if not df_exp.empty or not df_inc.empty:
        st.subheader("📊 Your Financial Summary")
        col1, col2, col3 = st.columns(3)
        
        total_spent = df_exp["Amount"].sum() if not df_exp.empty else 0
        total_income = df_inc["Amount"].sum() if not df_inc.empty else 0
        net_balance = total_income - total_spent
        
        col1.metric("💸 Total Expenses", f"₹{total_spent:,.2f}")
        col2.metric("💰 Total Income", f"₹{total_income:,.2f}")
        col3.metric("📈 Net Balance", f"₹{net_balance:,.2f}", 
                   delta=f"{'Surplus' if net_balance >= 0 else 'Deficit'}")
        
        st.markdown("---")

    # Suggested questions for users
    st.subheader("💡 Suggested Questions")
    suggestion_cols = st.columns(2)
    
    with suggestion_cols[0]:
        if st.button("📊 Analyze my spending patterns", key="analyze_spending"):
            if not df_exp.empty:
                suggested_question = "Can you analyze my spending patterns and give me insights on how to improve my budget?"
                st.session_state.suggested_question = suggested_question
            else:
                st.info("Add some expenses first to get spending analysis!")
        
        if st.button("💰 How can I save more money?", key="save_money"):
            st.session_state.suggested_question = "Based on my spending, what are the best ways I can save more money?"
    
    with suggestion_cols[1]:
        if st.button("🎯 Help me set financial goals", key="financial_goals"):
            st.session_state.suggested_question = "Can you help me set realistic financial goals based on my income and expenses?"
        
        if st.button("📈 Investment advice for beginners", key="investment_advice"):
            st.session_state.suggested_question = "I'm new to investing. What should I know and how much should I invest based on my finances?"

    st.markdown("---")

    # Chat interface
    st.subheader("💬 Chat with NeuroBot")
    
    # Initialize messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        welcome_msg = """👋 Hello! I'm NeuroBot, your personal financial coach. I'm here to help you understand your spending habits, create better budgets, and achieve your financial goals.

I can analyze your expense and income data to provide personalized advice. Feel free to ask me anything about:
• Budgeting and expense management
• Saving strategies and tips
• Financial planning and goal setting
• Investment basics
• Debt management

What would you like to know about your finances today?"""
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle suggested questions
    if hasattr(st.session_state, 'suggested_question'):
        prompt = st.session_state.suggested_question
        delattr(st.session_state, 'suggested_question')
    else:
        prompt = st.chat_input("Ask me anything about your finances...")

    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response with enhanced context
        with st.chat_message("assistant"):
            with st.spinner("SynBot is analyzing your financial data..."):
                answer = synbot.answer(prompt, df_exp, df_inc, analytics_data)
                st.markdown(answer)
                
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})

    # Quick actions sidebar
    with st.sidebar:
        st.markdown("### 🎯 Quick Actions")
        
        if st.button("🔄 Clear Chat History", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()  # ✅ UPDATED: Changed from st.experimental_rerun()
        
        if st.button("📤 Export Chat", key="export_chat"):
            if st.session_state.messages:
                chat_content = ""
                for msg in st.session_state.messages:
                    role = "You" if msg["role"] == "user" else "SynBot"
                    chat_content += f"{role}: {msg['content']}\n\n"
                
                st.download_button(
                    "💾 Download Chat History",
                    data=chat_content.encode('utf-8'),
                    file_name=f"synbot_chat_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

