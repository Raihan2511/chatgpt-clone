import streamlit as st
from frontend.pages import login, signup, chat

# Ensure session state is initialized
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "Login"  # Default page

def set_page(page_name):
    st.session_state["page"] = page_name
    st.rerun()

# Redirect based on authentication
if st.session_state["user_id"]:
    st.session_state["page"] = "Chat"

# Render correct page
if st.session_state["page"] == "Login":
    login.show(set_page)
elif st.session_state["page"] == "Sign Up":
    signup.show(set_page)
elif st.session_state["page"] == "Chat":
    chat.show()
