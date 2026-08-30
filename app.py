"""Streamlit Web Application for AI Multi-PDF Question Answering."""

import streamlit as st
from config import get_api_key
from pdf_extractor import PDFExtractor, PDFDocument
from chat_agent import PDFChatAgent

# Page configuration
st.set_page_config(
    page_title="PDF Question Answering with AI",
    page_icon="📄",
    layout="wide",
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #666;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    /* Streamlit chat message formatting */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 0.8rem;
    }
    .stChatMessage h3 {
        font-size: 1.25rem;
        margin-top: 1rem;
        margin-bottom: 0.4rem;
        color: #1a73e8;
    }
    .stChatMessage code {
        background-color: #f1f3f4;
        color: #d93025;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.9em;
    }
    .footer {
        text-align: center;
        color: #888;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown('<div class="main-title">📄 PDF Question Answering with AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Powered by Google Gemini</div>', unsafe_allow_html=True)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents" not in st.session_state:
    st.session_state.documents = []

if "agent" not in st.session_state:
    st.session_state.agent = None

if "processed" not in st.session_state:
    st.session_state.processed = False

# Sidebar for PDF uploads
with st.sidebar:
    st.header("📥 Upload PDFs")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or multiple PDF documents to analyze and compare.",
    )

    if st.button("Process PDFs", type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("Please upload at least one PDF file first.")
        else:
            with st.spinner("Extracting and processing PDFs..."):
                docs: list[PDFDocument] = []
                for uploaded_file in uploaded_files:
                    try:
                        doc = PDFExtractor.extract_stream(uploaded_file, file_name=uploaded_file.name)
                        docs.append(doc)
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {e}")

                if docs:
                    api_key = get_api_key()
                    agent = PDFChatAgent(api_key=api_key)
                    agent.set_documents(docs)

                    st.session_state.documents = docs
                    st.session_state.agent = agent
                    st.session_state.processed = True
                    st.session_state.messages = []  # Reset chat history for new documents
                    st.success(f"Successfully loaded {len(docs)} PDF document(s)!")

    # Display loaded PDFs section
    if st.session_state.processed and st.session_state.documents:
        st.markdown("---")
        st.subheader("✅ Loaded PDFs:")
        for doc in st.session_state.documents:
            page_str = "page" if doc.page_count == 1 else "pages"
            st.markdown(f"- **{doc.file_name}** ({doc.page_count} {page_str}, {doc.char_count:,} chars)")

        st.markdown("---")
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.agent:
                st.session_state.agent.reset()
                st.session_state.agent.set_documents(st.session_state.documents)
            st.rerun()

# Main area logic
if not st.session_state.processed:
    st.info("👈 Upload PDF files from the sidebar to get started!")
else:
    # Render chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your PDFs..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.agent.ask(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error generating answer: {e}"
                    st.error(error_msg)

# Footer
st.markdown(
    '<div class="footer">Built with Streamlit • Powered by Google Gemini • LangChain</div>',
    unsafe_allow_html=True,
)
