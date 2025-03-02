import streamlit as st
from backend.services.auth_service import create_user

def show(set_page):
    st.title("Sign Up")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if not username or not password:
            st.warning("Please fill all fields.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            user = create_user(username, password)
            if user:
                st.success("Account created! Redirecting to login...")
                set_page("Login")  # Redirect to login
            else:
                st.error("Username already exists. Choose another one.")
