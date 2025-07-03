from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    """Request model for document queries"""
    query: str = Field(..., description="The question or query about the document")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the main topics discussed in this document?"
            }
        }

class QueryResponse(BaseModel):
    """Response model for document queries"""
    response: str = Field(..., description="The AI-generated response to the query")
    query: str = Field(..., description="The original query")
    sources: List[str] = Field(default=[], description="Relevant text chunks used for the response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "The main topics discussed include...",
                "query": "What are the main topics discussed in this document?",
                "sources": ["Text chunk 1", "Text chunk 2"]
            }
        }

class StatusResponse(BaseModel):
    """Response model for document processing status"""
    status: str = Field(..., description="Current processing status")
    message: str = Field(..., description="Status message")
    document_info: Optional[Dict[str, Any]] = Field(None, description="Information about the current document")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ready",
                "message": "Document is ready for querying",
                "document_info": {
                    "filename": "example.pdf",
                    "chunks": 15,
                    "chunk_count": 15
                }
            }
        }

class UploadResponse(BaseModel):
    """Response model for document upload"""
    message: str = Field(..., description="Upload status message")
    filename: str = Field(..., description="Name of the uploaded file")
    chunks: int = Field(..., description="Number of text chunks created")
    status: str = Field(..., description="Processing status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Document uploaded and processed successfully",
                "filename": "example.pdf",
                "chunks": 15,
                "status": "ready"
            }
        }

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Overall health status")
    azure_openai: bool = Field(..., description="Azure OpenAI service status")
    vector_store: bool = Field(..., description="Vector store status")
    document_processor: bool = Field(..., description="Document processor status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "azure_openai": True,
                "vector_store": True,
                "document_processor": True
            }
        }

class ResetResponse(BaseModel):
    """Response model for session reset"""
    message: str = Field(..., description="Reset status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Session reset successfully"
            }
        }
