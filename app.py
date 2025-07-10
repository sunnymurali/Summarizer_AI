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
        response = requests.post(f"{BACKEND_URL}/query", json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return True, result  # Return full result with sources
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return False, f"Query failed: {error_detail}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def send_query_reranked(query: str):
    """Send query to backend for reranked document analysis"""
    try:
        data = {"query": query}
        response = requests.post(f"{BACKEND_URL}/query_reranked", json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return True, result  # Return full result with sources
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return False, f"Query failed: {error_detail}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def send_query_bm25(query: str):
    """Send query to backend for BM25 keyword search"""
    try:
        data = {"query": query}
        response = requests.post(f"{BACKEND_URL}/query_bm25", json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return True, result
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return False, f"BM25 query failed: {error_detail}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def send_query_contextual(query: str):
    """Send query to backend for contextual retrieval"""
    try:
        data = {"query": query}
        response = requests.post(f"{BACKEND_URL}/query_contextual", json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return True, result
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return False, f"Contextual query failed: {error_detail}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def send_query_hybrid(query: str):
    """Send query to backend for hybrid retrieval"""
    try:
        data = {"query": query}
        response = requests.post(f"{BACKEND_URL}/query_hybrid", json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return True, result
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return False, f"Hybrid query failed: {error_detail}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def display_sources(sources: List[str], title: str = "📚 Sources Used"):
    """Display source citations in an expandable section"""
    if sources:
        with st.expander(f"{title} ({len(sources)} sources)", expanded=False):
            for i, source in enumerate(sources, 1):
                st.markdown(f"**Source {i}:**")
                # Truncate long sources for better display
                if len(source) > 500:
                    preview = source[:500] + "..."
                    st.markdown(f"*{preview}*")
                    with st.expander(f"View full source {i}"):
                        st.text(source)
                else:
                    st.markdown(f"*{source}*")
                if i < len(sources):
                    st.markdown("---")

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
        
        # Query method selection
        st.header("🔍 Query Method")
        query_method = st.selectbox(
            "Choose retrieval strategy:",
            [
                "Standard Query",
                "Reranked Query (GPT-4o)",
                "BM25 Keyword Search", 
                "Contextual Retrieval",
                "Hybrid Search (Recommended)"
            ],
            index=4,  # Default to Hybrid Search
            help="Different methods for finding relevant information in your document"
        )
        
        # Query method descriptions
        method_descriptions = {
            "Standard Query": "🔍 Basic semantic similarity search",
            "Reranked Query (GPT-4o)": "🔄 Semantic search + GPT-4o reranking",
            "BM25 Keyword Search": "🔤 Keyword-based search for exact terms",
            "Contextual Retrieval": "📖 Context-aware document search",
            "Hybrid Search (Recommended)": "🚀 Combines all methods for best results"
        }
        
        st.info(method_descriptions.get(query_method, "Select a query method"))

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
            # Display sources if available
            if message["role"] == "assistant" and "sources" in message:
                display_sources(message["sources"])
    
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
                # Route to appropriate query method
                if query_method == "Standard Query":
                    success, response_data = send_query(prompt)
                    query_type = "🔍 Standard Query"
                elif query_method == "Reranked Query (GPT-4o)":
                    success, response_data = send_query_reranked(prompt)
                    query_type = "🔄 Reranked Query"
                elif query_method == "BM25 Keyword Search":
                    success, response_data = send_query_bm25(prompt)
                    query_type = "🔤 BM25 Search"
                elif query_method == "Contextual Retrieval":
                    success, response_data = send_query_contextual(prompt)
                    query_type = "📖 Contextual Search"
                elif query_method == "Hybrid Search (Recommended)":
                    success, response_data = send_query_hybrid(prompt)
                    query_type = "🚀 Hybrid Search"
                else:
                    success, response_data = send_query(prompt)
                    query_type = "🔍 Default Query"
                
                if success and isinstance(response_data, dict):
                    # Display the response
                    response_text = response_data.get("response", "No response received")
                    st.markdown(response_text)
                    
                    # Display sources if available
                    sources = response_data.get("sources", [])
                    if sources:
                        display_sources(sources, f"📚 Sources Used ({query_type})")
                    
                    # Add assistant response to chat history with sources
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response_text,
                        "sources": sources,
                        "query_type": query_type
                    })
                else:
                    error_message = f"❌ {response_data if isinstance(response_data, str) else 'Unknown error'}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})

# Footer
st.markdown("---")
st.markdown("*Powered by Azure OpenAI and FAISS Vector Store*")
