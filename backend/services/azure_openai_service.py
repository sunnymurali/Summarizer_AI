import os
import openai
from typing import List, Optional
import asyncio
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()
import logging


class AzureOpenAIService:
    """Service for interacting with Azure OpenAI API"""
    
    def __init__(self):
        # Initialize Azure OpenAI client
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        self.embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
        
        if not self.api_key or not self.endpoint:
            raise ValueError("Azure OpenAI API key and endpoint must be provided via environment variables")
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing AzureOpenAIService")
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a list of texts"""
        self.logger.info("Getting embeddings for %d texts", len(texts))
        try:
            if not texts:
                return []
            
            # Azure OpenAI has a limit on batch size, so we'll process in batches
            batch_size = 16
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.embedding_deployment
                )
                
                # Extract embeddings from response
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
            
        except Exception as e:
            raise Exception(f"Error getting embeddings: {str(e)}")
    
    async def generate_response(self, query: str, context_chunks: List[str], document_filename: str) -> str:
        """Generate a response based on query and context chunks"""
        self.logger.info("Generating response for query '%s' with %d context chunks", query, len(context_chunks))
        try:
            # Prepare context
            context = "\n\n".join(context_chunks)
            
            # Create system message
            system_message = f"""You are an AI assistant that helps analyze documents. 
            You have been provided with relevant excerpts from the document "{document_filename}".
            
            Instructions:
            1. Answer the user's question based on the provided context
            2. If the context doesn't contain relevant information, say so clearly
            3. Be specific and cite relevant parts of the document when possible
            4. If you're unsure about something, acknowledge the uncertainty
            5. Keep your response concise but informative
            
            Context from the document:
            {context}
            """
            
            # Create user message
            user_message = f"Question: {query}"
            
            # Generate response
            self.logger.info("Generating response using Azure OpenAI")
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=2500,
                temperature=0.3,
                top_p=0.95
            )
            
            self.logger.info("Received response from Azure OpenAI")
            self.logger.debug("Response: %s", response)
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error("Error generating response: %s", str(e))
            raise Exception(f"Error generating response: {str(e)}")
    


    async def rerank_documents(self, query: str, retrieved_docs: List[dict]) -> List[dict]:
        """Re-rank retrieved documents using GPT-4o for better relevance"""
        try:
            if not retrieved_docs:
                self.logger.info("No documents to rerank")
                return []
            
            # Prepare documents for reranking
            docs_text = ""
            for i, doc in enumerate(retrieved_docs):
                docs_text += f"Document {i+1}:\n{doc['text']}\n\n"
            
            # Create reranking prompt
            self.logger.info("Creating reranking prompt")
            system_message = """You are an expert document ranker. Given a user query and a list of document excerpts, 
            rank them by relevance to the query. Consider semantic similarity, context relevance, and how well each 
            document answers the query.

            Return your response as a JSON array of document IDs in order of relevance (most relevant first).
            Only return the JSON array, nothing else.
            
            Example format: [1, 3, 2, 4, 5]
            """
            
            user_message = f"""Query: {query}

            Documents to rank:
            {docs_text}

            Rank these documents by relevance to the query. Return only a JSON array of document numbers (1-{len(retrieved_docs)}) in order of relevance."""
            
            # Generate reranking
            self.logger.info("Generating reranking")
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            # Parse the ranking
            self.logger.info("Parsing reranking")
            try:
                raw_output = response.choices[0].message.content.strip()
                self.logger.info(f"LLM returned reranking: {raw_output}")
                ranking_result = json.loads(raw_output)
                self.logger.info(f"Parsed reranking: {ranking_result}")
                if isinstance(ranking_result, list):
                    ranking = ranking_result
                else:
                    # Handle case where response is wrapped in an object
                    ranking = ranking_result.get('ranking', list(range(1, len(retrieved_docs) + 1)))
            except json.JSONDecodeError:
                # Fallback to original order if JSON parsing fails
                self.logger.warning("JSON parsing failed, falling back to original order")
                ranking = list(range(1, len(retrieved_docs) + 1))
            
            # Reorder documents based on ranking
            self.logger.info("Reordering documents based on reranking")
            reranked_docs = []
            for rank_idx in ranking:
                if 1 <= rank_idx <= len(retrieved_docs):
                    doc_idx = rank_idx - 1  # Convert to 0-based index
                    reranked_doc = retrieved_docs[doc_idx].copy()
                    reranked_doc['rerank_score'] = len(ranking) - ranking.index(rank_idx)
                    reranked_docs.append(reranked_doc)
            self.logger.info(f"Reordered documents based on reranking: {reranked_docs}")
            return reranked_docs
            
        except Exception as e:
            # If reranking fails, return original order
            self.logger.warning(f"Reranking failed: {str(e)}")
            return retrieved_docs

    def is_configured(self) -> bool:
        """Check if Azure OpenAI service is properly configured"""
        self.logger.info("Checking if Azure OpenAI service is configured")
        try:
            return bool(self.api_key and self.endpoint and self.client)
        except:
            return False
    
    def get_model_info(self) -> dict:
        """Get information about the configured models"""
        self.logger.info("Getting information about the configured models")
        return {
            "chat_model": self.deployment_name,
            "embedding_model": self.embedding_deployment,
            "api_version": self.api_version,
            "endpoint": self.endpoint
        }
    
    async def test_connection(self) -> bool:
        """Test connection to Azure OpenAI service"""
        self.logger.info("Testing connection to Azure OpenAI service")
        try:
            # Test embedding
            test_embedding = await self.get_embeddings(["test"])
            if not test_embedding:
                return False
            
            # Test chat completion
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            return bool(response.choices[0].message.content)
            
        except Exception as e:
            logger.error("Connection test failed: %s", str(e))
            return False
