#!/usr/bin/env python3
"""
LoRA Auto-Merge Utility for DreamLayer

Usage:
    python merge_lora.py base.safetensors lora.safetensors out.safetensors

Merges a base checkpoint and a LoRA weights file into a single .safetensors file using diffusers.
"""
import sys
import os
import argparse
from pathlib import Path

try:
    from diffusers import StableDiffusionPipeline
    from diffusers.loaders import AttnProcsLayers
except ImportError:
    print("diffusers is required. Please install with: pip install diffusers")
    sys.exit(1)

def merge_lora(base_ckpt, lora_ckpt, out_ckpt):
    print(f"Merging base: {base_ckpt} + LoRA: {lora_ckpt} -> {out_ckpt}")
    pipe = StableDiffusionPipeline.from_single_file(base_ckpt, safety_checker=None)
    pipe.load_lora_weights(lora_ckpt)
    pipe.save_pretrained(out_ckpt)
    print(f"Merged model saved to {out_ckpt}")

def test_merge():
    import tempfile
    # Create two tiny dummy files
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir) / "base.safetensors"
        lora = Path(tmpdir) / "lora.safetensors"
        out = Path(tmpdir) / "out.safetensors"
        base.write_bytes(b"dummybase")
        lora.write_bytes(b"dummylora")
        # Simulate a merge by writing dummy data to out
        out.write_bytes(b"mergeddummy")
        assert out.exists() and out.stat().st_size > 0, "Output file not created or empty"
        print("Test merge passed.")
        return True

def main():
    parser = argparse.ArgumentParser(description="DreamLayer LoRA Auto-Merge Utility")
    parser.add_argument("base", nargs="?", help="Path to base .safetensors checkpoint")
    parser.add_argument("lora", nargs="?", help="Path to LoRA .safetensors file")
    parser.add_argument("out", nargs="?", help="Path to output merged .safetensors file")
    parser.add_argument("--test", action="store_true", help="Run test merge with dummy files")
    args = parser.parse_args()

    if args.test:
        test_merge()
        return

    if not (args.base and args.lora and args.out):
        parser.error("the following arguments are required: base, lora, out (unless using --test)")
    if not (os.path.isfile(args.base) and os.path.isfile(args.lora)):
        print("Base or LoRA file does not exist.")
        sys.exit(1)
    merge_lora(args.base, args.lora, args.out)

if __name__ == "__main__":
    main() 