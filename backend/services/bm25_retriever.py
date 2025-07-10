import json
from typing import List, Tuple, Dict, Any
from rank_bm25 import BM25Okapi
import re

class BM25Retriever:
    """BM25-based keyword retrieval service"""
    
    def __init__(self):
        self.bm25 = None
        self.documents = []
        self.tokenized_corpus = []
        
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for BM25 processing"""
        # Convert to lowercase and split on whitespace and punctuation
        text = text.lower()
        # Remove punctuation and split on whitespace
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def add_documents(self, documents: List[str]):
        """Add documents to BM25 index"""
        try:
            self.documents = documents
            # Tokenize all documents
            self.tokenized_corpus = [self._tokenize(doc) for doc in documents]
            # Create BM25 index
            self.bm25 = BM25Okapi(self.tokenized_corpus)
            
        except Exception as e:
            raise Exception(f"Error adding documents to BM25: {str(e)}")
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search documents using BM25 scoring"""
        try:
            if not self.bm25 or not self.documents:
                return []
            
            # Tokenize query
            tokenized_query = self._tokenize(query)
            
            # Get BM25 scores for all documents
            doc_scores = self.bm25.get_scores(tokenized_query)
            
            # Create results with metadata
            results = []
            for i, score in enumerate(doc_scores):
                if score > 0:  # Only include documents with positive scores
                    results.append({
                        'id': str(i),
                        'text': self.documents[i],
                        'bm25_score': float(score),
                        'rank': 0  # Will be set after sorting
                    })
            
            # Sort by BM25 score (descending)
            results.sort(key=lambda x: x['bm25_score'], reverse=True)
            
            # Set ranks and return top k
            for i, result in enumerate(results[:k]):
                result['rank'] = i + 1
            
            return results[:k]
            
        except Exception as e:
            raise Exception(f"Error searching with BM25: {str(e)}")
    
    def get_top_keywords(self, query: str, k: int = 10) -> List[str]:
        """Get top keywords from query for debugging"""
        try:
            tokenized_query = self._tokenize(query)
            # Return unique tokens
            return list(set(tokenized_query))[:k]
            
        except Exception as e:
            raise Exception(f"Error getting keywords: {str(e)}")
    
    def clear(self):
        """Clear the BM25 index"""
        self.bm25 = None
        self.documents = []
        self.tokenized_corpus = []
    
    def is_ready(self) -> bool:
        """Check if BM25 retriever is ready"""
        return self.bm25 is not None and len(self.documents) > 0
    
    def get_document_count(self) -> int:
        """Get number of indexed documents"""
        return len(self.documents)