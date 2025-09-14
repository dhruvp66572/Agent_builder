import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        # Initialize Google AI as primary embedding provider
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        genai.configure(api_key=google_api_key)
        
        # Set default embedding model
        self.default_model = "models/embedding-001"
    
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Google Gemini"""
        try:
            embeddings = []
            
            # Process texts in batches to avoid rate limits
            batch_size = 10
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = await self._process_batch(batch)
                embeddings.extend(batch_embeddings)
                
                # Add small delay between batches to respect rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating Gemini embeddings: {str(e)}")
            raise Exception(f"Error generating embeddings: {str(e)}")
    
    async def _process_batch(self, texts: List[str]) -> List[List[float]]:
        """Process a batch of texts for embedding generation"""
        embeddings = []
        
        for text in texts:
            try:
                # Clean and validate text
                clean_text = self._clean_text(text)
                if not clean_text:
                    # Use zero vector for empty text
                    embeddings.append([0.0] * 768)  # Gemini embedding dimension
                    continue
                
                result = genai.embed_content(
                    model=self.default_model,
                    content=clean_text,
                    task_type="retrieval_document"
                )
                embeddings.append(result["embedding"])
                
            except Exception as e:
                logger.warning(f"Error processing text for embedding: {str(e)}")
                # Use zero vector as fallback
                embeddings.append([0.0] * 768)
        
        return embeddings
    
    def _clean_text(self, text: str) -> str:
        """Clean and prepare text for embedding"""
        if not text or not isinstance(text, str):
            return ""
        
        # Remove excessive whitespace and normalize
        clean_text = ' '.join(text.strip().split())
        
        # Truncate if too long (Gemini has token limits)
        max_length = 30000  # Conservative limit for Gemini
        if len(clean_text) > max_length:
            clean_text = clean_text[:max_length]
            logger.warning(f"Text truncated to {max_length} characters for embedding")
        
        return clean_text
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for search queries"""
        try:
            clean_query = self._clean_text(query)
            if not clean_query:
                raise ValueError("Query text is empty or invalid")
            
            result = genai.embed_content(
                model=self.default_model,
                content=clean_query,
                task_type="retrieval_query"  # Optimized for query embeddings
            )
            return result["embedding"]
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise Exception(f"Error generating query embedding: {str(e)}")
    
    async def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the current model"""
        return 768  # Gemini embedding-001 produces 768-dimensional embeddings
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current embedding model"""
        return {
            "provider": "google_gemini",
            "model": self.default_model,
            "dimension": 768,
            "max_input_length": 30000,
            "task_types": ["retrieval_document", "retrieval_query"]
        }