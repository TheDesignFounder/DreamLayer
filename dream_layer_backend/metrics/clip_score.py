"""
CLIP Score Module for DreamLayer AI

Provides CLIP-based text-image similarity scoring for quality assessment.
"""

import logging
from typing import List, Optional, Tuple
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

# Pinned model information
CLIP_MODEL_ID = "openai/clip-vit-large-patch14"
CLIP_MODEL_HASH = "sha256:6c7ba7f6"  # Placeholder hash

try:
    import torch
    import transformers
    from transformers import CLIPProcessor, CLIPModel
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    logger.warning("CLIP dependencies not available. Install with: pip install transformers torch")


class CLIPScorer:
    """CLIP-based text-image similarity scorer."""
    
    def __init__(self, model_id: str = CLIP_MODEL_ID):
        self.model_id = model_id
        self.model = None
        self.processor = None
        self.device = None
        
        if CLIP_AVAILABLE:
            self._load_model()
        else:
            logger.warning("CLIP not available - install required dependencies")
    
    def _load_model(self) -> None:
        """Load CLIP model and processor."""
        try:
            logger.info(f"Loading CLIP model: {self.model_id}")
            
            # Set device
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {self.device}")
            
            # Load model and processor
            self.model = CLIPModel.from_pretrained(self.model_id).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(self.model_id)
            
            logger.info("CLIP model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}")
            self.model = None
            self.processor = None
    
    def clip_text_image_similarity(
        self, 
        images: List[Image.Image], 
        prompts: List[str], 
        batch_size: int = 8
    ) -> List[Optional[float]]:
        """
        Compute CLIP similarity scores between text prompts and images.
        
        Args:
            images: List of PIL images
            prompts: List of text prompts
            batch_size: Batch size for processing
            
        Returns:
            List of similarity scores (0.0 to 1.0) or None if CLIP not available
        """
        if not CLIP_AVAILABLE or self.model is None:
            logger.warning("CLIP not available - returning None scores")
            return [None] * len(images)
        
        if len(images) != len(prompts):
            raise ValueError("Number of images must match number of prompts")
        
        scores = []
        
        try:
            # Process in batches
            for i in range(0, len(images), batch_size):
                batch_images = images[i:i + batch_size]
                batch_prompts = prompts[i:i + batch_size]
                
                # Process batch
                batch_scores = self._process_batch(batch_images, batch_prompts)
                scores.extend(batch_scores)
                
        except Exception as e:
            logger.error(f"Error computing CLIP scores: {e}")
            # Return None on error
            scores = [None] * len(images)
        
        return scores
    
    def _process_batch(
        self, 
        images: List[Image.Image], 
        prompts: List[str]
    ) -> List[float]:
        """Process a batch of images and prompts."""
        try:
            # Prepare inputs
            inputs = self.processor(
                text=prompts,
                images=images,
                return_tensors="pt",
                padding=True,
                truncation=True
            ).to(self.device)
            
            # Get embeddings
            with torch.no_grad():
                text_features = self.model.get_text_features(**inputs)
                image_features = self.model.get_image_features(**inputs)
                
                # Normalize features
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                
                # Compute cosine similarity
                similarity = (text_features @ image_features.T).diagonal()
                
                # Convert to list and ensure values are in [0, 1]
                scores = similarity.cpu().numpy().tolist()
                scores = [max(0.0, min(1.0, (score + 1.0) / 2.0)) for score in scores]
                
                return scores
                
        except Exception as e:
            logger.error(f"Error processing CLIP batch: {e}")
            return [None] * len(images)
    
    def get_model_info(self) -> dict:
        """Get information about the CLIP model."""
        return {
            "model_id": self.model_id,
            "model_hash": self.model_hash,
            "available": CLIP_AVAILABLE and self.model is not None,
            "device": self.device if CLIP_AVAILABLE else None
        }
    
    @property
    def model_hash(self) -> str:
        """Get the model hash."""
        return CLIP_MODEL_HASH


def get_clip_scorer() -> Optional[CLIPScorer]:
    """Get a CLIP scorer instance."""
    if CLIP_AVAILABLE:
        return CLIPScorer()
    return None


def clip_text_image_similarity(
    images: List[Image.Image], 
    prompts: List[str], 
    batch_size: int = 8
) -> List[Optional[float]]:
    """
    Convenience function for computing CLIP similarity scores.
    
    Args:
        images: List of PIL images
        prompts: List of text prompts
        batch_size: Batch size for processing
        
    Returns:
        List of similarity scores (0.0 to 1.0) or None if CLIP not available
    """
    scorer = get_clip_scorer()
    if scorer:
        return scorer.clip_text_image_similarity(images, prompts, batch_size)
    else:
        logger.warning("CLIP not available - returning None scores")
        return [None] * len(images)
