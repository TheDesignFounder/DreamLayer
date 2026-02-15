"""
Video Quality Metrics (No-Reference).

Single-video evaluation metrics that don't require a reference video.
Adapted from VBench (CVPR 2024).

Metrics:
    - Temporal Flickering: frame-to-frame stability (pure math, no model)
    - Subject Consistency: DINO feature similarity across frames
    - Background Consistency: DINO feature similarity across frames
    - Motion Smoothness: optical flow smoothness (OpenCV, no model)
    - Aesthetic Quality: per-frame LAION aesthetic score (reuses existing model)
"""

import os
import logging
from typing import Dict, List, Optional, Any

import cv2
import numpy as np
import torch
import torch.nn.functional as F

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Video frame extraction
# ---------------------------------------------------------------------------

def extract_frames(video_path: str, max_frames: Optional[int] = None) -> List[np.ndarray]:
    """Extract RGB frames from a video file.

    Returns:
        List of numpy arrays in RGB format (H, W, 3), uint8
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if max_frames and len(frames) >= max_frames:
            break
    cap.release()

    if not frames:
        raise RuntimeError(f"No frames extracted from: {video_path}")

    return frames


# ---------------------------------------------------------------------------
# 1. Temporal Flickering (pure math)
# ---------------------------------------------------------------------------

def compute_temporal_flickering(video_path: str, max_frames: Optional[int] = None) -> Dict[str, Any]:
    """Compute temporal flickering score.

    Measures frame-to-frame stability using Mean Absolute Error (MAE).
    Lower MAE = less flickering = higher score.

    Returns:
        dict with temporal_flickering_score (0-1, higher is better)
        and per_frame_flicker (list of MAE values between consecutive frames)
    """
    frames = extract_frames(video_path, max_frames)

    if len(frames) < 2:
        return {"temporal_flickering_score": 1.0, "per_frame_flicker": []}

    mae_values = []
    for i in range(len(frames) - 1):
        diff = cv2.absdiff(frames[i], frames[i + 1])
        mae = float(np.mean(diff))
        mae_values.append(mae)

    mean_mae = float(np.mean(mae_values))
    # Normalize: 0 MAE = perfect (score 1.0), 255 MAE = worst (score 0.0)
    score = (255.0 - mean_mae) / 255.0

    return {
        "temporal_flickering_score": score,
        "per_frame_flicker": mae_values,
    }


# ---------------------------------------------------------------------------
# 2 & 3. Subject & Background Consistency (DINO ViT)
# ---------------------------------------------------------------------------

_dino_model = None


def _get_dino_model(device: torch.device):
    """Lazy-load DINO ViT-B/16 model."""
    global _dino_model
    if _dino_model is None:
        logger.info("Loading DINO ViT-B/16 model...")
        _dino_model = torch.hub.load('facebookresearch/dino:main', 'dino_vitb16', pretrained=True)
        _dino_model = _dino_model.to(device)
        _dino_model.eval()
        logger.info("DINO model loaded successfully")
    return _dino_model


def _dino_preprocess(frame: np.ndarray, size: int = 224) -> torch.Tensor:
    """Preprocess a frame for DINO: resize, normalize, to tensor."""
    from torchvision import transforms
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((size, size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])
    return transform(frame)


def _compute_dino_features(frames: List[np.ndarray], model, device: torch.device,
                           batch_size: int = 8) -> torch.Tensor:
    """Extract DINO features for a list of frames.

    Returns:
        Tensor of shape (N, feature_dim) with L2-normalized features
    """
    all_features = []

    for i in range(0, len(frames), batch_size):
        batch_frames = frames[i:i + batch_size]
        batch_tensors = torch.stack([_dino_preprocess(f) for f in batch_frames]).to(device)

        with torch.no_grad():
            features = model(batch_tensors)

        features = F.normalize(features, dim=-1, p=2)
        all_features.append(features.cpu())

    return torch.cat(all_features, dim=0)


def compute_subject_consistency(video_path: str, device: torch.device,
                                max_frames: Optional[int] = None) -> Dict[str, Any]:
    """Compute subject consistency using DINO features.

    Measures how consistent the main subject is across frames by computing
    cosine similarity of DINO features between consecutive frames and the first frame.

    Returns:
        dict with subject_consistency_score (0-1, higher is better)
        and per_frame_subject_sim (list)
    """
    frames = extract_frames(video_path, max_frames)

    if len(frames) < 2:
        return {"subject_consistency_score": 1.0, "per_frame_subject_sim": []}

    model = _get_dino_model(device)
    features = _compute_dino_features(frames, model, device)

    per_frame_sim = []
    for i in range(1, len(features)):
        sim_to_prev = F.cosine_similarity(features[i:i+1], features[i-1:i]).item()
        sim_to_first = F.cosine_similarity(features[i:i+1], features[0:1]).item()
        avg_sim = (sim_to_prev + sim_to_first) / 2.0
        per_frame_sim.append(avg_sim)

    score = float(np.mean(per_frame_sim))

    return {
        "subject_consistency_score": score,
        "per_frame_subject_sim": per_frame_sim,
    }


def compute_background_consistency(video_path: str, device: torch.device,
                                   max_frames: Optional[int] = None) -> Dict[str, Any]:
    """Compute background consistency using DINO features.

    Same approach as subject consistency but evaluates overall scene stability.
    Uses consecutive-frame similarity without first-frame anchoring
    to better capture background drift over time.

    Returns:
        dict with background_consistency_score (0-1, higher is better)
        and per_frame_bg_sim (list)
    """
    frames = extract_frames(video_path, max_frames)

    if len(frames) < 2:
        return {"background_consistency_score": 1.0, "per_frame_bg_sim": []}

    model = _get_dino_model(device)
    features = _compute_dino_features(frames, model, device)

    per_frame_sim = []
    for i in range(1, len(features)):
        sim = F.cosine_similarity(features[i:i+1], features[i-1:i]).item()
        per_frame_sim.append(sim)

    score = float(np.mean(per_frame_sim))

    return {
        "background_consistency_score": score,
        "per_frame_bg_sim": per_frame_sim,
    }


# ---------------------------------------------------------------------------
# 4. Motion Smoothness (OpenCV optical flow)
# ---------------------------------------------------------------------------

def compute_motion_smoothness(video_path: str,
                              max_frames: Optional[int] = None) -> Dict[str, Any]:
    """Compute motion smoothness using optical flow.

    Measures how smoothly motion changes between frames using Farneback optical flow.
    Smooth motion = small changes in flow magnitude between consecutive frame pairs.
    Jerky motion = large, abrupt changes in flow.

    Returns:
        dict with motion_smoothness_score (0-1, higher is better)
        and per_frame_motion (list of flow magnitude per frame pair)
    """
    frames = extract_frames(video_path, max_frames)

    if len(frames) < 3:
        return {"motion_smoothness_score": 1.0, "per_frame_motion": []}

    # Convert to grayscale for optical flow
    gray_frames = [cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) for f in frames]

    # Compute optical flow magnitude between consecutive frames
    flow_magnitudes = []
    for i in range(len(gray_frames) - 1):
        flow = cv2.calcOpticalFlowFarneback(
            gray_frames[i], gray_frames[i + 1],
            None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
        flow_magnitudes.append(float(np.mean(magnitude)))

    # Smoothness = how stable the flow magnitude is over time
    # Low variance in flow magnitude change = smooth motion
    if len(flow_magnitudes) < 2:
        return {"motion_smoothness_score": 1.0, "per_frame_motion": flow_magnitudes}

    flow_diffs = []
    for i in range(len(flow_magnitudes) - 1):
        diff = abs(flow_magnitudes[i + 1] - flow_magnitudes[i])
        flow_diffs.append(diff)

    mean_diff = float(np.mean(flow_diffs))
    # Normalize: typical flow diffs are 0-50 pixels; cap at 50 for scoring
    score = max(0.0, 1.0 - mean_diff / 50.0)

    return {
        "motion_smoothness_score": score,
        "per_frame_motion": flow_magnitudes,
    }


# ---------------------------------------------------------------------------
# 5. Per-Frame Aesthetic Quality (reuses existing LAION scorer)
# ---------------------------------------------------------------------------

def compute_video_aesthetic_quality(video_path: str,
                                   max_frames: Optional[int] = None) -> Dict[str, Any]:
    """Compute per-frame aesthetic quality using the existing LAION aesthetic predictor.

    Returns:
        dict with video_aesthetic_mean, video_aesthetic_min, video_aesthetic_std (1-10 scale)
        and per_frame_aesthetic (list)
    """
    import tempfile
    from PIL import Image

    frames = extract_frames(video_path, max_frames)

    try:
        from dream_layer_backend_utils.aesthetic_metrics import get_aesthetic_calculator
        calculator = get_aesthetic_calculator()
    except Exception as e:
        logger.error(f"Failed to load aesthetic calculator: {e}")
        return {
            "video_aesthetic_mean": None,
            "video_aesthetic_min": None,
            "video_aesthetic_std": None,
            "per_frame_aesthetic": [],
        }

    per_frame_scores = []
    # Sample frames to avoid excessive computation (every Nth frame)
    sample_step = max(1, len(frames) // 16)  # Cap at ~16 frames
    sampled_frames = frames[::sample_step]

    for frame in sampled_frames:
        try:
            # Save frame to temp file for the aesthetic calculator
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                Image.fromarray(frame).save(tmp.name)
                score = calculator.calculate_aesthetic_score(tmp.name)
                if score is not None:
                    per_frame_scores.append(score)
                os.unlink(tmp.name)
        except Exception as e:
            logger.warning(f"Aesthetic score failed for frame: {e}")
            continue

    if not per_frame_scores:
        return {
            "video_aesthetic_mean": None,
            "video_aesthetic_min": None,
            "video_aesthetic_std": None,
            "per_frame_aesthetic": [],
        }

    return {
        "video_aesthetic_mean": float(np.mean(per_frame_scores)),
        "video_aesthetic_min": float(np.min(per_frame_scores)),
        "video_aesthetic_std": float(np.std(per_frame_scores)),
        "per_frame_aesthetic": per_frame_scores,
    }


# ---------------------------------------------------------------------------
# Combined computation
# ---------------------------------------------------------------------------

def compute_all_quality_metrics(video_path: str, device: torch.device,
                                max_frames: Optional[int] = None) -> Dict[str, Any]:
    """Compute all no-reference video quality metrics.

    Returns a combined dict with all metrics and an _errors list.
    """
    metrics = {}
    errors = []

    # Extract video FPS
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        if fps and fps > 0:
            metrics["video_fps"] = float(fps)
    except Exception:
        pass

    # 1. Temporal Flickering (fast, no model)
    try:
        flickering = compute_temporal_flickering(video_path, max_frames)
        metrics.update(flickering)
    except Exception as e:
        logger.error(f"Temporal flickering failed: {e}")
        errors.append(f"Temporal Flickering: {str(e)}")

    # 2. Subject Consistency (DINO)
    try:
        subject = compute_subject_consistency(video_path, device, max_frames)
        metrics.update(subject)
    except Exception as e:
        logger.error(f"Subject consistency failed: {e}")
        errors.append(f"Subject Consistency: {str(e)}")

    # 3. Background Consistency (DINO, reuses loaded model)
    try:
        background = compute_background_consistency(video_path, device, max_frames)
        metrics.update(background)
    except Exception as e:
        logger.error(f"Background consistency failed: {e}")
        errors.append(f"Background Consistency: {str(e)}")

    # 4. Motion Smoothness (OpenCV, no model)
    try:
        smoothness = compute_motion_smoothness(video_path, max_frames)
        metrics.update(smoothness)
    except Exception as e:
        logger.error(f"Motion smoothness failed: {e}")
        errors.append(f"Motion Smoothness: {str(e)}")

    # 5. Aesthetic Quality (reuses existing LAION model)
    try:
        aesthetic = compute_video_aesthetic_quality(video_path, max_frames)
        metrics.update(aesthetic)
    except Exception as e:
        logger.error(f"Aesthetic quality failed: {e}")
        errors.append(f"Aesthetic Quality: {str(e)}")

    metrics["_quality_errors"] = errors
    return metrics
