"""
FVD (Frechet Video Distance) computation using I3D features.
Adapted from https://github.com/universome/fvd-comparison
and common_metrics_on_video_quality.
"""

import os
import math
from typing import Tuple

import numpy as np
import torch
import torch.nn.functional as F
from scipy.linalg import sqrtm


def load_i3d_pretrained(device=torch.device('cpu')):
    """Load pretrained I3D model (TorchScript). Downloads on first use (~500MB)."""
    i3d_weights_url = "https://www.dropbox.com/s/ge9e5ujwgetktms/i3d_torchscript.pt?dl=1"
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'i3d_torchscript.pt')

    if not os.path.exists(filepath):
        print(f"Downloading I3D model to {filepath}...")
        import requests
        response = requests.get(i3d_weights_url, stream=True)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("I3D model downloaded successfully.")

    i3d = torch.jit.load(filepath).eval().to(device)
    return i3d


def preprocess_single(video, resolution=224):
    """Preprocess a single video for I3D input.

    Args:
        video: tensor of shape (C, T, H, W) in [0, 1]
        resolution: target spatial resolution

    Returns:
        Preprocessed video tensor (C, T, resolution, resolution) in [-1, 1]
    """
    c, t, h, w = video.shape

    # Scale shorter side to resolution
    scale = resolution / min(h, w)
    if h < w:
        target_size = (resolution, math.ceil(w * scale))
    else:
        target_size = (math.ceil(h * scale), resolution)
    video = F.interpolate(video, size=target_size, mode='bilinear', align_corners=False)

    # Center crop
    c, t, h, w = video.shape
    w_start = (w - resolution) // 2
    h_start = (h - resolution) // 2
    video = video[:, :, h_start:h_start + resolution, w_start:w_start + resolution]

    # [0, 1] -> [-1, 1]
    video = (video - 0.5) * 2

    return video.contiguous()


def get_fvd_feats(videos, i3d, device, bs=10):
    """Extract I3D features from videos.

    Args:
        videos: tensor of shape (B, C, T, H, W) in [0, 1]
        i3d: pretrained I3D model
        device: torch device
        bs: batch size for feature extraction

    Returns:
        numpy array of shape (B, 400) with I3D features
    """
    detector_kwargs = dict(rescale=False, resize=False, return_features=True)
    feats = np.empty((0, 400))

    with torch.no_grad():
        for i in range((len(videos) - 1) // bs + 1):
            batch = torch.stack([
                preprocess_single(video)
                for video in videos[i * bs:(i + 1) * bs]
            ]).to(device)
            batch_feats = i3d(batch, **detector_kwargs).detach().cpu().numpy()
            feats = np.vstack([feats, batch_feats])

    return feats


def compute_stats(feats: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute mean and covariance of features."""
    mu = feats.mean(axis=0)
    sigma = np.cov(feats, rowvar=False)
    return mu, sigma


def frechet_distance(feats_fake: np.ndarray, feats_real: np.ndarray) -> float:
    """Compute Frechet distance between two sets of features."""
    mu_gen, sigma_gen = compute_stats(feats_fake)
    mu_real, sigma_real = compute_stats(feats_real)
    m = np.square(mu_gen - mu_real).sum()
    if feats_fake.shape[0] > 1:
        s, _ = sqrtm(np.dot(sigma_gen, sigma_real), disp=False)
        fid = np.real(m + np.trace(sigma_gen + sigma_real - s * 2))
    else:
        fid = np.real(m)
    return float(fid)
