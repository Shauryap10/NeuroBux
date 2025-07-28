import streamlit as st

def login_page(auth):
    st.title("💰 NeuroBux")
    st.markdown("### AI-powered finance tracker")

    col1, col2 = st.columns(2)

    with col1:
        with st.form("login"):
            email = st.text_input("📧 Email")
            pwd = st.text_input("🔒 Password", type="password")
            if st.form_submit_button("Login"):
                if auth.login(email, pwd):
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.session_state.page = "🏠 Dashboard"
                    st.rerun()  # ✅ UPDATED: Changed from st.experimental_rerun()
                else:
                    st.error("Invalid credentials")

    with col2:
        with st.form("register"):
            new_email = st.text_input("📧 New Email")
            new_pwd = st.text_input("🔐 New Password", type="password")
            if st.form_submit_button("Register"):
                if auth.register(new_email, new_pwd):
                    st.success("Registered! Please log in.")
                else:
                    st.error("User already exists")
