import streamlit as st
from backend.services.auth_service import authenticate_user

def show(set_page):
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = authenticate_user(username, password)
        if user:
            st.session_state["user_id"] = user.id
            st.success("Login successful! Redirecting to chat...")
            set_page("Chat")  # Redirect to chat page
        else:
            st.error("Invalid username or password.")
            
    st.button("Go to Sign Up", on_click=lambda: set_page("Sign Up"))


