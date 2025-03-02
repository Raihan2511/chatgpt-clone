import streamlit as st
import time
from backend.services.chat_service import generate_response, save_chat_message, get_chat_history
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI


def auto_scroll():
    """Auto-scroll to the latest message in chat."""
    time.sleep(0.1)  # Small delay to ensure UI updates first
    st.markdown(
        """
        <script>
            var chatContainer = window.parent.document.getElementById("chat-container");
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        </script>
        """,
        unsafe_allow_html=True
    )

def show():
    # ✅ Apply ChatGPT-like UI
    st.markdown(
        """
        <style>
            .stApp { background-color: #343541; }  
            
            .chat-bubble { 
                padding: 12px; 
                border-radius: 10px; 
                margin-bottom: 10px; 
                width: fit-content;
            }

            .user-bubble { 
                text-align: right; 
                background-color: #0b93f6;  
                color: white; 
                margin-left: auto;
                align-self: flex-end;
            }

            .bot-bubble {
                text-align: left;
                color: white;
                align-self: flex-start;
                width: 100%;
                border-top: 1px solid;
                border-top-color: #727586;
            }

            .sidebar-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
            .chat-item { padding: 8px; border-radius: 5px; cursor: pointer; color: white; }
            .chat-item:hover { background-color: #52535b; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.title("Chat History")

    user_id = st.session_state.get("user_id", None)
    if not user_id:
        st.sidebar.warning("Please log in to see chat history.")
        return

    # ✅ File uploader for PDF
    st.sidebar.header("Upload PDF for Q&A")
    uploaded_file = st.sidebar.file_uploader("Upload your PDF", type="pdf")

    qa = None  # Initialize RAG system

    if uploaded_file is not None:  # ✅ Fix: Check if file is uploaded before using it
        st.sidebar.success("PDF uploaded successfully! Processing...")

        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getvalue())  # ✅ Prevents NoneType error

        # ✅ Load and process PDF
        loader = PDFPlumberLoader("temp.pdf")
        docs = loader.load()
        text_splitter = SemanticChunker(HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))

        documents = text_splitter.split_documents(docs)

# text_splitter = SemanticChunker(HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))
# embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # ✅ Create embeddings and retriever
        # embedder = HuggingFaceEmbeddings()
        embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector = FAISS.from_documents(documents, embedder)
        retriever = vector.as_retriever(search_type="similarity", search_kwargs={"k": 3})

        # ✅ Define LLM & Prompt

        # llm = Ollama(model="deepseek-r1:1.5b")
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-thinking-exp-1219", google_api_key="AIzaSyAl67MS8iGGcAnMi9RJljSjWtcgRagiqOE")

        prompt = """
        Use the following pieces of context to answer the question:
        Context: {context}
        Question: {question}
        Answer:"""
        QA_CHAIN_PROMPT = PromptTemplate.from_template(prompt)
        
        llm_chain = LLMChain(llm=llm, prompt=QA_CHAIN_PROMPT, verbose=True)
        document_prompt = PromptTemplate(input_variables=["page_content"], template="Context:\n{page_content}")
        
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=llm_chain, document_variable_name="context", document_prompt=document_prompt, verbose=True
        )

        qa = RetrievalQA(combine_documents_chain=combine_documents_chain, retriever=retriever, verbose=True)

    # ✅ Chat UI
    st.title("Chat with AI / Ask About Your PDF")
    st.markdown('<div id="chat-container">', unsafe_allow_html=True)

    # ✅ Load chat history
    chat_history_db = get_chat_history(user_id)

    if "chat_titles" not in st.session_state:
        st.session_state["chat_titles"] = {chat.id: chat.title for chat in chat_history_db}

    if "current_chat_id" not in st.session_state:
        st.session_state["current_chat_id"] = None
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # ✅ Sidebar: Show past chat sessions
    if st.sidebar.button("New Chat"):
        st.session_state["chat_history"] = []
        st.session_state["current_chat_id"] = None
        st.rerun()

    # ✅ Search Chat Feature
    search_query = st.sidebar.text_input("Search chats...", placeholder="Enter keywords to search chat history")

    # ✅ Filter chat titles based on search query
    filtered_chats = [
        chat for chat in chat_history_db if search_query.lower() in chat.title.lower()
    ] if search_query else chat_history_db  # Show all chats if no search input

    # ✅ Sidebar: Show unique filtered chat titles
    unique_titles = {chat.title for chat in filtered_chats}  # ✅ Store only unique titles

    for title in unique_titles:
        if st.sidebar.button(title, key=f"title_{title}"):
            st.session_state["current_chat_title"] = title  # ✅ Store selected chat title
            selected_chat = [c for c in chat_history_db if c.title == title]

            if selected_chat:
                st.session_state["current_chat_id"] = selected_chat[0].id  # ✅ Store chat ID for saving new messages
                st.session_state["chat_history"] = [(c.message, c.response) for c in selected_chat]

            st.rerun()


    # ✅ Display chat messages dynamically
    for message, response in st.session_state["chat_history"]:
        st.markdown(f'<div class="chat-bubble user-bubble">{message}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble bot-bubble">{response}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ✅ Auto-scroll to latest message
    auto_scroll()

    user_input = st.text_input("You:", "")

    # if st.button("Send"):
    #     if user_input:
    #         response = generate_response(user_input, use_rag=(qa is not None), qa=qa)

    #         st.session_state["chat_history"].append((user_input, response))

    #         chat_id = st.session_state["current_chat_id"]
    #         chat_entry = save_chat_message(user_id, user_input, response, chat_id)

    #         if not chat_id and chat_entry:
    #             st.session_state["current_chat_id"] = chat_entry.id
    #             st.session_state["chat_titles"][chat_entry.id] = chat_entry.title

    #         st.rerun()
    #     else:
    #         st.warning("Please enter a message.")
    if st.button("Send"):
        print("<think...>")
        if user_input:
            response = generate_response(user_input, use_rag=(qa is not None), qa=qa)

            st.session_state["chat_history"].append((user_input, response))

            chat_id = st.session_state.get("current_chat_id")  # ✅ Get the existing chat session ID

            chat_entry = save_chat_message(user_id, user_input, response, chat_id)  # ✅ Save under the same chat

            if not chat_id and chat_entry:
                st.session_state["current_chat_id"] = chat_entry.id  # ✅ Store chat ID for future messages
                st.session_state["chat_titles"][chat_entry.id] = chat_entry.title  # ✅ Store title

            st.rerun()

