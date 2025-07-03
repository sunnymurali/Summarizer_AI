# AI Document Analysis Application

## Overview

This is a full-stack AI document analysis application built with FastAPI backend and Streamlit frontend. The application allows users to upload documents (PDF, TXT, DOCX) and perform intelligent queries on them using Azure OpenAI's GPT and embedding models. The system uses FAISS for vector similarity search to retrieve relevant document chunks for question answering.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit
- **Port**: 5000
- **Purpose**: Provides a user-friendly web interface for document upload and querying
- **Communication**: HTTP requests to FastAPI backend on port 8000

### Backend Architecture
- **Framework**: FastAPI
- **Port**: 8000  
- **Architecture Pattern**: Service-oriented with clear separation of concerns
- **API Design**: RESTful endpoints for document upload, status checking, and querying
- **CORS**: Enabled for cross-origin requests from frontend

## Key Components

### Backend Services
1. **DocumentProcessor**: Handles document parsing and text extraction
   - Supports PDF (PyPDF2), TXT (plain text), and DOCX (python-docx) formats
   - Implements text chunking with configurable chunk size (1000 tokens) and overlap (200 tokens)
   - Uses tiktoken for accurate token counting

2. **VectorStore**: FAISS-based vector storage and similarity search
   - Uses L2 distance for similarity calculations
   - Stores document embeddings with 1536 dimensions (Azure OpenAI standard)
   - Provides efficient similarity search for document chunks

3. **AzureOpenAIService**: Integration with Azure OpenAI API
   - Handles both text generation (GPT-4) and embeddings (text-embedding-ada-002)
   - Implements batch processing for embeddings with size limits
   - Manages API authentication and configuration

### Data Models
- **Pydantic schemas** for request/response validation
- Type-safe models for QueryRequest, QueryResponse, StatusResponse, and UploadResponse

### Utilities
- **File validation**: Ensures only supported file types are processed
- **MIME type checking**: Additional validation layer for file uploads
- **File size validation**: Prevents processing of oversized files

## Data Flow

1. **Document Upload**:
   - User uploads document via Streamlit interface
   - Frontend sends file to `/upload` endpoint
   - Backend validates file type and processes document
   - Text is extracted and chunked into manageable pieces
   - Chunks are converted to embeddings via Azure OpenAI
   - Embeddings are stored in FAISS vector store

2. **Document Querying**:
   - User submits query via Streamlit chat interface
   - Query is converted to embedding using Azure OpenAI
   - Vector similarity search finds relevant document chunks
   - Context and query are sent to GPT-4 for response generation
   - Response is returned with source chunks for transparency

3. **Status Monitoring**:
   - Frontend polls `/status` endpoint to track processing progress
   - Backend maintains global state for document processing status

## External Dependencies

### Required Services
- **Azure OpenAI**: Core AI functionality for embeddings and text generation
  - Requires API key, endpoint, and deployment names
  - Uses text-embedding-ada-002 for embeddings
  - Uses GPT-4 for text generation

### Python Libraries
- **FastAPI**: Web framework for backend API
- **Streamlit**: Frontend framework
- **FAISS**: Vector similarity search
- **PyPDF2**: PDF processing
- **python-docx**: DOCX processing
- **tiktoken**: Token counting for OpenAI models
- **numpy**: Numerical operations for embeddings

## Deployment Strategy

### Local Development
- **Service Orchestration**: `start_services.py` manages both frontend and backend
- **Backend Runner**: `run_backend.py` provides standalone backend execution
- **Port Configuration**: Backend on 8000, Frontend on 5000
- **Auto-reload**: Enabled for development convenience

### Environment Configuration
- Relies on environment variables for Azure OpenAI configuration
- No database persistence - uses in-memory storage
- Temporary file handling for document processing

### Process Management
- Threading-based service startup
- Graceful shutdown handling
- Error recovery and logging

## Changelog
- July 03, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.