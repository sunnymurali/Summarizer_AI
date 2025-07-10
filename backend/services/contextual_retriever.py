import json
from typing import List, Dict, Any, Optional
import numpy as np

class ContextualRetriever:
    """Contextual retrieval service that considers document context"""
    
    def __init__(self):
        self.documents = []
        self.contextual_documents = []
        self.embeddings = []
        self.context_embeddings = []
        
    def _create_contextual_chunk(self, text: str, prev_text: str = "", next_text: str = "") -> str:
        """Create contextual chunk with surrounding context"""
        context_prefix = f"Previous context: {prev_text[-200:]}... " if prev_text else ""
        context_suffix = f" ...Next context: {next_text[:200]}" if next_text else ""
        
        return f"{context_prefix}Main content: {text}{context_suffix}"
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]]):
        """Add documents with contextual processing"""
        try:
            self.documents = documents
            self.embeddings = embeddings
            
            # Create contextual versions of documents
            self.contextual_documents = []
            for i, doc in enumerate(documents):
                # Get previous and next documents for context
                prev_doc = documents[i-1] if i > 0 else ""
                next_doc = documents[i+1] if i < len(documents) - 1 else ""
                
                # Create contextual chunk
                contextual_chunk = self._create_contextual_chunk(doc, prev_doc, next_doc)
                self.contextual_documents.append(contextual_chunk)
            
        except Exception as e:
            raise Exception(f"Error adding contextual documents: {str(e)}")
    
    def search_contextual(self, query: str, query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Search using contextual understanding"""
        try:
            if not self.documents or not self.embeddings:
                return []
            
            # Calculate contextual relevance scores
            results = []
            query_vec = np.array(query_embedding)
            
            for i, (doc, embedding) in enumerate(zip(self.documents, self.embeddings)):
                # Calculate similarity with original embedding
                doc_vec = np.array(embedding)
                similarity = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
                
                # Apply contextual boost
                contextual_score = self._calculate_contextual_boost(
                    query, doc, self.contextual_documents[i], i
                )
                
                # Combine scores
                final_score = float(similarity) * (1 + contextual_score)
                
                results.append({
                    'id': str(i),
                    'text': doc,
                    'contextual_text': self.contextual_documents[i],
                    'similarity_score': float(similarity),
                    'contextual_boost': contextual_score,
                    'final_score': final_score,
                    'rank': 0
                })
            
            # Sort by final score
            results.sort(key=lambda x: x['final_score'], reverse=True)
            
            # Set ranks
            for i, result in enumerate(results[:k]):
                result['rank'] = i + 1
            
            return results[:k]
            
        except Exception as e:
            raise Exception(f"Error in contextual search: {str(e)}")
    
    def _calculate_contextual_boost(self, query: str, doc: str, contextual_doc: str, position: int) -> float:
        """Calculate contextual relevance boost"""
        try:
            boost = 0.0
            
            # Position-based boost (earlier documents might be more important)
            if position < len(self.documents) * 0.1:  # First 10% of documents
                boost += 0.1
            
            # Length-based boost (longer documents might have more context)
            if len(doc) > 1000:
                boost += 0.05
            
            # Keyword overlap boost
            query_words = set(query.lower().split())
            doc_words = set(doc.lower().split())
            overlap = len(query_words.intersection(doc_words))
            boost += min(overlap * 0.02, 0.2)  # Max 0.2 boost
            
            # Context window boost (if query terms appear in surrounding context)
            context_words = set(contextual_doc.lower().split())
            context_overlap = len(query_words.intersection(context_words))
            boost += min(context_overlap * 0.01, 0.1)  # Max 0.1 boost
            
            return boost
            
        except Exception as e:
            return 0.0
    
    def get_contextual_summary(self, doc_index: int) -> Dict[str, Any]:
        """Get contextual summary for a document"""
        try:
            if doc_index < 0 or doc_index >= len(self.documents):
                return {}
            
            return {
                'original_text': self.documents[doc_index],
                'contextual_text': self.contextual_documents[doc_index],
                'position': doc_index,
                'total_documents': len(self.documents),
                'length': len(self.documents[doc_index])
            }
            
        except Exception as e:
            return {}
    
    def clear(self):
        """Clear contextual retriever"""
        self.documents = []
        self.contextual_documents = []
        self.embeddings = []
        self.context_embeddings = []
    
    def is_ready(self) -> bool:
        """Check if contextual retriever is ready"""
        return len(self.documents) > 0 and len(self.embeddings) > 0
    
    def get_document_count(self) -> int:
        """Get number of documents"""
        return len(self.documents)