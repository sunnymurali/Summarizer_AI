from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import shutil
import tempfile
from typing import Optional, List
from .services.bm25_retriever import BM25Retriever
from .services.contextual_retriever import ContextualRetriever
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
bm25_retriever = BM25Retriever()
contextual_retriever = ContextualRetriever()
# Global state for multiple documents
documents_collection = []  # List of all uploaded documents
document_status = "none"  # none, processing, ready, error
total_chunks = 0

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    global documents_collection, document_status, total_chunks
    
    try:
        # Validate file type
        if not validate_file_type(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload PDF, TXT, or DOCX files."
            )
        
        # Check if file already exists
        existing_doc = next((doc for doc in documents_collection if doc["filename"] == file.filename), None)
        if existing_doc:
            raise HTTPException(
                status_code=400,
                detail=f"Document '{file.filename}' already exists. Please use a different name or remove the existing document first."
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
            
            # Add document metadata to chunks for tracking
            chunks_with_metadata = []
            for chunk in chunks:
                chunks_with_metadata.append({
                    "text": chunk,
                    "document": file.filename,
                    "chunk_id": len(chunks_with_metadata)
                })

            # Generate embeddings and store in vector store
            embeddings = await azure_openai_service.get_embeddings(chunks)
            vector_store.add_documents(chunks, embeddings)
                        
            # Add documents to BM25 retriever
            bm25_retriever.add_documents(chunks)
            

            # Add documents to contextual retriever
            contextual_retriever.add_documents(chunks, embeddings)

            # Update documents collection
            new_document = {
                "filename": file.filename,
                "content": text_content,
                "chunks": chunks,
                 "chunks_with_metadata": chunks_with_metadata,
                "chunk_count": len(chunks),
                "upload_time": str(os.path.getmtime(tmp_file_path))
            }
            # Update global state
            documents_collection.append(new_document)
            # Update global counters
            total_chunks += len(chunks)
            document_status = "ready"
            
            return {
                "message": "Document uploaded and processed successfully",
                "filename": file.filename,
                "chunks": len(chunks),
                "status": "ready",
                "total_documents": len(documents_collection)
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
    global documents_collection, document_status, total_chunks
    
    if document_status == "none":
        return StatusResponse(
            status="none",
            message="No documents uploaded yet",
            documents=[],
            total_documents=0,
            total_chunks=0
        )
    elif document_status == "processing":
        return StatusResponse(
            status="processing",
            message="Document is being processed...",
            documents=[{"filename": doc["filename"], "chunks": doc["chunk_count"]} for doc in documents_collection],
            total_documents=len(documents_collection),
            total_chunks=total_chunks
        )
    elif document_status == "ready":
        return StatusResponse(
            status="ready",
            message=f"Ready to query {len(documents_collection)} document(s)",
            documents=[{"filename": doc["filename"], "chunks": doc["chunk_count"]} for doc in documents_collection],
            total_documents=len(documents_collection),
            total_chunks=total_chunks
        )
    elif document_status == "error":
        return StatusResponse(
            status="error",
            message="Error processing document",
            documents=[{"filename": doc["filename"], "chunks": doc["chunk_count"]} for doc in documents_collection],
            total_documents=len(documents_collection),
            total_chunks=total_chunks
        )
    else:
        return StatusResponse(
            status="unknown",
            message="Unknown status",
            documents=[],
            total_documents=0,
            total_chunks=0
        )

@app.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    """Query the uploaded documents"""
    global documents_collection, document_status
    
    if document_status != "ready" or not documents_collection:
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
            document_filename=f"{len(documents_collection)} documents"
        )
        
        # Extract source documents from chunks
        source_documents = list(set([doc["filename"] for doc in documents_collection]))
        
        return QueryResponse(
            response=response_text,
            query=request.query,
            sources=similar_chunks[:3],  # Return top 3 sources
            source_documents=source_documents,
            documents_searched=len(documents_collection)  
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.post("/query_reranked", response_model=QueryResponse)
async def query_document_by_semantic_reranking(request: QueryRequest):
    """Query the uploaded documents with semantic reranking for better results"""
    global documents_collection, document_status
    
    if document_status != "ready" or not documents_collection:
        raise HTTPException(
            status_code=400,
            detail="No documents are ready for querying. Please upload a document first."
        )
    
    try:
        # Step 1: Get query embedding
        query_embedding = await azure_openai_service.get_embeddings([request.query])
        
        if not query_embedding:
            raise HTTPException(
                status_code=500,
                detail="Could not generate embedding for query"
            )
        
        # Step 2: Perform initial semantic search to get larger pool of candidates
        k_initial = 10  # Get more candidates for reranking
        retrieved_docs = vector_store.search_similar_with_metadata(query_embedding[0], k=k_initial)
        
        if not retrieved_docs:
            return QueryResponse(
                response="I couldn't find relevant information in the document to answer your question.",
                query=request.query,
                sources=[]
            )
        
        # Step 3: Re-rank documents using GPT-4o
        reranked_docs = await azure_openai_service.rerank_documents(
            query=request.query,
            retrieved_docs=retrieved_docs
        )
        
        # Step 4: Extract top reranked chunks for response generation
        top_reranked_chunks = [doc['text'] for doc in reranked_docs[:5]]
        
        # Step 5: Generate response using Azure OpenAI with reranked context
        response_text = await azure_openai_service.generate_response(
            query=request.query,
            context_chunks=top_reranked_chunks,
            document_filename=f"{len(documents_collection)} documents"
        )
        
        # Extract source documents
        source_documents = list(set([doc["filename"] for doc in documents_collection]))
        
        return QueryResponse(
            response=response_text,
            query=request.query,
            sources=top_reranked_chunks[:3],  # Return top 3 reranked sources
            source_documents=source_documents,
            documents_searched=len(documents_collection)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query with reranking: {str(e)}"
        )

@app.post("/query_bm25", response_model=QueryResponse)
async def query_document_bm25(request: QueryRequest):
    """Query documents using BM25 keyword search"""
    global documents_collection, document_status
    
    if document_status != "ready" or not documents_collection:
        raise HTTPException(
            status_code=400,
            detail="No document is ready for querying. Please upload a document first."
        )
    
    try:
        # Search using BM25
        bm25_results = bm25_retriever.search(request.query, k=5)
        
        if not bm25_results:
            return QueryResponse(
                response="I couldn't find relevant information using keyword search. Try a different query approach.",
                query=request.query,
                sources=[]
            )
        
        # Extract text chunks from BM25 results
        top_chunks = [result['text'] for result in bm25_results]
        
        # Generate response using Azure OpenAI
        response_text = await azure_openai_service.generate_response(
            query=request.query,
            context_chunks=top_chunks,
            document_filename=f"{len(documents_collection)} documents"
        )
        
        # Extract source documents
        source_documents = list(set([doc["filename"] for doc in documents_collection]))
        
        return QueryResponse(
            response=response_text,
            query=request.query,
            sources=top_chunks[:3],  # Return top 3 BM25 sources
            source_documents=source_documents,
            documents_searched=len(documents_collection)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing BM25 query: {str(e)}"
        )
@app.post("/query_contextual", response_model=QueryResponse)
async def query_document_contextual(request: QueryRequest):
    """Query documents using contextual retrieval"""
    global documents_collection, document_status
    
    if document_status != "ready" or not documents_collection:
        raise HTTPException(
            status_code=400,
            detail="No documents are ready for querying. Please upload documents first."
        )
    
    try:
        # Get query embedding
        query_embedding = await azure_openai_service.get_embeddings([request.query])
        
        if not query_embedding:
            raise HTTPException(
                status_code=500,
                detail="Could not generate embedding for query"
            )
        
        # Search using contextual retrieval
        contextual_results = contextual_retriever.search_contextual(
            query=request.query,
            query_embedding=query_embedding[0],
            k=5
        )
        
        if not contextual_results:
            return QueryResponse(
                response="I couldn't find relevant information using contextual search.",
                query=request.query,
                sources=[]
            )
        
        # Extract text chunks from contextual results
        top_chunks = [result['text'] for result in contextual_results]
        
        # Generate response using Azure OpenAI
        response_text = await azure_openai_service.generate_response(
            query=request.query,
            context_chunks=top_chunks,
            document_filename=f"{len(documents_collection)} documents"
        )
        
        # Extract source documents
        source_documents = list(set([doc["filename"] for doc in documents_collection]))
        
        return QueryResponse(
            response=response_text,
            query=request.query,
            sources=top_chunks[:3],  # Return top 3 contextual sources
            source_documents=source_documents,
            documents_searched=len(documents_collection)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing contextual query: {str(e)}"
        )
@app.post("/query_hybrid", response_model=QueryResponse)
async def query_document_hybrid(request: QueryRequest):
    """Query documents using hybrid retrieval (combines multiple methods)"""
    global documents_collection, document_status
    
    if document_status != "ready" or not documents_collection:
        raise HTTPException(
            status_code=400,
            detail="No documents are ready for querying. Please upload documents first."
        )
    
    try:
        # Get query embedding
        query_embedding = await azure_openai_service.get_embeddings([request.query])
        
        if not query_embedding:
            raise HTTPException(
                status_code=500,
                detail="Could not generate embedding for query"
            )
        
        # 1. Semantic search (vector store)
        semantic_results = vector_store.search_similar_with_metadata(query_embedding[0], k=8)
        
        # 2. BM25 keyword search
        bm25_results = bm25_retriever.search(request.query, k=8)
        
        # 3. Contextual search
        contextual_results = contextual_retriever.search_contextual(
            query=request.query,
            query_embedding=query_embedding[0],
            k=8
        )
        
        # Combine and score results
        all_results = []
        
        # Add semantic results with weight
        for i, result in enumerate(semantic_results):
            all_results.append({
                'text': result['text'],
                'score': result['similarity_score'] * 0.4,  # 40% weight
                'method': 'semantic',
                'rank': i + 1
            })
        
        # Add BM25 results with weight
        for i, result in enumerate(bm25_results):
            all_results.append({
                'text': result['text'],
                'score': result['bm25_score'] * 0.3,  # 30% weight
                'method': 'bm25',
                'rank': i + 1
            })
        
        # Add contextual results with weight
        for i, result in enumerate(contextual_results):
            all_results.append({
                'text': result['text'],
                'score': result['final_score'] * 0.3,  # 30% weight
                'method': 'contextual',
                'rank': i + 1
            })
        
        # Remove duplicates and sort by combined score
        unique_results = {}
        for result in all_results:
            text = result['text']
            if text in unique_results:
                # Combine scores from multiple methods
                unique_results[text]['score'] += result['score']
                unique_results[text]['methods'].append(result['method'])
            else:
                unique_results[text] = {
                    'text': text,
                    'score': result['score'],
                    'methods': [result['method']]
                }
        
        # Sort by combined score and take top results
        sorted_results = sorted(unique_results.values(), key=lambda x: x['score'], reverse=True)
        top_chunks = [result['text'] for result in sorted_results[:5]]
        
        if not top_chunks:
            return QueryResponse(
                response="I couldn't find relevant information using hybrid search.",
                query=request.query,
                sources=[]
            )
        
        # Generate response using Azure OpenAI
        response_text = await azure_openai_service.generate_response(
            query=request.query,
            context_chunks=top_chunks,
            document_filename=f"{len(documents_collection)} documents"
        )
        
        # Extract source documents
        source_documents = list(set([doc["filename"] for doc in documents_collection]))
        
        return QueryResponse(
            response=response_text,
            query=request.query,
            sources=top_chunks[:3],  # Return top 3 hybrid sources
            source_documents=source_documents,
            documents_searched=len(documents_collection)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing hybrid query: {str(e)}"
        )

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a specific document from the collection"""
    global documents_collection, document_status, total_chunks
    
    try:
        # Find document to delete
        doc_to_delete = next((doc for doc in documents_collection if doc["filename"] == filename), None)
        if not doc_to_delete:
            raise HTTPException(
                status_code=404,
                detail=f"Document '{filename}' not found"
            )
        
        # Remove document from collection
        documents_collection = [doc for doc in documents_collection if doc["filename"] != filename]
        total_chunks -= doc_to_delete["chunk_count"]
        
        # Update status if no documents left
        if not documents_collection:
            document_status = "none"
            total_chunks = 0
            # Clear all retrievers
            vector_store.clear()
            bm25_retriever.clear()
            contextual_retriever.clear()
        else:
            # Rebuild all retrievers with remaining documents
            vector_store.clear()
            bm25_retriever.clear()
            contextual_retriever.clear()
            
            all_chunks = []
            all_embeddings = []
            
            for doc in documents_collection:
                all_chunks.extend(doc["chunks"])
                # Note: We'd need to store embeddings to avoid regenerating them
                # For now, we'll regenerate them (this is a limitation)
            
            if all_chunks:
                # Regenerate embeddings for all remaining documents
                embeddings = await azure_openai_service.get_embeddings(all_chunks)
                vector_store.add_documents(all_chunks, embeddings)
                bm25_retriever.add_documents(all_chunks)
                contextual_retriever.add_documents(all_chunks, embeddings)
        
        return {
            "message": f"Document '{filename}' deleted successfully",
            "remaining_documents": len(documents_collection),
            "total_chunks": total_chunks
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )
@app.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    global documents_collection
    
    return {
        "documents": [
            {
                "filename": doc["filename"],
                "chunks": doc["chunk_count"],
                "upload_time": doc.get("upload_time", "unknown")
            }
            for doc in documents_collection
        ],
        "total_documents": len(documents_collection),
        "total_chunks": sum(doc["chunk_count"] for doc in documents_collection)
    }

@app.post("/reset")
async def reset_session():
    """Reset the current session"""
    global documents_collection, document_status, total_chunks
    
    try:
        # Clear vector store
        vector_store.clear()
        bm25_retriever.clear()
        contextual_retriever.clear()
        # Reset global state
        documents_collection = []
        document_status = "none"
        total_chunks = 0
        
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
        "document_processor": document_processor.is_ready(),
        "bm25_retriever": bm25_retriever.is_ready(),
        "contextual_retriever": contextual_retriever.is_ready()
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
