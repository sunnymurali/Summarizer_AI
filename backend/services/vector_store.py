import numpy as np
import faiss
from typing import List, Optional, Tuple, Union
import pickle
import os
import logging

class VectorStore:
    """FAISS-based vector store for document embeddings"""
    
    def __init__(self, dimension: Optional[int] = None):  # Auto-detect embedding dimension
        self.dimension = dimension
        self.index: Optional[faiss.IndexFlatL2] = None
        self.documents = []
        self.embeddings = []
        self.is_initialized = False
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing VectorStore")
        
    def _initialize_index(self, dimension: Optional[int] = None):
        """Initialize FAISS index"""
        try:
            # Set dimension if provided
            if dimension is not None:
                self.dimension = dimension
            
            if self.dimension is None:
                raise ValueError("Dimension must be specified to initialize FAISS index")
            
            # Create FAISS index (using L2 distance)
            self.index = faiss.IndexFlatL2(self.dimension)
            self.is_initialized = True
            self.logger.info("Initialized FAISS index")
        except Exception as e:
            raise Exception(f"Error initializing FAISS index: {str(e)}")
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]]):
        """Add documents and their embeddings to the vector store"""
        try:
            if len(documents) != len(embeddings):
                raise ValueError("Number of documents must match number of embeddings")
            
            # Convert embeddings to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Auto-detect dimension from first embedding batch
            if not self.is_initialized:
                detected_dimension = embeddings_array.shape[1]
                self._initialize_index(detected_dimension)
            
            # Validate embedding dimensions
            if embeddings_array.shape[1] != self.dimension:
                raise ValueError(f"Embedding dimension mismatch. Expected {self.dimension}, got {embeddings_array.shape[1]}")
            
            # Add embeddings to FAISS index
            if self.index is not None:
                self.index.add(embeddings_array)
                self.logger.info("Added documents to FAISS index")
            else:
                raise Exception("FAISS index not initialized")
            
            # Store documents and embeddings
            self.documents.extend(documents)
            self.embeddings.extend(embeddings)
            self.logger.info("Added documents to vector store")
            
        except Exception as e:
            raise Exception(f"Error adding documents to vector store: {str(e)}")
    
    def search_similar(self, query_embedding: List[float], k: int = 5) -> List[str]:
        """Search for similar documents"""
        try:
            if not self.is_initialized or self.index is None:
                self.logger.info("Vector store not initialized - cannot search for similar documents")
                return []
            
            if len(self.documents) == 0:
                self.logger.info("No documents to search for similar documents")
                return []
            
            # Convert query embedding to numpy array
            query_array = np.array([query_embedding], dtype=np.float32)
            
            # Validate query embedding dimension
            if query_array.shape[1] != self.dimension:
                raise ValueError(f"Query embedding dimension mismatch. Expected {self.dimension}, got {query_array.shape[1]}")
            
            # Search for similar vectors
            k = min(k, len(self.documents))  # Don't search for more than we have
            if self.index is not None:
                distances, indices = self.index.search(query_array, k)
                self.logger.info("Searched for similar documents")
            else:
                return []
            
            # Return corresponding documents
            similar_documents = []
            for idx in indices[0]:
                if 0 <= idx < len(self.documents):
                    similar_documents.append(self.documents[idx])
            
            self.logger.info("Found similar documents")
            return similar_documents
            
        except Exception as e:
            raise Exception(f"Error searching similar documents: {str(e)}")
    
    def get_similarity_scores(self, query_embedding: List[float], k: int = 5) -> List[Tuple[str, float]]:
        """Get similar documents with similarity scores"""
        try:
            if not self.is_initialized or self.index is None:
                self.logger.info("Vector store not initialized - cannot get similarity scores")
                return []
            
            if len(self.documents) == 0:
                self.logger.info("No documents to get similarity scores")
                return []
            
            # Convert query embedding to numpy array
            query_array = np.array([query_embedding], dtype=np.float32)
            
            # Search for similar vectors
            k = min(k, len(self.documents))
            if self.index is not None:
                distances, indices = self.index.search(query_array, k)
                self.logger.info("Searched for similar documents")
            else:
                return []
            
            # Convert distances to similarity scores (lower distance = higher similarity)
            # Using negative exponential to convert L2 distance to similarity score
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if 0 <= idx < len(self.documents):
                    similarity = np.exp(-dist)  # Convert distance to similarity
                    results.append((self.documents[idx], float(similarity)))
            
            self.logger.info("Computed similarity scores")
            return results
            
        except Exception as e:
            raise Exception(f"Error getting similarity scores: {str(e)}")
    def search_similar_with_metadata(self, query_embedding: List[float], k: int = 10) -> List[dict]:
        """Search for similar documents and return with metadata for reranking"""
        try:
            if not self.is_initialized or self.index is None:
                return []
            
            if len(self.documents) == 0:
                return []
            
            # Convert query embedding to numpy array
            query_array = np.array([query_embedding], dtype=np.float32)
            
            # Validate query embedding dimension
            if query_array.shape[1] != self.dimension:
                raise ValueError(f"Query embedding dimension mismatch. Expected {self.dimension}, got {query_array.shape[1]}")
            
            # Search for similar vectors
            k = min(k, len(self.documents))
            if self.index is not None:
                distances, indices = self.index.search(query_array, k)
            else:
                return []
            
            # Return documents with metadata
            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if 0 <= idx < len(self.documents):
                    doc_data = {
                        'id': str(idx),
                        'text': self.documents[idx],
                        'similarity_score': float(np.exp(-dist)),
                        'distance': float(dist),
                        'rank': i + 1
                    }
                    results.append(doc_data)
            
            return results
            
        except Exception as e:
            raise Exception(f"Error searching similar documents with metadata: {str(e)}")

            
    def clear(self):
        """Clear all documents and embeddings from the vector store"""
        try:
            self.documents = []
            self.embeddings = []
            if self.is_initialized and self.index is not None:
                self.index.reset()
                self.logger.info("Reset FAISS index")
                
        except Exception as e:
            raise Exception(f"Error clearing vector store: {str(e)}")
    
    def get_document_count(self) -> int:
        """Get the number of documents in the vector store"""
        return len(self.documents)
    
    def is_ready(self) -> bool:
        """Check if vector store is ready for operations"""
        return self.is_initialized and len(self.documents) > 0
    
    def save_to_file(self, filepath: str):
        """Save vector store to file"""
        try:
            data = {
                'documents': self.documents,
                'embeddings': self.embeddings,
                'dimension': self.dimension
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
                self.logger.info("Saved vector store to file")
            
            # Save FAISS index
            if self.index is not None:
                faiss.write_index(self.index, filepath + '.faiss')
                self.logger.info("Saved FAISS index to file")
                
        except Exception as e:
            raise Exception(f"Error saving vector store: {str(e)}")
    
    def load_from_file(self, filepath: str):
        """Load vector store from file"""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            self.documents = data['documents']
            self.embeddings = data['embeddings']
            self.dimension = data['dimension']
            self.logger.info("Loaded vector store from file")
            
            # Load FAISS index
            if os.path.exists(filepath + '.faiss'):
                self.index = faiss.read_index(filepath + '.faiss')
                self.is_initialized = True
                self.logger.info("Loaded FAISS index from file")
            else:
                self._initialize_index()
                if self.embeddings and self.index is not None:
                    embeddings_array = np.array(self.embeddings, dtype=np.float32)
                    self.index.add(embeddings_array)
                    self.logger.info("Initialized FAISS index")
                    
        except Exception as e:
            raise Exception(f"Error loading vector store: {str(e)}")
