import streamlit as st
import requests
import time
import os
from typing import List, Dict, Any
import json

# Configuration
BACKEND_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="AI Document Analysis",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'document_uploaded' not in st.session_state:
    st.session_state.document_uploaded = False
if 'document_name' not in st.session_state:
    st.session_state.document_name = ""
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = ""

def upload_document(file):
    """Upload document to backend"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return True, result.get("message", "Document uploaded successfully")
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return False, f"Upload failed: {error_detail}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_processing_status():
    """Check document processing status"""
    try:
        response = requests.get(f"{BACKEND_URL}/status", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "message": "Could not check status"}
    except:
        return {"status": "error", "message": "Backend not available"}

def send_query(query: str):
    """Send query to backend for document analysis"""
    try:
        data = {"query": query}
        response = requests.post(f"{BACKEND_URL}/query_reranked", json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return True, result.get("response", "No response received")
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return False, f"Query failed: {error_detail}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def clear_chat():
    """Clear chat history"""
    st.session_state.messages = []
    st.rerun()

def reset_session():
    """Reset entire session"""
    try:
        requests.post(f"{BACKEND_URL}/reset", timeout=10)
    except:
        pass
    
    st.session_state.messages = []
    st.session_state.document_uploaded = False
    st.session_state.document_name = ""
    st.session_state.processing_status = ""
    st.rerun()

# Main UI
st.title("📄 AI Document Analysis")
st.markdown("Upload a document and interrogate it using AI-powered analysis")

# Sidebar for document upload and controls
with st.sidebar:
    st.header("📁 Document Upload")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a document",
        type=['pdf', 'txt', 'docx'],
        help="Supported formats: PDF, TXT, DOCX"
    )
    
    if uploaded_file is not None:
        if st.button("Upload Document", type="primary"):
            with st.spinner("Uploading document..."):
                success, message = upload_document(uploaded_file)
                
                if success:
                    st.session_state.document_uploaded = True
                    st.session_state.document_name = uploaded_file.name
                    st.session_state.processing_status = "processing"
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    # Document status
    if st.session_state.document_uploaded:
        st.header("📋 Document Status")
        
        # Check processing status
        status_info = check_processing_status()
        
        if status_info["status"] == "ready":
            st.success("✅ Document ready for analysis")
            st.session_state.processing_status = "ready"
        elif status_info["status"] == "processing":
            st.info("⏳ Processing document...")
            st.session_state.processing_status = "processing"
            # Auto-refresh every 2 seconds while processing
            time.sleep(2)
            st.rerun()
        else:
            st.error(f"❌ {status_info.get('message', 'Unknown status')}")
        
        # Document info
        st.info(f"📄 **Document:** {st.session_state.document_name}")
        
        # Control buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Chat"):
                clear_chat()
        with col2:
            if st.button("Reset All"):
                reset_session()

# Main content area
if not st.session_state.document_uploaded:
    st.info("👆 Please upload a document using the sidebar to begin analysis")
    
    # Instructions
    st.markdown("### How to use:")
    st.markdown("""
    1. **Upload a document** using the sidebar (PDF, TXT, or DOCX)
    2. **Wait for processing** - the document will be analyzed and indexed
    3. **Start chatting** - ask questions about your document content
    4. **Get AI insights** - receive intelligent responses based on your document
    """)
    
    st.markdown("### Example queries:")
    st.markdown("""
    - "What is the main topic of this document?"
    - "Summarize the key points"
    - "What are the conclusions mentioned?"
    - "Find information about [specific topic]"
    """)

elif st.session_state.processing_status == "processing":
    st.info("⏳ Your document is being processed. Please wait...")
    st.markdown("The system is:")
    st.markdown("- Extracting text from your document")
    st.markdown("- Breaking it into chunks for analysis")
    st.markdown("- Creating embeddings for similarity search")
    st.markdown("- Preparing the vector store for queries")

else:
    # Chat interface
    st.header("💬 Chat with your Document")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your document..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing document..."):
                success, response = send_query(prompt)
                
                if success:
                    st.markdown(response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    error_message = f"❌ {response}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})

# Footer
st.markdown("---")
st.markdown("*Powered by Azure OpenAI and FAISS Vector Store*")
