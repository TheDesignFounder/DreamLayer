"""
Enhanced FID Integration with Database
Handles FID calculation with proper path resolution using database
Follows the exact pattern of clip_integration.py
"""

import os
import logging
import numpy as np
from typing import Optional, Dict, Any, List
from queries import DreamLayerQueries

# Try to import torch, but make it optional
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseFidCalculator:
    """FID calculator that uses database for path resolution"""
    
    def __init__(self):
        self.queries = DreamLayerQueries()
        self.fid_calculator = None
        self._initialize_fid_calculator()
    
    def _initialize_fid_calculator(self):
        """Initialize the FID calculator"""
        try:
            # Import FID calculation utilities
            from torchmetrics.image.fid import FrechetInceptionDistance
            import torch
            from PIL import Image
            import torchvision.transforms as transforms
            
            # Initialize FID metric
            self.fid_metric = FrechetInceptionDistance(feature=2048, normalize=True)
            
            # Image preprocessing pipeline (Inception-V3 requirements)
            self.transform = transforms.Compose([
                transforms.Resize(299),
                transforms.CenterCrop(299),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            # Load dataset statistics
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from datasets.dataset_utils import get_dataset_stats, ensure_cifar10_stats
            
            # Ensure CIFAR-10 stats exist
            if ensure_cifar10_stats():
                self.dataset_stats = get_dataset_stats('cifar10')
                if self.dataset_stats:
                    logger.info("FID calculator initialized successfully with CIFAR-10 stats")
                    self.fid_calculator = True
                else:
                    logger.error("Failed to load dataset statistics")
                    self.fid_calculator = False
            else:
                logger.error("Failed to ensure CIFAR-10 stats exist")
                self.fid_calculator = False
                
        except ImportError as e:
            logger.error(f"Could not import FID dependencies: {e}")
            logger.error("Install with: pip install torchmetrics torch torchvision")
            self.fid_calculator = False
        except Exception as e:
            logger.error(f"Error initializing FID calculator: {e}")
            self.fid_calculator = False
    
    def _preprocess_image(self, image_path: str) -> Optional['torch.Tensor']:
        """Preprocess image for Inception-V3"""
        try:
            if not TORCH_AVAILABLE:
                logger.error("PyTorch not available")
                return None
                
            from PIL import Image
            
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            # Resize and crop for Inception-V3
            image = image.resize((299, 299))
            
            # Convert to tensor as uint8 (0-255 range) for FiD metric
            import torch
            tensor = torch.from_numpy(np.array(image)).permute(2, 0, 1).unsqueeze(0).to(torch.uint8)
            return tensor
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {e}")
            return None
    
    def _compute_fid_from_images(self, image_paths: List[str]) -> Optional[float]:
        """Compute FID score from list of image paths"""
        try:
            import torch
            
            if not self.dataset_stats:
                logger.error("No dataset statistics available")
                return None
            
            mu_real, sigma_real = self.dataset_stats
            
            # Process all images
            image_tensors = []
            for image_path in image_paths:
                tensor = self._preprocess_image(image_path)
                if tensor is not None:
                    image_tensors.append(tensor)
            
            if len(image_tensors) == 0:
                return -1.0
            
            # Concatenate all images
            batch_tensor = torch.cat(image_tensors, dim=0)
            
            # Extract features using FID metric's inception model
            with torch.no_grad():
                features = self.fid_metric.inception(batch_tensor)
                features = features.cpu().numpy()
            
            # Compute statistics for generated images
            mu_fake = np.mean(features, axis=0)
            
            # Handle single image case for covariance
            if features.shape[0] == 1:
                # For single image, use identity matrix scaled by small value
                sigma_fake = np.eye(features.shape[1]) * 1e-6
            else:
                sigma_fake = np.cov(features, rowvar=False)
            
            # Compute FID score
            fid_score = self._calculate_fid(mu_real, sigma_real, mu_fake, sigma_fake)
            
            return float(fid_score)
            
        except Exception as e:
            logger.error(f"Error computing FID from images: {e}")
            return None
    
    def _calculate_fid(self, mu1, sigma1, mu2, sigma2, eps=1e-6):
        """Calculate FID score between two distributions"""
        try:
            from scipy import linalg
            
            mu1 = np.atleast_1d(mu1)
            mu2 = np.atleast_1d(mu2)
            
            sigma1 = np.atleast_2d(sigma1)
            sigma2 = np.atleast_2d(sigma2)
            
            assert mu1.shape == mu2.shape, f"Mean vectors have different lengths: {mu1.shape} vs {mu2.shape}"
            assert sigma1.shape == sigma2.shape, f"Covariance matrices have different dimensions: {sigma1.shape} vs {sigma2.shape}"
            
            diff = mu1 - mu2
            
            # Product might be almost singular
            covmean, _ = linalg.sqrtm(sigma1.dot(sigma2), disp=False)
            if not np.isfinite(covmean).all():
                msg = ('fid calculation produces singular product; '
                       'adding %s to diagonal of cov estimates') % eps
                logger.warning(msg)
                offset = np.eye(sigma1.shape[0]) * eps
                covmean = linalg.sqrtm((sigma1 + offset).dot(sigma2 + offset))
            
            # Numerical error might give slight imaginary component
            if np.iscomplexobj(covmean):
                if not np.allclose(np.diagonal(covmean).imag, 0, atol=1e-3):
                    m = np.max(np.abs(covmean.imag))
                    raise ValueError('Imaginary component {}'.format(m))
                covmean = covmean.real
            
            tr_covmean = np.trace(covmean)
            
            return (diff.dot(diff) + np.trace(sigma1) + np.trace(sigma2) - 2 * tr_covmean)
            
        except Exception as e:
            logger.error(f"Error calculating FID: {e}")
            return None
    
    def calculate_for_run(self, run_id: str) -> Optional[float]:
        """Calculate FID for a specific run (all images)"""
        if not self.fid_calculator:
            logger.error("FID calculator not available")
            return None
        
        try:
            # Get run data
            run = self.queries.db.get_run(run_id)
            if not run:
                logger.error(f"Run {run_id} not found in database")
                return None
            
            # Get ALL image paths for this run (unlike ClipScore which uses just first image)
            assets = self.queries.db.get_run_assets(run_id)
            if not assets:
                logger.error(f"No assets found for run {run_id}")
                return None
            
            # Extract image paths and verify they exist
            image_paths = []
            for asset in assets:
                full_path = asset['full_path']
                
                # Use dynamic project root discovery (same as queries.py)
                current_dir = os.path.dirname(os.path.abspath(__file__))
                dreamlayer_root = current_dir
                
                # Navigate up to find DreamLayer root (contains Dream_Layer_Resources)
                while dreamlayer_root != os.path.dirname(dreamlayer_root):  # Not at filesystem root
                    if os.path.exists(os.path.join(dreamlayer_root, 'Dream_Layer_Resources', 'output')):
                        break
                    dreamlayer_root = os.path.dirname(dreamlayer_root)
                
                possible_paths = [
                    full_path,
                    os.path.join(dreamlayer_root, full_path.lstrip('./')),
                    os.path.join(dreamlayer_root, 'Dream_Layer_Resources', 'output', os.path.basename(full_path)),
                    os.path.join(dreamlayer_root, 'dream_layer_backend', 'served_images', os.path.basename(full_path))
                ]
                
                found_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        found_path = path
                        break
                
                if found_path:
                    image_paths.append(found_path)
                else:
                    logger.warning(f"Image file not found in any location: {full_path}")
            
            if not image_paths:
                logger.error(f"No valid image files found for run {run_id}")
                return None
            
            logger.info(f"Computing FID for {len(image_paths)} images in run {run_id}")
            
            # Calculate FID
            fid_score = self._compute_fid_from_images(image_paths)
            
            if fid_score is not None:
                # Save to database
                if self.queries.save_fid_score(run_id, run['timestamp'], fid_score):
                    logger.info(f"Calculated and saved FID {fid_score:.4f} for run {run_id}")
                    return fid_score
                else:
                    logger.error(f"Failed to save FID for run {run_id}")
                    return fid_score  # Return value even if save failed
            else:
                logger.error(f"Failed to calculate FID for run {run_id}")
                return None
            
        except Exception as e:
            logger.error(f"Error calculating FID for run {run_id}: {e}")
            return None
    
    def calculate_batch(self, limit: int = 50) -> Dict[str, Any]:
        """Calculate FID for multiple runs that don't have it"""
        if not self.fid_calculator:
            logger.error("FID calculator not available")
            return {"success": 0, "failed": 0, "total": 0}
        
        # Get runs without FID
        runs_without_fid = self.queries.get_runs_without_fid_score(limit)
        
        stats = {
            "total": len(runs_without_fid),
            "success": 0,
            "failed": 0,
            "results": []
        }
        
        logger.info(f"Calculating FID for {stats['total']} runs...")
        
        for run in runs_without_fid:
            run_id = run['run_id']
            fid_score = self.calculate_for_run(run_id)
            
            if fid_score is not None:
                stats["success"] += 1
                stats["results"].append({
                    "run_id": run_id,
                    "fid_score": fid_score,
                    "prompt": run.get('prompt', '')[:50] + "..."
                })
            else:
                stats["failed"] += 1
        
        logger.info(f"Batch calculation complete: {stats['success']} success, {stats['failed']} failed")
        return stats
    
    def recalculate_all(self, force: bool = False) -> Dict[str, Any]:
        """Recalculate FID for all runs (use with caution)"""
        if not force:
            logger.warning("Use recalculate_all(force=True) to recalculate all FID scores")
            return {"error": "Force parameter required"}
        
        if not self.fid_calculator:
            logger.error("FID calculator not available")
            return {"success": 0, "failed": 0, "total": 0}
        
        # Get all runs
        all_runs = self.queries.db.get_all_runs()
        
        stats = {
            "total": len(all_runs),
            "success": 0,
            "failed": 0,
            "results": []
        }
        
        logger.info(f"Recalculating FID for {stats['total']} runs...")
        
        for run in all_runs:
            run_id = run['run_id']
            fid_score = self.calculate_for_run(run_id)
            
            if fid_score is not None:
                stats["success"] += 1
                stats["results"].append({
                    "run_id": run_id,
                    "fid_score": fid_score
                })
            else:
                stats["failed"] += 1
        
        logger.info(f"Recalculation complete: {stats['success']} success, {stats['failed']} failed")
        return stats

def calculate_missing_fid_scores(limit: int = 50) -> Dict[str, Any]:
    """Convenience function to calculate missing FID scores"""
    calculator = DatabaseFidCalculator()
    return calculator.calculate_batch(limit)

def compute_fid_score_for_run(run_id: str) -> Optional[float]:
    """Convenience function to calculate FID for a single run"""
    calculator = DatabaseFidCalculator()
    return calculator.calculate_for_run(run_id)

if __name__ == "__main__":
    # Test FID calculation
    calculator = DatabaseFidCalculator()
    
    # Calculate for runs without FID
    stats = calculator.calculate_batch(limit=10)
    print(f"Calculated FID for {stats['success']}/{stats['total']} runs")
    
    # Show results
    for result in stats['results'][:5]:
        print(f"Run {result['run_id']}: FID {result['fid_score']:.4f}")
