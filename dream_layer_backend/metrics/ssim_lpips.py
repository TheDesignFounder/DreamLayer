"""
SSIM and LPIPS Metrics Module for DreamLayer AI

Provides structural similarity and perceptual quality metrics for image assessment.
"""

import logging
from typing import Optional, Tuple, Union
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

# Pinned model information
LPIPS_MODEL_ID = "alex"  # Default LPIPS network
LPIPS_MODEL_HASH = "sha256:lpips_alex_v0.1"  # Placeholder hash

# SSIM availability
try:
    from skimage.metrics import structural_similarity as ssim
    SSIM_AVAILABLE = True
except ImportError:
    SSIM_AVAILABLE = False
    logger.warning("SSIM not available. Install with: pip install scikit-image")

# LPIPS availability
try:
    import lpips
    LPIPS_AVAILABLE = True
except ImportError:
    LPIPS_AVAILABLE = False
    logger.warning("LPIPS not available. Install with: pip install lpips")


class SSIMScorer:
    """Structural Similarity Index scorer."""
    
    def __init__(self):
        self.available = SSIM_AVAILABLE
        if not self.available:
            logger.warning("SSIM not available - install scikit-image")
    
    def compute_ssim(
        self, 
        img_a: Union[np.ndarray, Image.Image], 
        img_b: Union[np.ndarray, Image.Image],
        **kwargs
    ) -> Optional[float]:
        """
        Compute SSIM between two images.
        
        Args:
            img_a: First image (numpy array or PIL Image)
            img_b: Second image (numpy array or PIL Image)
            **kwargs: Additional SSIM parameters
            
        Returns:
            SSIM score (0.0 to 1.0, higher is better) or None if SSIM not available
        """
        if not self.available:
            logger.warning("SSIM not available - returning None")
            return None
        
        try:
            # Convert to numpy arrays
            if isinstance(img_a, Image.Image):
                img_a = np.array(img_a)
            if isinstance(img_b, Image.Image):
                img_b = np.array(img_b)
            
            # Ensure same shape
            if img_a.shape != img_b.shape:
                logger.warning("Image shapes don't match, resizing img_b to match img_a")
                from skimage.transform import resize
                img_b = resize(img_b, img_a.shape, preserve_range=True)
            
            # Convert to grayscale if needed
            if len(img_a.shape) == 3 and img_a.shape[2] == 3:
                from skimage.color import rgb2gray
                img_a = rgb2gray(img_a)
                img_b = rgb2gray(img_b)
            
            # Set data_range based on image type
            if img_a.dtype == np.uint8:
                data_range = 255
            elif img_a.dtype == np.float32 or img_a.dtype == np.float64:
                data_range = 1.0
            else:
                data_range = img_a.max() - img_a.min()
            
            # Compute SSIM with proper data_range
            score = ssim(img_a, img_b, data_range=data_range, **kwargs)
            return float(score)
            
        except Exception as e:
            logger.error(f"Error computing SSIM: {e}")
            return None
    
    def get_info(self) -> dict:
        """Get information about SSIM availability."""
        return {
            "available": self.available,
            "dependencies": {
                "scikit-image": "Available" if SSIM_AVAILABLE else "Not installed"
            }
        }


class LPIPSScorer:
    """Learned Perceptual Image Patch Similarity scorer."""
    
    def __init__(self, net: str = LPIPS_MODEL_ID):
        self.net = net
        self.available = LPIPS_AVAILABLE
        self.model = None
        
        if self.available:
            self._load_model()
        else:
            logger.warning("LPIPS not available - install lpips")
    
    def _load_model(self) -> None:
        """Load LPIPS model."""
        try:
            logger.info(f"Loading LPIPS model: {self.net}")
            self.model = lpips.LPIPS(net=self.net)
            logger.info("LPIPS model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load LPIPS model: {e}")
            self.model = None
            self.available = False
    
    def compute_lpips(
        self, 
        img_a: Union[np.ndarray, Image.Image], 
        img_b: Union[np.ndarray, Image.Image],
        net: Optional[str] = None
    ) -> Optional[float]:
        """
        Compute LPIPS between two images.
        
        Args:
            img_a: First image (numpy array or PIL Image)
            img_b: Second image (numpy array or PIL Image)
            net: LPIPS network to use (optional)
            
        Returns:
            LPIPS score (0.0 is identical, higher is more different) or None if LPIPS not available
        """
        if not self.available or self.model is None:
            logger.warning("LPIPS not available - returning None")
            return None
        
        try:
            # Convert to numpy arrays if needed
            if isinstance(img_a, Image.Image):
                img_a = np.array(img_a)
            if isinstance(img_b, Image.Image):
                img_b = np.array(img_b)
            
            # Ensure images are in the right format for LPIPS
            if len(img_a.shape) == 3 and img_a.shape[2] == 3:
                # Convert to RGB format expected by LPIPS
                img_a = img_a.transpose(2, 0, 1)  # HWC to CHW
                img_b = img_b.transpose(2, 0, 1)  # HWC to CHW
            else:
                # Grayscale - convert to RGB
                img_a = np.stack([img_a] * 3, axis=0)
                img_b = np.stack([img_b] * 3, axis=0)
            
            # Normalize to [-1, 1] range
            img_a = (img_a / 127.5) - 1.0
            img_b = (img_b / 127.5) - 1.0
            
            # Convert to torch tensors
            import torch
            img_a_tensor = torch.from_numpy(img_a).float().unsqueeze(0)
            img_b_tensor = torch.from_numpy(img_b).float().unsqueeze(0)
            
            # Compute LPIPS
            with torch.no_grad():
                score = self.model(img_a_tensor, img_b_tensor)
                return float(score.item())
                
        except Exception as e:
            logger.error(f"Error computing LPIPS: {e}")
            return None
    
    def get_info(self) -> dict:
        """Get information about LPIPS availability."""
        return {
            "available": self.available,
            "net": self.net,
            "dependencies": {
                "lpips": "Available" if LPIPS_AVAILABLE else "Not installed"
            }
        }


