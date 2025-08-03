import streamlit as st
from auth import AuthManager
from database import ExpenseManager, IncomeManager, init_supabase
from synbot import SynBot
from pages.login import login_page
from pages import dashboard, add_transaction, view_expenses, markets, ai_coach, smart_analytics
from datetime import datetime

# ===== THEME & GLOW CSS =====
st.markdown("""
<style>
body, .stApp {background-color: #18192A !important; color: #f5f5f7 !important;}
[data-testid="stSidebar"] {background-color: #23243A !important; color: #f5f5f7 !important;}
/* Glow effect for Neurobux app title and all sidebar nav */
h1, .neurobux-glow {
    color: #26a69a !important;
    text-shadow:
        0 0 5px #26a69a,
        0 0 10px #26a69a,
        0 0 15px #26a69a,
        0 0 25px #ffffff;
}
.stSidebar [data-testid="stSidebarNav"] span,
.stSidebar .sidebar-user-info,
.stSidebar [data-testid="stSidebarNav"] button,
.stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6 {
    color: #26a69a !important;
    text-shadow:
        0 0 6px #26a69a,
        0 0 13px #26a69a,
        0 0 18px #26a69a;
    font-weight: bold !important;
}
.stSidebar * {text-shadow: 0 0 3px #26a69a90, 0 0 7px #26a69a50;}
.stSidebar button, .stSidebar .stButton>button {
    color: #26a69a !important;
    text-shadow: 0 0 5px #26a69a, 0 0 10px #26a69a;
    font-weight: 600 !important;
}
.stSidebar button:hover, .stSidebar .stButton>button:hover {
    filter: brightness(1.15) drop-shadow(0 0 10px #ffffff40);
}
.stButton>button {
    background-color: #26a69a !important;
    color: white !important;
    border-radius: 6px !important;
}
.stButton>button:hover {
    background-color: #1f8e7e !important;
}
/* Custom metric, input, header, and misc style overrides */
.stMetric-label   {color: #bfc8d9 !important;}
.stMetric-value   {color: #f5f5f7 !important;}
.stTextInput>div>div>input {background-color: #23243A !important; color: #f5f5f7 !important; border-radius: 8px !important;}
div[data-testid="stTabs"] > div {background-color: #23243A !important; color: #f5f5f7 !important; border-radius: 10px !important;}
div[data-testid="stTabs"] > div > button {
    color: #bfc8d9 !important; background-color: #23243A !important; border: none !important; font-weight: 600 !important;
}
div[data-testid="stTabs"] > div > button:focus, 
div[data-testid="stTabs"] > div > button:hover, 
div[data-testid="stTabs"] > div > button[aria-selected="true"] {
    color: #26a69a !important; background-color: transparent !important;
}
h1, h2, h3, h4 {color: #26a69a !important; font-weight: 700 !important;}
hr {border-color: #26a69a !important; opacity: 0.2 !important;}
</style>
""", unsafe_allow_html=True)
# ===== END THEME & GLOW CSS =====

# PAGE CONFIG
st.set_page_config(
    page_title="NeuroBux - AI Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === SESSION STATE SETUP ===
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

# === INIT DATABASE + AUTH ===
supabase = init_supabase()
if not supabase:
    st.error("❌ Database connection failed. Please check your Supabase configuration.")
    st.info("Contact support if this issue persists.")
    st.stop()

auth = AuthManager(supabase)
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

def test_database_connection():
    try:
        if supabase:
            result = supabase.table("expenses").select("count", count="exact").execute()
            return True, f"✅ Database connected! {result.count} expenses in database"
        else:
            return False, "❌ Supabase client not initialized"
    except Exception as e:
        return False, f"❌ Database connection failed: {str(e)}"

def main_app():
    # === SIDEBAR: APP TITLE with GLOW ===
    st.sidebar.markdown('<h2 class="neurobux-glow">💰 Neurobux</h2>', unsafe_allow_html=True)

    # === SIDEBAR: USER INFO ===
    st.sidebar.markdown(f"""
    <div class="sidebar-user-info">
        <p><strong>👤 Logged in as:</strong></p>
        <p>{st.session_state.user_email}</p>
    </div>
    """, unsafe_allow_html=True)

    # === SIDEBAR NAVIGATION: GLOW APPLIES AUTOMATICALLY ===
    st.sidebar.markdown("### 📊 Navigation")
    for label, func in pages.items():
        if st.sidebar.button(label, key=label, use_container_width=True):
            st.session_state.page = label

    # === SIDEBAR TOOLS SECTION ===
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛠️ Tools")
    if st.sidebar.button("🔍 Test Database", help="Check database connection status"):
        success, message = test_database_connection()
        if success:
            st.sidebar.success(message)
        else:
            st.sidebar.error(message)
    if st.sidebar.button("👤 Account Info"):
        user_info = auth.get_user_info(st.session_state.user_email)
        if user_info:
            st.sidebar.info(f"""
            **Account Details:**
            - Email: {user_info['email']}
            - Member since: {user_info['created_at'][:10]}
            - Last login: {user_info.get('last_login', 'Unknown')[:10] if user_info.get('last_login') else 'First time'}
            """)

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", type="primary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.page = "🏠 Dashboard"
        st.sidebar.success("👋 Successfully logged out!")
        st.rerun()

    # === MAIN PAGE CONTENT ===
    try:
        pages[st.session_state.page]()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.info("Please try refreshing the page or contact support.")

# === RUN THE APP ===
if st.session_state.logged_in:
    main_app()
else:
    login_page(auth)
