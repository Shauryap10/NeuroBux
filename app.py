import streamlit as st
from auth import AuthManager
from database import ExpenseManager, IncomeManager
from synbot import SynBot
from pages import login, dashboard, add_transaction, view_expenses, markets, ai_coach, smart_analytics
from datetime import datetime

# Initialize session states
for key, default in {
    "logged_in": False, 
    "user_email": "", 
    "page": "🏠 Dashboard", 
    "selected_month": None,
    "confirm_reset_month": False,
    "confirm_delete_all": False,
    "confirm_reset_view": False,
    "confirm_delete_month": False,
    "confirm_delete_all_view": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

auth = AuthManager()
exp_mgr = ExpenseManager()
inc_mgr = IncomeManager()
synbot = SynBot()

pages = {
    "🏠 Dashboard": lambda: dashboard.dashboard_page(exp_mgr, inc_mgr),
    "➕ Add Transaction": lambda: add_transaction.add_transaction_page(exp_mgr, inc_mgr),
    "📑 View Expenses": lambda: view_expenses.view_expenses_page(exp_mgr, inc_mgr),
    "🧠 Smart Analytics": lambda: smart_analytics.smart_analytics_page(exp_mgr, inc_mgr),
    "📈 Markets": markets.markets_page,
    "💬 AI Coach": lambda: ai_coach.ai_coach_page(exp_mgr, inc_mgr, synbot),
}

def main_app():
    # Animated CSS for sidebar nav
    st.markdown("""
        <style>
        .nav-tile {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            margin: 6px 0;
            border-radius: 12px;
            background: rgba(255,255,255,0.08);
            color: #f5f5f7;
            font-size: 15px;
            font-weight: 500;
            transition: all 0.3s ease;
            cursor: pointer;
            border: 1px solid rgba(255,255,255,0.05);
            text-decoration: none;
            user-select: none;
        }
        .nav-tile:hover,
        .nav-tile.selected {
            background: rgba(255,255,255,0.15);
            box-shadow: 0 0 12px rgba(0,122,255,0.4);
            transform: translateY(-2px);
            color: #ffffff;
        }
        </style>""", unsafe_allow_html=True)

    st.sidebar.markdown("## NeuroBux")
    st.sidebar.caption(st.session_state.user_email)

    for label, func in pages.items():
        selected = label == st.session_state.page
        if st.sidebar.button(label, key=label, use_container_width=True):
            st.session_state.page = label

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.page = "🏠 Dashboard"
        st.experimental_rerun()

    # Render the selected page
    pages[st.session_state.page]()

if st.session_state.logged_in:
    main_app()
else:
    login.login_page(auth)