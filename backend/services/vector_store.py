import numpy as np
import faiss
from typing import List, Optional, Tuple
import pickle
import os

class VectorStore:
    """FAISS-based vector store for document embeddings"""
    
    def __init__(self, dimension: int = 1536):  # Azure OpenAI embedding dimension
        self.dimension = dimension
        self.index = None
        self.documents = []
        self.embeddings = []
        self.is_initialized = False
        
    def _initialize_index(self):
        """Initialize FAISS index"""
        try:
            # Create FAISS index (using L2 distance)
            self.index = faiss.IndexFlatL2(self.dimension)
            self.is_initialized = True
        except Exception as e:
            raise Exception(f"Error initializing FAISS index: {str(e)}")
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]]):
        """Add documents and their embeddings to the vector store"""
        try:
            if not self.is_initialized:
                self._initialize_index()
            
            if len(documents) != len(embeddings):
                raise ValueError("Number of documents must match number of embeddings")
            
            # Convert embeddings to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Validate embedding dimensions
            if embeddings_array.shape[1] != self.dimension:
                raise ValueError(f"Embedding dimension mismatch. Expected {self.dimension}, got {embeddings_array.shape[1]}")
            
            # Add embeddings to FAISS index
            self.index.add(embeddings_array)
            
            # Store documents and embeddings
            self.documents.extend(documents)
            self.embeddings.extend(embeddings)
            
        except Exception as e:
            raise Exception(f"Error adding documents to vector store: {str(e)}")
    
    def search_similar(self, query_embedding: List[float], k: int = 5) -> List[str]:
        """Search for similar documents"""
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
            k = min(k, len(self.documents))  # Don't search for more than we have
            distances, indices = self.index.search(query_array, k)
            
            # Return corresponding documents
            similar_documents = []
            for idx in indices[0]:
                if 0 <= idx < len(self.documents):
                    similar_documents.append(self.documents[idx])
            
            return similar_documents
            
        except Exception as e:
            raise Exception(f"Error searching similar documents: {str(e)}")
    
    def get_similarity_scores(self, query_embedding: List[float], k: int = 5) -> List[Tuple[str, float]]:
        """Get similar documents with similarity scores"""
        try:
            if not self.is_initialized or self.index is None:
                return []
            
            if len(self.documents) == 0:
                return []
            
            # Convert query embedding to numpy array
            query_array = np.array([query_embedding], dtype=np.float32)
            
            # Search for similar vectors
            k = min(k, len(self.documents))
            distances, indices = self.index.search(query_array, k)
            
            # Convert distances to similarity scores (lower distance = higher similarity)
            # Using negative exponential to convert L2 distance to similarity score
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if 0 <= idx < len(self.documents):
                    similarity = np.exp(-dist)  # Convert distance to similarity
                    results.append((self.documents[idx], float(similarity)))
            
            return results
            
        except Exception as e:
            raise Exception(f"Error getting similarity scores: {str(e)}")
    
    def clear(self):
        """Clear all documents and embeddings from the vector store"""
        try:
            self.documents = []
            self.embeddings = []
            if self.is_initialized:
                self.index.reset()
                
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
            
            # Save FAISS index
            if self.index is not None:
                faiss.write_index(self.index, filepath + '.faiss')
                
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
            
            # Load FAISS index
            if os.path.exists(filepath + '.faiss'):
                self.index = faiss.read_index(filepath + '.faiss')
                self.is_initialized = True
            else:
                self._initialize_index()
                if self.embeddings:
                    embeddings_array = np.array(self.embeddings, dtype=np.float32)
                    self.index.add(embeddings_array)
                    
        except Exception as e:
            raise Exception(f"Error loading vector store: {str(e)}")
