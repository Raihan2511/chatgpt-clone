import os
import streamlit as st
import google.generativeai as genai
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA

# Set up Google Gemini API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyAl67MS8iGGcAnMi9RJljSjWtcgRagiqOE"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Streamlit UI
st.title("📄 PDF-based RAG System with Gemini")

st.sidebar.header("Instructions")
st.sidebar.write("""
1. Upload a PDF document.
2. Ask any question related to the document.
3. The model will provide concise, context-based answers.
""")

# File Upload Section
uploaded_file = st.file_uploader("📄 Upload your PDF file", type="pdf")

if uploaded_file is not None:
    st.success("✅ PDF uploaded successfully!")
    
    # Save File Temporarily
    with open("temp1.pdf", "wb") as f:
        f.write(uploaded_file.getvalue())

    # Load PDF
    loader = PDFPlumberLoader("temp1.pdf")
    docs = loader.load()

    st.info("📚 Splitting the document into chunks...")
    text_splitter = SemanticChunker(HuggingFaceEmbeddings())
    documents = text_splitter.split_documents(docs)


    # Split PDF into Chunks
    
    embedder = HuggingFaceEmbeddings()

    # Create Vector Store with FAISS
    st.info("🔍 Creating Embeddings and FAISS Vector Store...")
    vector = FAISS.from_documents(documents, embedder)
    retriever = vector.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    # Define Gemini LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-thinking-exp-1219", google_api_key="AIzaSyAl67MS8iGGcAnMi9RJljSjWtcgRagiqOE")

    # Prompt Template
    prompt = """
    Use the following context to answer the question.
    If you don't know the answer, just say "I don't know."
    Context: {context}
    Question: {question}
    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate.from_template(prompt)

    # LLM Chain
    llm_chain = LLMChain(llm=llm, prompt=QA_CHAIN_PROMPT, verbose=True)
    document_prompt = PromptTemplate(
        input_variables=["page_content"],
        template="Context:\n{page_content}"
    )
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="context",
        document_prompt=document_prompt,
        verbose=True
    )

    qa = RetrievalQA(
        combine_documents_chain=combine_documents_chain,
        retriever=retriever,
        verbose=True,
        return_source_documents=True
    )

    # User Question Input
    st.header("❓ Ask a Question")
    user_input = st.text_input("Type your question:")

    if user_input:
        with st.spinner("⏳ Generating Answer..."):
            try:
                result = qa(user_input)
                st.success("✅ Response:")
                st.write(result["result"])

                # Display Context
                st.subheader("🔍 Retrieved Context")
                for doc in result["source_documents"]:
                    st.text(f"{doc.page_content[:300]}...")

            except Exception as e:
                st.error(f"❌ Error: {e}")

else:
    st.info("📌 Please upload a PDF file to proceed.")
