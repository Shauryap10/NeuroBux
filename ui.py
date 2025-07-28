import streamlit as st
from auth import AuthManager
from database import ExpenseManager, IncomeManager, init_supabase
from synbot import SynBot
from pages import login, dashboard, add_transaction, view_expenses, markets, ai_coach, smart_analytics
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="NeuroBux - AI Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Initialize Supabase and managers
supabase = init_supabase()

if not supabase:
    st.error("❌ Database connection failed. Please check your Supabase configuration.")
    st.info("Contact support if this issue persists.")
    st.stop()

# Initialize managers with Supabase
auth = AuthManager(supabase)  # ✅ Updated: Pass supabase client to auth manager
exp_mgr = ExpenseManager()
inc_mgr = IncomeManager()
synbot = SynBot()

# Page navigation
pages = {
    "🏠 Dashboard": lambda: dashboard.dashboard_page(exp_mgr, inc_mgr),
    "➕ Add Transaction": lambda: add_transaction.add_transaction_page(exp_mgr, inc_mgr),
    "📑 View Expenses": lambda: view_expenses.view_expenses_page(exp_mgr, inc_mgr),
    "🧠 Smart Analytics": lambda: smart_analytics.smart_analytics_page(exp_mgr, inc_mgr),
    "📈 Markets": markets.markets_page,
    "💬 AI Coach": lambda: ai_coach.ai_coach_page(exp_mgr, inc_mgr, synbot),
}

def test_database_connection():
    """Test database connection"""
    try:
        if supabase:
            result = supabase.table("expenses").select("count", count="exact").execute()
            return True, f"✅ Database connected! {result.count} expenses in database"
        else:
            return False, "❌ Supabase client not initialized"
    except Exception as e:
        return False, f"❌ Database connection failed: {str(e)}"

def main_app():
    # Custom CSS for better UI
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
        .sidebar-user-info {
            background: rgba(0,122,255,0.1);
            padding: 10px;
            border-radius: 8px;
            margin: 10px 0;
        }
        </style>""", unsafe_allow_html=True)

    # Sidebar user information
    st.sidebar.markdown("## 💰 NeuroBux")
    
    # User info section
    st.sidebar.markdown(f"""
    <div class="sidebar-user-info">
        <p><strong>👤 Logged in as:</strong></p>
        <p>{st.session_state.user_email}</p>
    </div>
    """, unsafe_allow_html=True)

    # Navigation buttons
    st.sidebar.markdown("### 📊 Navigation")
    for label, func in pages.items():
        selected = label == st.session_state.page
        if st.sidebar.button(label, key=label, use_container_width=True):
            st.session_state.page = label

    # Sidebar tools
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛠️ Tools")
    
    # Database test button
    if st.sidebar.button("🔍 Test Database", help="Check database connection status"):
        success, message = test_database_connection()
        if success:
            st.sidebar.success(message)
        else:
            st.sidebar.error(message)
    
    # User info button
    if st.sidebar.button("👤 Account Info"):
        user_info = auth.get_user_info(st.session_state.user_email)
        if user_info:
            st.sidebar.info(f"""
            **Account Details:**
            - Email: {user_info['email']}
            - Member since: {user_info['created_at'][:10]}
            - Last login: {user_info.get('last_login', 'Unknown')[:10] if user_info.get('last_login') else 'First time'}
            """)
    
    # Logout button
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", type="primary", use_container_width=True):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Reset to logged out state
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.page = "🏠 Dashboard"
        
        st.sidebar.success("👋 Successfully logged out!")
        st.rerun()

    # Render the selected page
    try:
        pages[st.session_state.page]()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.info("Please try refreshing the page or contact support.")

# Main application logic
if st.session_state.logged_in:
    main_app()
else:
    login_page(auth)
