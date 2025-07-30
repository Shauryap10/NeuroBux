import streamlit as st
from streamlit_lottie import st_lottie
import json

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

def login_page(auth):
    st.title("💰 Neurobux")

    # Load and display Lottie animation
    lottie_json = load_lottiefile("Wallet-Expense-Icon-Animation-wallet-expense-bank.json")
    st_lottie(lottie_json, speed=1, height=220, key="wallet_animation")

    st.markdown("### AI-powered finance tracker")
    st.markdown("---")

    # Create tabs for Login and Register
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        st.subheader("Welcome Back!")
        st.caption("Access your personal dashboard")

        with st.form("login_form"):
            email = st.text_input(
                "📧 Email Address", 
                placeholder="your.email@example.com",
                help="Enter the email address you registered with"
            )
            password = st.text_input(
                "🔒 Password", 
                type="password",
                placeholder="Enter your password",
                help="Your account password"
            )

            col1, col2 = st.columns([1,1])
            with col1:
                login_button = st.form_submit_button("🚀 Login", use_container_width=True)
            with col2:
                forgot_password = st.form_submit_button("❓ Forgot Password?", use_container_width=True)

            if login_button:
                if email and password:
                    with st.spinner("Authenticating..."):
                        success, message = auth.login(email, password)
                    if success:
                        st.success("🎉 " + message)
                        st.session_state.logged_in = True
                        st.session_state.user_email = email.lower().strip()
                        st.session_state.page = "🏠 Dashboard"
                        st.balloons()
                        with st.container():
                            st.info("Welcome back! Redirecting to your dashboard...")
                        st.experimental_rerun()
                    else:
                        st.error("❌ " + message)
                        if "Invalid email or password" in message:
                            st.warning(
                                "💡 Tips:\n- Check your email spelling\n- Ensure caps lock is off\n- Try registering if you don't have an account"
                            )
                else:
                    st.error("❌ Please enter both email and password")

            if forgot_password:
                st.info(
                    "For password reset, please contact support at support@neurobux.com."
                )

    with tab2:
        st.subheader("Create Your Account")
        st.caption("Join thousands of users managing their finances")

        with st.form("register_form"):
            reg_email = st.text_input(
                "📧 Email Address",
                placeholder="your.email@example.com",
                key="reg_email",
                help="This email will be your login ID"
            )
            col1, col2 = st.columns([1,1])
            with col1:
                reg_password = st.text_input(
                    "🔒 Password",
                    type="password",
                    placeholder="Create a strong password",
                    key="reg_password",
                    help="Min 6 characters with letters and numbers"
                )
            with col2:
                confirm_password = st.text_input(
                    "🔒 Confirm Password",
                    type="password",
                    placeholder="Re-enter your password",
                    key="confirm_password",
                    help="Must match the password above"
                )
            # Password requirements info
            st.info("Password must be at least 6 characters long with letters and numbers.")

            terms_agreed = st.checkbox(
                "I agree to the Terms of Service and Privacy Policy",
                help="Required to create an account"
            )

            register_button = st.form_submit_button("🎉 Register", use_container_width=True)

            if register_button:
                if not terms_agreed:
                    st.error("You must agree to the Terms of Service and Privacy Policy.")
                elif reg_email and reg_password and confirm_password:
                    with st.spinner("Creating your account..."):
                        success, message = auth.register(reg_email, reg_password, confirm_password)
                    if success:
                        st.success("🎉 " + message)
                        st.info("You can now login using your credentials.")
                    else:
                        st.error("❌ " + message)
                        if "already exists" in message:
                            st.info("If you already have an account, switch to the Login tab.")
                else:
                    st.error("Please fill out all fields to register.")

    # Features section to showcase app benefits
    st.markdown("---")
    st.markdown("### Why Choose Neurobux?")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(
            """
            **🤖 AI-Powered Insights**  
            Smart expense analysis, personalized recommendations
            """
        )
    with col2:
        st.info(
            """
            **📊 Comprehensive Tracking**  
            Manage income, expenses & visualize data with charts
            """
        )
    with col3:
        st.info(
            """
            **🔒 Secure & Private**  
            Encrypted data storage, privacy first design
            """
        )

    # Footer
    st.markdown("---")
    st.caption("© 2025 Neurobux - Your AI-powered finance tracker")
