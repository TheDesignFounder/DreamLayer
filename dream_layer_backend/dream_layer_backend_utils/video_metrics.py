"""
Video Evaluation Metrics Calculator.

Provides FVD, Video SSIM, Video PSNR, and Video LPIPS metrics
for evaluating generated videos. Adapted from common_metrics_on_video_quality.

Input videos are loaded as tensors in [B, T, C, H, W] format with pixel values in [0, 1].
"""

import os
import math
import logging
from typing import Dict, List, Optional, Any

import cv2
import numpy as np
import torch

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Video loading
# ---------------------------------------------------------------------------

def load_video_as_tensor(video_path: str, max_frames: Optional[int] = None) -> torch.Tensor:
    """Load an mp4 video file as a tensor.

    Args:
        video_path: path to .mp4 file
        max_frames: optional cap on number of frames to load

    Returns:
        Tensor of shape [1, T, 3, H, W] in [0, 1] float32
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # BGR -> RGB, HWC -> CHW, uint8 -> float32 [0,1]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = torch.from_numpy(frame).permute(2, 0, 1).float() / 255.0
        frames.append(frame)
        if max_frames and len(frames) >= max_frames:
            break
    cap.release()

    if not frames:
        raise RuntimeError(f"No frames extracted from video: {video_path}")

    # [T, C, H, W] -> [1, T, C, H, W]
    video_tensor = torch.stack(frames).unsqueeze(0)
    return video_tensor


# ---------------------------------------------------------------------------
# SSIM (per-frame, no ML model needed)
# ---------------------------------------------------------------------------

def _ssim_single(img1: np.ndarray, img2: np.ndarray) -> float:
    """Compute SSIM between two single-channel images (numpy, float64, [0,1])."""
    C1 = 0.01 ** 2
    C2 = 0.03 ** 2
    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)
    kernel = cv2.getGaussianKernel(11, 1.5)
    window = np.outer(kernel, kernel.transpose())
    mu1 = cv2.filter2D(img1, -1, window)[5:-5, 5:-5]
    mu2 = cv2.filter2D(img2, -1, window)[5:-5, 5:-5]
    mu1_sq = mu1 ** 2
    mu2_sq = mu2 ** 2
    mu1_mu2 = mu1 * mu2
    sigma1_sq = cv2.filter2D(img1 ** 2, -1, window)[5:-5, 5:-5] - mu1_sq
    sigma2_sq = cv2.filter2D(img2 ** 2, -1, window)[5:-5, 5:-5] - mu2_sq
    sigma12 = cv2.filter2D(img1 * img2, -1, window)[5:-5, 5:-5] - mu1_mu2
    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
    return float(ssim_map.mean())


def _ssim_frame(img1: np.ndarray, img2: np.ndarray) -> float:
    """Compute SSIM for a frame pair. Input shape: (C, H, W), values in [0, 1]."""
    if img1.ndim == 2:
        return _ssim_single(img1, img2)
    elif img1.ndim == 3:
        if img1.shape[0] == 3:
            return float(np.mean([_ssim_single(img1[i], img2[i]) for i in range(3)]))
        elif img1.shape[0] == 1:
            return _ssim_single(np.squeeze(img1), np.squeeze(img2))
    raise ValueError(f"Unexpected image dimensions: {img1.shape}")


def compute_video_ssim(videos1: torch.Tensor, videos2: torch.Tensor,
                       per_frame: bool = False) -> Dict[str, Any]:
    """Compute SSIM between two video tensors.

    Args:
        videos1, videos2: tensors of shape [B, T, C, H, W] in [0, 1]
        per_frame: if True, return per-frame scores

    Returns:
        dict with video_ssim_mean, video_ssim_std, and optionally video_ssim_per_frame
    """
    assert videos1.shape == videos2.shape, "Video shapes must match"

    all_frame_scores = []
    for b in range(videos1.shape[0]):
        for t in range(videos1.shape[1]):
            img1 = videos1[b, t].numpy()
            img2 = videos2[b, t].numpy()
            all_frame_scores.append(_ssim_frame(img1, img2))

    num_frames = videos1.shape[1]
    per_frame_means = []
    if per_frame:
        for t in range(num_frames):
            frame_scores = [all_frame_scores[b * num_frames + t]
                            for b in range(videos1.shape[0])]
            per_frame_means.append(float(np.mean(frame_scores)))

    result = {
        "video_ssim_mean": float(np.mean(all_frame_scores)),
        "video_ssim_std": float(np.std(all_frame_scores)),
    }
    if per_frame:
        result["video_ssim_per_frame"] = per_frame_means
    return result


# ---------------------------------------------------------------------------
# PSNR (per-frame, no ML model needed)
# ---------------------------------------------------------------------------

def _psnr_frame(img1: np.ndarray, img2: np.ndarray) -> float:
    """Compute PSNR for a frame pair. Input: (C, H, W), values in [0, 1]."""
    mse = np.mean((img1.astype(np.float64) - img2.astype(np.float64)) ** 2)
    if mse < 1e-10:
        return 100.0
    return float(20 * math.log10(1.0 / math.sqrt(mse)))


def compute_video_psnr(videos1: torch.Tensor, videos2: torch.Tensor,
                       per_frame: bool = False) -> Dict[str, Any]:
    """Compute PSNR between two video tensors.

    Args:
        videos1, videos2: tensors of shape [B, T, C, H, W] in [0, 1]
        per_frame: if True, return per-frame scores

    Returns:
        dict with video_psnr_mean, video_psnr_std, and optionally video_psnr_per_frame
    """
    assert videos1.shape == videos2.shape, "Video shapes must match"

    all_frame_scores = []
    for b in range(videos1.shape[0]):
        for t in range(videos1.shape[1]):
            img1 = videos1[b, t].numpy()
            img2 = videos2[b, t].numpy()
            all_frame_scores.append(_psnr_frame(img1, img2))

    num_frames = videos1.shape[1]
    per_frame_means = []
    if per_frame:
        for t in range(num_frames):
            frame_scores = [all_frame_scores[b * num_frames + t]
                            for b in range(videos1.shape[0])]
            per_frame_means.append(float(np.mean(frame_scores)))

    result = {
        "video_psnr_mean": float(np.mean(all_frame_scores)),
        "video_psnr_std": float(np.std(all_frame_scores)),
    }
    if per_frame:
        result["video_psnr_per_frame"] = per_frame_means
    return result


# ---------------------------------------------------------------------------
# LPIPS (per-frame, requires pretrained network)
# ---------------------------------------------------------------------------

def compute_video_lpips(videos1: torch.Tensor, videos2: torch.Tensor,
                        device: torch.device, per_frame: bool = False) -> Dict[str, Any]:
    """Compute LPIPS between two video tensors.

    Args:
        videos1, videos2: tensors of shape [B, T, C, H, W] in [0, 1]
        device: torch device
        per_frame: if True, return per-frame scores

    Returns:
        dict with video_lpips_mean, video_lpips_std, and optionally video_lpips_per_frame
    """
    import lpips as lpips_lib
    import warnings
    warnings.filterwarnings("ignore")

    assert videos1.shape == videos2.shape, "Video shapes must match"

    loss_fn = lpips_lib.LPIPS(net='alex', spatial=True).to(device)

    # Handle grayscale
    if videos1.shape[2] == 1:
        videos1 = videos1.repeat(1, 1, 3, 1, 1)
        videos2 = videos2.repeat(1, 1, 3, 1, 1)

    # [0, 1] -> [-1, 1] for LPIPS
    videos1 = videos1 * 2 - 1
    videos2 = videos2 * 2 - 1

    all_frame_scores = []
    with torch.no_grad():
        for b in range(videos1.shape[0]):
            for t in range(videos1.shape[1]):
                img1 = videos1[b, t].unsqueeze(0).to(device)
                img2 = videos2[b, t].unsqueeze(0).to(device)
                score = loss_fn.forward(img1, img2).mean().detach().cpu().item()
                all_frame_scores.append(score)

    num_frames = videos1.shape[1]
    per_frame_means = []
    if per_frame:
        for t in range(num_frames):
            frame_scores = [all_frame_scores[b * num_frames + t]
                            for b in range(videos1.shape[0])]
            per_frame_means.append(float(np.mean(frame_scores)))

    result = {
        "video_lpips_mean": float(np.mean(all_frame_scores)),
        "video_lpips_std": float(np.std(all_frame_scores)),
    }
    if per_frame:
        result["video_lpips_per_frame"] = per_frame_means
    return result


# ---------------------------------------------------------------------------
# FVD (distribution metric, requires I3D model)
# ---------------------------------------------------------------------------

def compute_fvd(videos1: torch.Tensor, videos2: torch.Tensor,
                device: torch.device) -> Dict[str, float]:
    """Compute Frechet Video Distance between two sets of videos.

    Args:
        videos1, videos2: tensors of shape [B, T, C, H, W] in [0, 1]
                         B >= 2 for meaningful covariance, T >= 10 for I3D
        device: torch device

    Returns:
        dict with fvd_score
    """
    from .fvd.fvd import load_i3d_pretrained, get_fvd_feats, frechet_distance

    assert videos1.shape == videos2.shape, "Video shapes must match"
    assert videos1.shape[1] >= 10, "FVD requires at least 10 frames per video"

    # Handle grayscale
    if videos1.shape[2] == 1:
        videos1 = videos1.repeat(1, 1, 3, 1, 1)
        videos2 = videos2.repeat(1, 1, 3, 1, 1)

    # BTCHW -> BCTHW for I3D
    v1 = videos1.permute(0, 2, 1, 3, 4)
    v2 = videos2.permute(0, 2, 1, 3, 4)

    i3d = load_i3d_pretrained(device=device)
    feats1 = get_fvd_feats(v1, i3d=i3d, device=device)
    feats2 = get_fvd_feats(v2, i3d=i3d, device=device)
    fvd_score = frechet_distance(feats1, feats2)

    return {"fvd_score": fvd_score}


# ---------------------------------------------------------------------------
# VideoMetricsCalculator (singleton pattern)
# ---------------------------------------------------------------------------

class VideoMetricsCalculator:
    """Calculator for video evaluation metrics."""

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else
                                   'mps' if torch.backends.mps.is_available() else 'cpu')
        logger.info(f"VideoMetricsCalculator initialized on device: {self.device}")

    def compute_all(self, video_path: str, reference_path: Optional[str] = None,
                    per_frame: bool = True) -> Dict[str, Any]:
        """Compute all applicable video metrics.

        Args:
            video_path: path to the generated video
            reference_path: optional path to a reference video (for SSIM/PSNR/LPIPS)
            per_frame: whether to include per-frame breakdowns

        Returns:
            dict with all computed metrics and _errors list
        """
        metrics = {}
        errors = []

        video_tensor = load_video_as_tensor(video_path)
        logger.info(f"Loaded video: {video_path}, shape: {video_tensor.shape}")

        # Reference-based metrics (SSIM, PSNR, LPIPS)
        if reference_path:
            ref_tensor = load_video_as_tensor(reference_path)

            # Match frame counts by truncating to shorter
            min_frames = min(video_tensor.shape[1], ref_tensor.shape[1])
            v1 = video_tensor[:, :min_frames]
            v2 = ref_tensor[:, :min_frames]

            # Match spatial dimensions by resizing reference to match generated
            if v1.shape[3:] != v2.shape[3:]:
                h, w = v1.shape[3], v1.shape[4]
                v2_resized = []
                for t in range(v2.shape[1]):
                    frame = torch.nn.functional.interpolate(
                        v2[:, t], size=(h, w), mode='bilinear', align_corners=False
                    )
                    v2_resized.append(frame)
                v2 = torch.stack(v2_resized, dim=1)

            try:
                ssim_result = compute_video_ssim(v1, v2, per_frame=per_frame)
                metrics.update(ssim_result)
            except Exception as e:
                logger.error(f"SSIM computation failed: {e}")
                errors.append(f"SSIM: {str(e)}")

            try:
                psnr_result = compute_video_psnr(v1, v2, per_frame=per_frame)
                metrics.update(psnr_result)
            except Exception as e:
                logger.error(f"PSNR computation failed: {e}")
                errors.append(f"PSNR: {str(e)}")

            try:
                lpips_result = compute_video_lpips(v1, v2, self.device, per_frame=per_frame)
                metrics.update(lpips_result)
            except Exception as e:
                logger.error(f"LPIPS computation failed: {e}")
                errors.append(f"LPIPS: {str(e)}")

        # FVD requires two *sets* of videos (distribution metric)
        # For single video comparison, FVD is not applicable
        metrics["fvd_score"] = None

        # No-reference quality metrics (always computed)
        try:
            from .video_quality_metrics import compute_all_quality_metrics
            quality_metrics = compute_all_quality_metrics(video_path, self.device)
            quality_errors = quality_metrics.pop("_quality_errors", [])
            metrics.update(quality_metrics)
            errors.extend(quality_errors)
        except Exception as e:
            logger.error(f"Quality metrics computation failed: {e}")
            errors.append(f"Quality Metrics: {str(e)}")

        metrics["_errors"] = errors
        return metrics


# Singleton
_calculator = None


def get_video_calculator() -> VideoMetricsCalculator:
    """Get or create the singleton VideoMetricsCalculator."""
    global _calculator
    if _calculator is None:
        _calculator = VideoMetricsCalculator()
    return _calculator
