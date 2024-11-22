import streamlit as st
import uuid
from utils.appwrite_client import account



# Now import your modules for pages
from pages import google, market, userdashboard 

# Sidebar for navigation
with st.sidebar:
    st.title("Navigation")

    # Check login status
    if "logged_in" in st.session_state and st.session_state.logged_in:
        # If the user is logged in, show the navigation options
        page = st.selectbox(
            "Choose a page", 
            [
                "Market", 
                "Google News", 
                "Dashboard", 
                
            ]
        )
    else:
        # If the user is not logged in, show login page option
        page = "Login"

# Login/Signup Page Logic
def user_auth_page():
    st.title("User Authentication")

    # Login Section
    st.subheader("Log In")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")

        if submitted:
            try:
                # Email and password-based session creation using Appwrite's login API
                session = account.create_email_password_session(email=email, password=password)
                # Store the session details in session state
                st.session_state.logged_in = True
                st.session_state.user_id = session["$id"]
                st.session_state.email = email
                # Add a username (you might want to fetch this from your user profile)
                st.session_state.username = email.split('@')[0]  # Use part of email as username
                st.success("Logged in successfully!")
                st.rerun()  # Rerun the app to update the page
            except Exception as e:
                st.error(f"Login failed: {e}")

    st.markdown("---")

    # Signup Section
    st.subheader("Sign Up")
    with st.form("signup_form"):
        username = st.text_input("Username")
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        signup_submitted = st.form_submit_button("Sign Up")

        if signup_submitted:
            if new_password != confirm_password:
                st.error("Passwords do not match.")
                return
            try:
                # Generate a random user_id using uuid
                user_id = str(uuid.uuid4())  # Generate a random UUID as user_id
                st.session_state.username = username
                # Create user account via Appwrite's signup API with random user_id
                account.create(user_id=user_id, name=username, email=new_email, password=new_password)
                st.success("Account created successfully! Please log in.")
            except Exception as e:
                st.error(f"Signup failed: {e}")

# Page-specific logic
if page == "Login":
    user_auth_page()  # Show the login/signup page if the user is not logged in

elif page == "Market":
    if "logged_in" in st.session_state and st.session_state.logged_in:
        market.show_page()  # Show Market page if logged in
    else:
        st.error("You need to log in first!")
    
elif page == "Google News":
    if "logged_in" in st.session_state and st.session_state.logged_in:
        google.show_page()  # Show Google page if logged in
    else:
        st.error("You need to log in first!")

elif page == "Dashboard":
    if "logged_in" in st.session_state and st.session_state.logged_in:
        userdashboard.show_page()  # Show Dashboard page if logged in
    else:
        st.error("You need to log in first!")
