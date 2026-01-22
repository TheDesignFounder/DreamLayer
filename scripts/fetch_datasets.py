#!/usr/bin/env python3
"""
Dataset Fetcher for DreamLayer

Downloads required datasets for FID evaluation metrics.
Run this after cloning the repository if you need FID scoring.

Usage:
    python scripts/fetch_datasets.py
"""

import os
import sys
import tarfile
import hashlib
from pathlib import Path
from urllib.request import urlretrieve
from urllib.error import URLError

# Dataset configuration
DATASETS_DIR = Path(__file__).resolve().parents[1] / "dream_layer_backend" / "datasets"

CIFAR10_URL = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
CIFAR10_MD5 = "c58f30108f718f92721af3b95e74349a"
CIFAR10_EXTRACT_DIR = "cifar-10-batches-py"


def md5_checksum(filepath: Path) -> str:
    """Calculate MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def download_with_progress(url: str, dest: Path, description: str = "Downloading"):
    """Download a file with progress indication."""
    print(f"{description}: {url}")
    print(f"  -> {dest}")

    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 // total_size)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            sys.stdout.write(f"\r  Progress: {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
            sys.stdout.flush()

    try:
        urlretrieve(url, dest, progress_hook)
        print()  # newline after progress
        return True
    except URLError as e:
        print(f"\n  Error downloading: {e}")
        return False


def fetch_cifar10():
    """Download and extract CIFAR-10 dataset."""
    print("\n" + "=" * 60)
    print("CIFAR-10 Dataset")
    print("=" * 60)

    extract_path = DATASETS_DIR / CIFAR10_EXTRACT_DIR

    # Check if already exists
    if extract_path.exists() and (extract_path / "data_batch_1").exists():
        print(f"CIFAR-10 already exists at: {extract_path}")
        print("  Skipping download.")
        return True

    # Create datasets directory
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    # Download
    tar_path = DATASETS_DIR / "cifar-10-python.tar.gz"
    if not tar_path.exists():
        if not download_with_progress(CIFAR10_URL, tar_path, "Downloading CIFAR-10"):
            return False

        # Verify checksum
        print("  Verifying checksum...")
        actual_md5 = md5_checksum(tar_path)
        if actual_md5 != CIFAR10_MD5:
            print(f"  ERROR: Checksum mismatch!")
            print(f"    Expected: {CIFAR10_MD5}")
            print(f"    Got: {actual_md5}")
            tar_path.unlink()
            return False
        print("  Checksum OK")

    # Extract
    print("  Extracting...")
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=DATASETS_DIR)
        print(f"  Extracted to: {extract_path}")

        # Clean up tar file
        tar_path.unlink()
        print("  Cleaned up archive")
        return True
    except Exception as e:
        print(f"  Error extracting: {e}")
        return False


def check_inception_stats():
    """Check if CIFAR-10 inception stats exist and provide instructions."""
    print("\n" + "=" * 60)
    print("CIFAR-10 Inception Statistics")
    print("=" * 60)

    stats_file = DATASETS_DIR / "cifar10_inception_stats.npz"

    if stats_file.exists():
        size_mb = stats_file.stat().st_size / (1024 * 1024)
        print(f"Stats file exists: {stats_file}")
        print(f"  Size: {size_mb:.1f} MB")
        return True
    else:
        print(f"Stats file NOT found: {stats_file}")
        print("\nThe inception statistics file will be generated automatically")
        print("when you first run FID evaluation. This may take a few minutes.")
        print("\nAlternatively, you can pre-generate it by running:")
        print("  python dream_layer_backend/datasets/dataset_utils.py")
        return False


def main():
    print("=" * 60)
    print("DreamLayer Dataset Fetcher")
    print("=" * 60)
    print(f"\nDatasets directory: {DATASETS_DIR}")

    success = True

    # Fetch CIFAR-10
    if not fetch_cifar10():
        success = False

    # Check inception stats
    check_inception_stats()

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    if success:
        print("All required datasets are ready!")
        print("\nYou can now use FID evaluation metrics in DreamLayer.")
    else:
        print("Some datasets failed to download.")
        print("Please check your internet connection and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
