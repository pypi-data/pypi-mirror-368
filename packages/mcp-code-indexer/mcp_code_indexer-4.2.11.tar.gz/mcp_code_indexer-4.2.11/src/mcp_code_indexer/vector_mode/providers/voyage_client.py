"""
Voyage AI client for embedding generation using official SDK.

Provides clean integration with Voyage AI's embedding API for generating
high-quality code embeddings using the voyage-code-2 model.
"""

import logging
from typing import List, Dict, Any
import voyageai

from ..config import VectorConfig

logger = logging.getLogger(__name__)

class VoyageClient:
    """Clean Voyage AI client using official SDK."""
    
    def __init__(self, api_key: str, model: str = "voyage-code-2"):
        self.api_key = api_key
        self.model = model
        self._embedding_dimension: int | None = None
        
        # Initialize official Voyage AI client
        self.client = voyageai.Client(api_key=api_key)
        logger.info(f"Initialized Voyage AI client with model {model}")
    
    def health_check(self) -> bool:
        """Check if Voyage AI service is healthy."""
        try:
            result = self.client.embed(["test"], model=self.model, input_type="query")
            return len(result.embeddings) > 0
        except Exception as e:
            logger.warning(f"Voyage AI health check failed: {e}")
            return False
    
    def generate_embeddings(
        self,
        texts: List[str],
        input_type: str = "document",
        **kwargs
    ) -> List[List[float]]:
        """Generate embeddings for texts using official SDK."""
        if not texts:
            return []
        
        logger.info(f"Generating embeddings for {len(texts)} texts using {self.model}")
        
        try:
            result = self.client.embed(
                texts=texts,
                model=self.model,
                input_type=input_type,
                truncation=True
            )
            
            # Log usage if available
            if hasattr(result, 'usage') and result.usage:
                logger.debug(f"Token usage: {result.usage.total_tokens}")
            
            logger.info(f"Successfully generated {len(result.embeddings)} embeddings")
            return result.embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise RuntimeError(f"Embedding generation failed: {e}")
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        if self._embedding_dimension is not None:
            return self._embedding_dimension
        
        # Generate a test embedding to determine dimension
        try:
            test_embeddings = self.generate_embeddings(["test"], input_type="query")
            if test_embeddings:
                self._embedding_dimension = len(test_embeddings[0])
                logger.info(f"Detected embedding dimension: {self._embedding_dimension}")
                return self._embedding_dimension
        except Exception as e:
            logger.warning(f"Could not determine embedding dimension: {e}")
        
        # Default dimensions for known Voyage models
        model_dimensions = {
            "voyage-code-2": 1536,
            "voyage-2": 1024,
            "voyage-large-2": 1536,
            "voyage-3": 1024,
        }
        
        self._embedding_dimension = model_dimensions.get(self.model, 1536)
        logger.info(f"Using default embedding dimension: {self._embedding_dimension}")
        return self._embedding_dimension
    
    def estimate_cost(self, texts: List[str]) -> Dict[str, Any]:
        """Estimate the cost of embedding generation."""
        # Rough token estimation (4 chars per token)
        total_tokens = sum(len(text) // 4 for text in texts)
        
        # Voyage AI pricing (approximate, may change)
        cost_per_1k_tokens = 0.00013  # voyage-code-2 pricing
        estimated_cost = (total_tokens / 1000) * cost_per_1k_tokens
        
        return {
            "total_tokens": total_tokens,
            "total_texts": len(texts),
            "estimated_cost_usd": round(estimated_cost, 6),
            "model": self.model,
        }

def create_voyage_client(config: VectorConfig) -> VoyageClient:
    """Create a Voyage client from configuration."""
    if not config.voyage_api_key:
        raise ValueError("VOYAGE_API_KEY is required for embedding generation")
    
    return VoyageClient(
        api_key=config.voyage_api_key,
        model=config.embedding_model,
    )
