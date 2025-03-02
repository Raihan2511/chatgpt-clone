import streamlit as st
from backend.models.chat_history import ChatHistory
from backend.services.chat_service import get_chat_history

from backend.models.database import get_db
from sqlalchemy.orm import Session

def delete_chat(chat_id):
    """Delete a chat session from the database."""
    db: Session = next(get_db())
    try:
        db.query(ChatHistory).filter(ChatHistory.id == chat_id).delete()
        db.commit()
        st.success("Chat deleted successfully!")
        st.rerun()  # Refresh page after deletion
    except Exception as e:
        db.rollback()
        st.error(f"Error deleting chat: {e}")
    finally:
        db.close()

def show():
    """Display and manage past chat sessions."""
    st.sidebar.title("Chat History")
    
    user_id = st.session_state.get("user_id", None)
    if not user_id:
        st.sidebar.warning("Please log in to see your chat history.")
        return

    # ✅ Load chat history
    chat_history_db = get_chat_history(user_id)

    if not chat_history_db:
        st.info("No chat history found.")
        return

    # ✅ Sidebar: Show chat sessions
    search_query = st.sidebar.text_input("Search chats...")
    
    filtered_chats = [
        chat for chat in chat_history_db if not search_query or search_query.lower() in chat.title.lower()
    ]

    for chat in filtered_chats:
        if st.sidebar.button(chat.title, key=f"sidebar_{chat.id}"):
            st.session_state["current_chat_id"] = chat.id
            st.rerun()

    # ✅ Display chat session details
    chat_id = st.session_state.get("current_chat_id")
    if not chat_id:
        st.write("Select a chat from the sidebar to view the conversation.")
        return

    selected_chat = [chat for chat in chat_history_db if chat.id == chat_id]
    
    if not selected_chat:
        st.error("Chat not found!")
        return

    st.title(f"Chat: {selected_chat[0].title}")
    for chat in selected_chat:
        st.write(f"**You:** {chat.message}")
        st.write(f"**AI:** {chat.response}")
        st.write(f"**Date:** {chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write("---")

    # ✅ Delete button for chat history
    if st.button("Delete Chat"):
        delete_chat(chat_id)
