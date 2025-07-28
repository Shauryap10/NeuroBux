import streamlit as st

def login_page(auth):
    st.title("💰 NeuroBux")
    st.markdown("### AI-powered finance tracker")
    st.markdown("---")

    # Create tabs for Login and Register
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        st.subheader("Welcome Back!")
        st.caption("Access your personal finance dashboard")
        
        with st.form("login_form"):
            email = st.text_input(
                "📧 Email Address", 
                placeholder="your.email@example.com",
                help="Enter the email address you used to register"
            )
            password = st.text_input(
                "🔒 Password", 
                type="password", 
                placeholder="Enter your password",
                help="Enter your account password"
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                login_button = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
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
                        
                        # Add welcome message
                        with st.container():
                            st.info(f"Welcome back! Redirecting to your dashboard...")
                        
                        st.rerun()
                    else:
                        st.error("❌ " + message)
                        if "Invalid email or password" in message:
                            st.warning("💡 **Tips:**\n- Check your email spelling\n- Ensure caps lock is off\n- Try registering if you don't have an account")
                else:
                    st.error("❌ Please enter both email and password")
            
            if forgot_password:
                st.info("📧 **Password Reset:**\nContact support at support@neurobux.com or register a new account if you've forgotten your credentials.")

    with tab2:
        st.subheader("Create Your Account")
        st.caption("Join thousands of users managing their finances with AI")
        
        with st.form("register_form"):
            reg_email = st.text_input(
                "📧 Email Address", 
                placeholder="your.email@example.com", 
                key="reg_email",
                help="We'll use this email for your account login"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                reg_password = st.text_input(
                    "🔒 Password", 
                    type="password", 
                    placeholder="Create a secure password", 
                    key="reg_password",
                    help="Minimum 6 characters with letters and numbers"
                )
            with col2:
                confirm_password = st.text_input(
                    "🔒 Confirm Password", 
                    type="password", 
                    placeholder="Confirm your password", 
                    key="confirm_password",
                    help="Re-enter your password to confirm"
                )
            
            # Password requirements info - FIXED
            st.info("**Password Requirements:** At least 6 characters with letters and numbers")
            
            terms_agreed = st.checkbox(
                "I agree to the Terms of Service and Privacy Policy",
                help="By checking this box, you agree to our terms and conditions"
            )
            
            register_button = st.form_submit_button("🎉 Create Account", type="primary", use_container_width=True)

            if register_button:
                if not terms_agreed:
                    st.error("❌ Please agree to the Terms of Service to continue")
                elif reg_email and reg_password and confirm_password:
                    with st.spinner("Creating your account..."):
                        success, message = auth.register(reg_email, reg_password, confirm_password)
                    
                    if success:
                        st.success("🎉 " + message)
                        st.success("🎯 **Next Steps:**\n1. Switch to the Login tab\n2. Enter your email and password\n3. Start tracking your finances!")
                        st.balloons()
                    else:
                        st.error("❌ " + message)
                        if "already exists" in message:
                            st.info("💡 **Already have an account?** Switch to the Login tab to sign in.")
                else:
                    st.error("❌ Please fill in all required fields")

    # App features section
    st.markdown("---")
    st.markdown("### 🌟 Why Choose NeuroBux?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**🤖 AI-Powered Insights**\n- Smart spending analysis\n- Personalized financial advice\n- Automated categorization")
    
    with col2:
        st.info("**📊 Comprehensive Tracking**\n- Income & expense management\n- Visual charts & reports\n- Export capabilities")
    
    with col3:
        st.info("**🔒 Secure & Private**\n- Bank-level security\n- Encrypted data storage\n- Privacy-focused design")

    # Footer
    st.markdown("---")
    st.caption("🔒 Your financial data is encrypted and secure | 📱 Access anywhere, anytime | 🤖 AI-powered insights")
    st.caption("© 2025 NeuroBux - Smart Finance Tracking")
