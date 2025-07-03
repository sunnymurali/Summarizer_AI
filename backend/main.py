from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import shutil
import tempfile
from typing import Optional

from .services.document_processor import DocumentProcessor
from .services.vector_store import VectorStore
from .services.azure_openai_service import AzureOpenAIService
from .models.schemas import QueryRequest, QueryResponse, StatusResponse
from .utils.file_utils import validate_file_type, get_file_extension

# Initialize FastAPI app
app = FastAPI(title="AI Document Analysis API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_processor = DocumentProcessor()
vector_store = VectorStore()
azure_openai_service = AzureOpenAIService()

# Global state
current_document = None
document_status = "none"  # none, processing, ready, error

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    global current_document, document_status
    
    try:
        # Validate file type
        if not validate_file_type(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload PDF, TXT, or DOCX files."
            )
        
        # Set processing status
        document_status = "processing"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=get_file_extension(file.filename)) as tmp_file:
            # Save uploaded file
            shutil.copyfileobj(file.file, tmp_file)
            tmp_file_path = tmp_file.name
        
        try:
            # Process document
            text_content = document_processor.process_document(tmp_file_path, file.filename)
            
            if not text_content or not text_content.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract text from the document. Please ensure the file is not corrupted."
                )
            
            # Create chunks
            chunks = document_processor.create_chunks(text_content)
            
            if not chunks:
                raise HTTPException(
                    status_code=400,
                    detail="Document is too short or could not be processed into chunks."
                )
            
            # Generate embeddings and store in vector store
            embeddings = await azure_openai_service.get_embeddings(chunks)
            vector_store.add_documents(chunks, embeddings)
            
            # Update global state
            current_document = {
                "filename": file.filename,
                "content": text_content,
                "chunks": chunks,
                "chunk_count": len(chunks)
            }
            document_status = "ready"
            
            return {
                "message": "Document uploaded and processed successfully",
                "filename": file.filename,
                "chunks": len(chunks),
                "status": "ready"
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except HTTPException:
        document_status = "error"
        raise
    except Exception as e:
        document_status = "error"
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current document processing status"""
    return StatusResponse(
        status=document_status,
        message=f"Document status: {document_status}",
        document_info=current_document
    )

@app.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    """Query the uploaded document"""
    global current_document, document_status
    
    if document_status != "ready" or not current_document:
        raise HTTPException(
            status_code=400,
            detail="No document is ready for querying. Please upload a document first."
        )
    
    try:
        # Get query embedding
        query_embedding = await azure_openai_service.get_embeddings([request.query])
        
        if not query_embedding:
            raise HTTPException(
                status_code=500,
                detail="Could not generate embedding for query"
            )
        
        # Search similar chunks
        similar_chunks = vector_store.search_similar(query_embedding[0], k=5)
        
        if not similar_chunks:
            return QueryResponse(
                response="I couldn't find relevant information in the document to answer your question.",
                query=request.query,
                sources=[]
            )
        
        # Generate response using Azure OpenAI
        response_text = await azure_openai_service.generate_response(
            query=request.query,
            context_chunks=similar_chunks,
            document_filename=current_document["filename"]
        )
        
        return QueryResponse(
            response=response_text,
            query=request.query,
            sources=similar_chunks[:3]  # Return top 3 sources
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.post("/reset")
async def reset_session():
    """Reset the current session"""
    global current_document, document_status
    
    try:
        # Clear vector store
        vector_store.clear()
        
        # Reset global state
        current_document = None
        document_status = "none"
        
        return {"message": "Session reset successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting session: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "azure_openai": azure_openai_service.is_configured(),
        "vector_store": vector_store.is_ready(),
        "document_processor": document_processor.is_ready()
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Document Analysis API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
