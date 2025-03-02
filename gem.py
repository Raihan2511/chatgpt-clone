import google.generativeai as genai
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import RetrievalQA

# Set up Google Gemini API key
import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyAl67MS8iGGcAnMi9RJljSjWtcgRagiqOE"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load the PDF
loader = PDFPlumberLoader("temp.pdf")
docs = loader.load()

# Split the document into chunks
text_splitter = SemanticChunker(HuggingFaceEmbeddings())
documents = text_splitter.split_documents(docs)

# Instantiate the embedding model
embedder = HuggingFaceEmbeddings()

# Create vector store and retriever
vector = FAISS.from_documents(documents, embedder)
retriever = vector.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Define the LLM (Google Gemini)
llm = genai.GenerativeModel("imagen-3.0-generate-002")

# Define the prompt
prompt = """
1. Use the following pieces of context to answer the question at the end.
2. If you don't know the answer, just say that "I don't know" but don't make up an answer on your own.\n
3. Keep the answer crisp and limited to 3-4 sentences.
Context: {context}
Question: {question}
Helpful Answer:"""
QA_CHAIN_PROMPT = PromptTemplate.from_template(prompt)

# Define the document and combination chains
llm_chain = LLMChain(llm=llm, prompt=QA_CHAIN_PROMPT, verbose=True)
document_prompt = PromptTemplate(
    input_variables=["page_content", "source"],
    template="Context:\ncontent:{page_content}\nsource:{source}",
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

# Example usage: Ask a question
user_input = "What is the main topic of the document?"
response = qa(user_input)["result"]
print("Response:", response)
