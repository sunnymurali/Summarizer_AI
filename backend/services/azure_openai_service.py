import os
import openai
from typing import List, Optional
import asyncio
import json
from openai import AzureOpenAI

class AzureOpenAIService:
    """Service for interacting with Azure OpenAI API"""
    
    def __init__(self):
        # Initialize Azure OpenAI client
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        self.embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
        
        if not self.api_key or not self.endpoint:
            raise ValueError("Azure OpenAI API key and endpoint must be provided via environment variables")
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a list of texts"""
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
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,
                temperature=0.3,
                top_p=0.95
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
    
    def is_configured(self) -> bool:
        """Check if Azure OpenAI service is properly configured"""
        try:
            return bool(self.api_key and self.endpoint and self.client)
        except:
            return False
    
    def get_model_info(self) -> dict:
        """Get information about the configured models"""
        return {
            "chat_model": self.deployment_name,
            "embedding_model": self.embedding_deployment,
            "api_version": self.api_version,
            "endpoint": self.endpoint
        }
    
    async def test_connection(self) -> bool:
        """Test connection to Azure OpenAI service"""
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
            print(f"Connection test failed: {str(e)}")
            return False