class QualityMetrics:
    """Combined quality metrics calculator."""
    
    def __init__(self):
        self.ssim_scorer = SSIMScorer()
        self.lpips_scorer = LPIPSScorer()
    
    def compute_all_metrics(
        self, 
        img_a: Union[np.ndarray, Image.Image], 
        img_b: Union[np.ndarray, Image.Image]
    ) -> dict:
        """
        Compute all available quality metrics between two images.
        
        Args:
            img_a: First image
            img_b: Second image
            
        Returns:
            Dictionary with metric results
        """
        results = {}
        
        # Compute SSIM
        if self.ssim_scorer.available:
            results["ssim"] = self.ssim_scorer.compute_ssim(img_a, img_b)
        else:
            results["ssim"] = None
        
        # Compute LPIPS
        if self.lpips_scorer.available:
            results["lpips"] = self.lpips_scorer.compute_lpips(img_a, img_b)
        else:
            results["lpips"] = None
        
        return results
    
    def get_metrics_info(self) -> dict:
        """Get information about available metrics."""
        return {
            "ssim": self.ssim_scorer.get_info(),
            "lpips": self.lpips_scorer.get_info()
        }


# Global instances
_ssim_scorer: Optional[SSIMScorer] = None
_lpips_scorer: Optional[LPIPSScorer] = None
_quality_metrics: Optional[QualityMetrics] = None


def get_ssim_scorer() -> SSIMScorer:
    """Get the global SSIM scorer instance."""
    global _ssim_scorer
    if _ssim_scorer is None:
        _ssim_scorer = SSIMScorer()
    return _ssim_scorer


def get_lpips_scorer() -> LPIPSScorer:
    """Get the global LPIPS scorer instance."""
    global _lpips_scorer
    if _lpips_scorer is None:
        _lpips_scorer = LPIPSScorer()
    return _lpips_scorer


def get_quality_metrics() -> QualityMetrics:
    """Get the global quality metrics instance."""
    global _quality_metrics
    if _quality_metrics is None:
        _quality_metrics = QualityMetrics()
    return _quality_metrics


def compute_ssim(
    img_a: Union[np.ndarray, Image.Image], 
    img_b: Union[np.ndarray, Image.Image]
) -> Optional[float]:
    """
    Convenience function for computing SSIM.
    
    Args:
        img_a: First image
        img_b: Second image
        
    Returns:
        SSIM score or None if SSIM not available
    """
    scorer = get_ssim_scorer()
    return scorer.compute_ssim(img_a, img_b)


def compute_lpips(
    img_a: Union[np.ndarray, Image.Image], 
    img_b: Union[np.ndarray, Image.Image],
    net: str = "alex"
) -> Optional[float]:
    """
    Convenience function for computing LPIPS.
    
    Args:
        img_a: First image
        img_b: Second image
        net: LPIPS network to use
        
    Returns:
        LPIPS score or None if LPIPS not available
    """
    scorer = get_lpips_scorer()
    return scorer.compute_lpips(img_a, img_b, net)


def compute_all_quality_metrics(
    img_a: Union[np.ndarray, Image.Image], 
    img_b: Union[np.ndarray, Image.Image]
) -> dict:
    """
    Convenience function for computing all quality metrics.
    
    Args:
        img_a: First image
        img_b: Second image
        
    Returns:
        Dictionary with all metric results
    """
    metrics = get_quality_metrics()
    return metrics.compute_all_metrics(img_a, img_b)
