"""
ClipScore metrics implementation for DreamLayer.
Reuses ComfyUI's existing dependencies (transformers, torch, PIL).
Based on HELM's research-grade implementation.
"""

import os
import statistics
from typing import List, Dict, Any, Optional
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClipScoreCalculator:
    """Calculate ClipScore metrics for image-text pairs using ComfyUI's dependencies."""
    
    def __init__(self, model_name: str = "openai/clip-vit-large-patch14"):
        self.model_name = model_name
        self.model = None
        self.processor = None
        self._model_loaded = False
        
        # Define common image search paths for DreamLayer
        self.image_search_paths = [
            "Dream_Layer_Resources/output/",
            "dream_layer_backend/served_images/",
            "ComfyUI/output/",
            "ComfyUI/input/",
            "./"
        ]
        
    def _find_image_path(self, image_path: str) -> Optional[str]:
        """Find the actual path of an image, checking common DreamLayer directories."""
        # If it's already an absolute path and exists, use it
        if os.path.isabs(image_path) and os.path.exists(image_path):
            return image_path
        
        # If it's a relative path and exists, use it
        if os.path.exists(image_path):
            return image_path
        
        # Search in common DreamLayer directories
        for search_path in self.image_search_paths:
            full_path = os.path.join(search_path, image_path)
            if os.path.exists(full_path):
                logger.debug(f"Found image at: {full_path}")
                return full_path
        
        logger.warning(f"Image not found in any search path: {image_path}")
        return None
        
    def _load_model(self):
        """Lazy load CLIP model and processor."""
        if self._model_loaded:
            return
            
        try:
            logger.info(f"Loading CLIP model: {self.model_name}")
            self.model = CLIPModel.from_pretrained(self.model_name)
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            self.model.eval()
            
            # Move to GPU if available (following ComfyUI's pattern)
            if torch.cuda.is_available():
                self.model = self.model.cuda()
                logger.info("CLIP model loaded on GPU")
            else:
                logger.info("CLIP model loaded on CPU")
                
            self._model_loaded = True
            
        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}")
            self.model = None
            self.processor = None
            self._model_loaded = False
    
    def compute_clip_score(self, prompt: str, image_path: str) -> float:
        """Compute ClipScore for a single image-text pair."""
        self._load_model()
        
        if self.model is None or self.processor is None:
            logger.warning("CLIP model not available, returning 0.0")
            return 0.0
        
        try:
            # Find the actual image path
            actual_image_path = self._find_image_path(image_path)
            if actual_image_path is None:
                logger.warning(f"Image not found: {image_path}")
                return 0.0
            
            # Load and preprocess image
            image = Image.open(actual_image_path).convert('RGB')
            
            # Process inputs (handles tokenization and image preprocessing)
            # max_length=77 matches HELM's implementation (75 tokens + 2 special tokens)
            inputs = self.processor(
                text=[prompt], 
                images=[image], 
                return_tensors="pt", 
                padding=True, 
                truncation=True,
                max_length=77
            )
            
            # Move inputs to same device as model
            if torch.cuda.is_available() and next(self.model.parameters()).is_cuda:
                inputs = {k: v.cuda() if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}
            
            # Compute embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                
                # ClipScore is cosine similarity between text and image embeddings
                # Following HELM's approach
                clip_score = torch.cosine_similarity(
                    outputs.text_embeds, 
                    outputs.image_embeds, 
                    dim=1
                ).item()
            
            logger.debug(f"ClipScore for '{prompt}' + '{actual_image_path}': {clip_score:.4f}")
            return clip_score
            
        except Exception as e:
            logger.error(f"Error computing ClipScore for {image_path}: {e}")
            return 0.0
    
    def compute_metrics_for_batch(self, prompt: str, image_paths: List[str]) -> Dict[str, float]:
        """
        Compute ClipScore metrics for a batch of images with the same prompt.
        Returns metrics compatible with DreamLayer's CSV schema.
        """
        scores = []
        
        logger.info(f"Computing ClipScore for {len(image_paths)} images with prompt: '{prompt[:50]}...'")
        
        for image_path in image_paths:
            if image_path:  # Skip empty paths
                score = self.compute_clip_score(prompt, image_path)
                if score != 0.0:  # Only include valid scores
                    scores.append(score)
                    logger.debug(f"Valid score: {score:.4f} for {image_path}")
                else:
                    logger.warning(f"Zero score for {image_path}")
        
        # Return metrics following HELM's naming convention
        if not scores:
            logger.warning("No valid ClipScores computed - all scores were 0.0")
            return {
                'clip_score_mean': 0.0,
                'clip_score_median': 0.0,
                'clip_score_std': 0.0,
                'clip_score_max': 0.0,
                'clip_score_min': 0.0
            }
        
        metrics = {
            'clip_score_mean': statistics.mean(scores),
            'clip_score_median': statistics.median(scores),
            'clip_score_std': statistics.stdev(scores) if len(scores) > 1 else 0.0,
            'clip_score_max': max(scores),
            'clip_score_min': min(scores)
        }
        
        logger.info(f"ClipScore metrics computed: mean={metrics['clip_score_mean']:.4f}, "
                   f"max={metrics['clip_score_max']:.4f}, min={metrics['clip_score_min']:.4f}")
        
        return metrics


# Global instance for reuse across report generation
_clip_calculator = None

def get_clip_calculator() -> ClipScoreCalculator:
    """Get or create global ClipScore calculator instance."""
    global _clip_calculator
    if _clip_calculator is None:
        _clip_calculator = ClipScoreCalculator()
    return _clip_calculator
