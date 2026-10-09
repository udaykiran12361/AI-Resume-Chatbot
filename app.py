
import os
import tempfile
import hashlib

import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

# Load API key from .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(
    page_title="AI Resume Chatbot",
    page_icon="🤖",
    layout="wide",
)

# Initialize session state
if "vector_db" not in st.session_state:
    st.session_state.vector_db = None

if "file_id" not in st.session_state:
    st.session_state.file_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "resume_name" not in st.session_state:
    st.session_state.resume_name = ""

if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0

# Sidebar
with st.sidebar:
    st.title("🤖 AI Resume Chatbot")
    st.write("Chat with your resume using AI.")

    st.subheader("Project Features")
    st.write("✅ PDF Resume Processing")
    st.write("✅ Text Chunking")
    st.write("✅ Gemini Embeddings")
    st.write("✅ FAISS Vector Search")
    st.write("✅ Gemini AI")
    st.write("✅ Chat History")

    if st.session_state.vector_db is not None:
        st.success("Resume Loaded")
        st.write(f"File: {st.session_state.resume_name}")
        st.write(f"Text chunks: {st.session_state.chunk_count}")

    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main page
st.title("🤖 AI Resume Chatbot")
st.write(
    "Upload your resume and ask questions about your "
    "education, skills, projects and experience."
)

if not GOOGLE_API_KEY:
    st.error(
        "Google API key not found. Check the GOOGLE_API_KEY "
        "entry in your project's .env file."
    )
    st.stop()

uploaded_file = st.file_uploader(
    "📄 Upload your Resume PDF",
    type=["pdf"],
)

# Process uploaded PDF
if uploaded_file is not None:
    pdf_bytes = uploaded_file.getvalue()
    current_file_id = hashlib.md5(pdf_bytes).hexdigest()

    if current_file_id != st.session_state.file_id:
        st.session_state.vector_db = None
        st.session_state.file_id = None
        st.session_state.messages = []

        temp_path = None

        try:
            with st.spinner("Reading your resume..."):
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".pdf"
                ) as temp_file:
                    temp_file.write(pdf_bytes)
                    temp_path = temp_file.name

                documents = PyPDFLoader(temp_path).load()

            if not documents:
                st.error("No readable pages found in this PDF.")
                st.stop()

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=150,
            )
            chunks = splitter.split_documents(documents)

            if not chunks:
                st.error(
                    "No text found. Please upload a text-based PDF."
                )
                st.stop()

            with st.spinner("Creating Gemini embeddings..."):
                embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/gemini-embedding-001",
                    google_api_key=GOOGLE_API_KEY,
                )

                vector_db = FAISS.from_documents(
                    chunks,
                    embeddings,
                )

            st.session_state.vector_db = vector_db
            st.session_state.file_id = current_file_id
            st.session_state.resume_name = uploaded_file.name
            st.session_state.chunk_count = len(chunks)

        except Exception as error:
            st.error(f"Resume processing failed: {error}")
            st.stop()

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    st.success(
        f"✅ Resume processed successfully! "
        f"Created {st.session_state.chunk_count} text chunks."
    )

    st.subheader("💬 Chat with Your Resume")
    st.caption(
        "Ask questions about your resume. "
        "Answers are based on the uploaded document."
    )

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                st.caption(
                    "📄 Sources: "
                    + ", ".join(
                        f"Page {page}"
                        for page in message["sources"]
                    )
                )

    # Chat input
    question = st.chat_input("Ask something about your resume...")

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        try:
            with st.spinner("Searching your resume..."):
                relevant_docs = (
                    st.session_state.vector_db.similarity_search(
                        question, k=4
                    )
                )

            context = "\n\n".join(
                doc.page_content for doc in relevant_docs
            )

            source_pages = sorted(
                {
                    doc.metadata.get("page", 0) + 1
                    for doc in relevant_docs
                }
            )

            prompt = f"""
You are an AI assistant that answers questions about a resume.

Use ONLY the information in the resume context below.
Do not invent skills, qualifications, experience, or projects.
If the answer is not present, say:
"I couldn't find that information in the uploaded resume."

Resume context:
{context}

Question:
{question}

Give a clear, professional answer.
"""

            with st.spinner("Generating answer with Gemini..."):
                llm = ChatGoogleGenerativeAI(
                    model="gemini-3.8-flash",
                    google_api_key=GOOGLE_API_KEY,
                    temperature=0.2,
                )
                response = llm.invoke(prompt)
                answer = response.content
                if isinstance(answer, list):
                    answer = "\n".join(
                        item.get("text", "")
                        for item in answer
                        if isinstance(item, dict) and item.get("type") == "text"
                    )

                if not isinstance(answer, str):
                    answer = str(answer)


                if not isinstance(answer, str):
                    answer = str(answer)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": source_pages,
                }
            )

            with st.chat_message("assistant"):
                st.markdown(answer)
                st.caption(
                    "📄 Sources: "
                    + ", ".join(
                        f"Page {page}" for page in source_pages
                    )
                )

        except Exception as error:
            st.error(f"Could not generate an answer: {error}")

else:
    st.info("👆 Upload your resume PDF to start chatting.")

    st.subheader("🚀 How it works")
    st.write("1. Upload your resume PDF.")
    st.write("2. The app extracts and splits the text.")
    st.write("3. Gemini embeddings and FAISS find relevant content.")
    st.write("4. Gemini generates an answer from your resume.")
