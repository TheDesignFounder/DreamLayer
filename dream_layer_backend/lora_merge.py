#!/usr/bin/env python3
"""
DreamLayer LoRA Auto-Merge Utility

This module provides functionality to merge LoRA adapters with base Stable Diffusion models
using the diffusers library. It supports both CLI usage and programmatic usage.

Usage:
    python lora_merge.py merge-lora base.safetensors lora.safetensors out.safetensors
    
Or programmatically:
    from lora_merge import merge_lora_with_base
    merge_lora_with_base("base.safetensors", "lora.safetensors", "out.safetensors")
"""

import os
import sys
import argparse
import logging
from typing import Dict
from pathlib import Path

try:
    import torch
    from diffusers import StableDiffusionPipeline, DiffusionPipeline
    from safetensors import safe_open
    from safetensors.torch import save_file
except ImportError as e:
    print(f"Error: Required dependencies not installed. Please install: {e}")
    print("Run: pip install diffusers torch safetensors transformers")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LoRAMerger:
    """Handles LoRA merging operations with Stable Diffusion models."""
    
    def __init__(self, device: str = "auto"):
        """Initialize the LoRA merger.
        
        Args:
            device: Device to use for computations ('auto', 'cpu', 'cuda')
        """
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"Using device: {self.device}")
    
    def load_base_model(self, base_path: str) -> DiffusionPipeline:
        """Load the base Stable Diffusion model.
        
        Args:
            base_path: Path to the base model checkpoint
            
        Returns:
            Loaded diffusion pipeline
        """
        if not os.path.exists(base_path):
            raise FileNotFoundError(f"Base model not found: {base_path}")
        
        logger.info(f"Loading base model from: {base_path}")
        
        try:
            # Try to load as StableDiffusionPipeline first
            pipeline = StableDiffusionPipeline.from_single_file(
                base_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                use_safetensors=True,
                device_map="auto" if self.device == "cuda" else None
            )
            
            if self.device == "cpu":
                pipeline = pipeline.to(self.device)
            
            logger.info("Successfully loaded base model")
            return pipeline
            
        except Exception as e:
            logger.error(f"Failed to load base model: {e}")
            raise
    
    def load_lora_weights(self, lora_path: str) -> Dict[str, torch.Tensor]:
        """Load LoRA weights from safetensors file.
        
        Args:
            lora_path: Path to the LoRA weights file
            
        Returns:
            Dictionary of LoRA weights
        """
        if not os.path.exists(lora_path):
            raise FileNotFoundError(f"LoRA file not found: {lora_path}")
        
        logger.info(f"Loading LoRA weights from: {lora_path}")
        
        try:
            lora_weights = {}
            with safe_open(lora_path, framework="pt", device=self.device) as f:
                for key in f.keys():
                    lora_weights[key] = f.get_tensor(key)
            
            logger.info(f"Loaded {len(lora_weights)} LoRA weight tensors")
            return lora_weights
            
        except Exception as e:
            logger.error(f"Failed to load LoRA weights: {e}")
            raise
    
    def _group_lora_weights_by_layer(self, lora_weights: Dict[str, torch.Tensor]) -> Dict[str, Dict[str, torch.Tensor]]:
        """Group LoRA weights by layer name."""
        lora_pairs = {}
        for key, weight in lora_weights.items():
            if '.lora_down.' in key:
                base_key = key.replace('.lora_down.', '.')
                layer_name = base_key.split('.weight')[0]
                if layer_name not in lora_pairs:
                    lora_pairs[layer_name] = {}
                lora_pairs[layer_name]['down'] = weight
            elif '.lora_up.' in key:
                base_key = key.replace('.lora_up.', '.')
                layer_name = base_key.split('.weight')[0]
                if layer_name not in lora_pairs:
                    lora_pairs[layer_name] = {}
                lora_pairs[layer_name]['up'] = weight
        return lora_pairs
    
    def _apply_lora_to_layer(self, unet_state_dict: Dict[str, torch.Tensor], layer_name: str, 
                            lora_pair: Dict[str, torch.Tensor], alpha: float) -> bool:
        """Apply LoRA adaptation to a specific layer."""
        # Find corresponding weight in UNet using next() instead of for-loop
        unet_key = next((key for key in unet_state_dict.keys() 
                        if layer_name in key and 'weight' in key), None)
        
        if not unet_key or unet_key not in unet_state_dict:
            return False
            
        # Calculate LoRA delta: up @ down
        down_weight = lora_pair['down']
        up_weight = lora_pair['up']
        
        # Compute the low-rank adaptation
        if len(down_weight.shape) == 4:  # Conv2d
            down_weight = down_weight.squeeze()
        if len(up_weight.shape) == 4:  # Conv2d
            up_weight = up_weight.squeeze()
        
        # Compute delta
        delta = alpha * torch.mm(up_weight, down_weight)
        
        # Reshape if needed
        original_shape = unet_state_dict[unet_key].shape
        if len(original_shape) == 4 and len(delta.shape) == 2:
            delta = delta.unsqueeze(-1).unsqueeze(-1)
        elif len(original_shape) != len(delta.shape):
            delta = delta.view(original_shape)
        
        # Apply the adaptation
        unet_state_dict[unet_key] = unet_state_dict[unet_key] + delta.to(unet_state_dict[unet_key].device)
        return True

    def merge_lora_with_pipeline(self, pipeline: DiffusionPipeline, lora_weights: Dict[str, torch.Tensor], 
                                alpha: float = 1.0) -> DiffusionPipeline:
        """Merge LoRA weights with the pipeline.
        
        Args:
            pipeline: Base diffusion pipeline
            lora_weights: LoRA weights dictionary
            alpha: LoRA strength/alpha parameter
            
        Returns:
            Pipeline with merged LoRA weights
        """
        logger.info(f"Merging LoRA weights with alpha={alpha}")
        
        try:
            # Apply LoRA weights to UNet
            unet_state_dict = pipeline.unet.state_dict()
            
            # Group LoRA weights by layer
            lora_pairs = self._group_lora_weights_by_layer(lora_weights)
            
            # Apply LoRA adaptations
            modifications = 0
            for layer_name, lora_pair in lora_pairs.items():
                if 'down' in lora_pair and 'up' in lora_pair:
                    if self._apply_lora_to_layer(unet_state_dict, layer_name, lora_pair, alpha):
                        modifications += 1
            
            # Load the modified state dict
            pipeline.unet.load_state_dict(unet_state_dict)
            
            logger.info(f"Successfully merged LoRA weights ({modifications} layers modified)")
            return pipeline
            
        except Exception as e:
            logger.error(f"Failed to merge LoRA weights: {e}")
            raise
    
    def save_merged_model(self, pipeline: DiffusionPipeline, output_path: str):
        """Save the merged model to disk.
        
        Args:
            pipeline: Pipeline with merged weights
            output_path: Path to save the merged model
        """
        logger.info(f"Saving merged model to: {output_path}")
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save as safetensors
            pipeline.save_pretrained(
                output_path.replace('.safetensors', ''),
                safe_serialization=True
            )
            
            # If user wants a single file, try to save as single file
            if output_path.endswith('.safetensors'):
                try:
                    # Extract just the UNet weights and save as single file
                    unet_state_dict = pipeline.unet.state_dict()
                    save_file(unet_state_dict, output_path)
                    logger.info(f"Saved merged UNet weights to: {output_path}")
                except Exception as e:
                    logger.warning(f"Could not save as single file, saved as directory instead: {e}")
            
            logger.info("Successfully saved merged model")
            
        except Exception as e:
            logger.error(f"Failed to save merged model: {e}")
            raise

def merge_lora_with_base(base_path: str, lora_path: str, output_path: str, 
                        alpha: float = 1.0, device: str = "auto") -> bool:
    """Main function to merge LoRA with base model.
    
    Args:
        base_path: Path to base model checkpoint
        lora_path: Path to LoRA weights file
        output_path: Path to save merged model
        alpha: LoRA strength parameter
        device: Device to use for computations
        
    Returns:
        True if successful, False otherwise
    """
    try:
        merger = LoRAMerger(device=device)
        
        # Try to load as full pipeline first, fall back to simple weight merge
        try:
            # Load base model
            pipeline = merger.load_base_model(base_path)
            
            # Load LoRA weights
            lora_weights = merger.load_lora_weights(lora_path)
            
            # Merge LoRA with pipeline
            merged_pipeline = merger.merge_lora_with_pipeline(pipeline, lora_weights, alpha)
            
            # Save merged model
            merger.save_merged_model(merged_pipeline, output_path)
            
        except Exception as pipeline_error:
            logger.warning(f"Pipeline approach failed: {pipeline_error}")
            logger.info("Falling back to simple weight merge...")
            
            # Simple weight merge approach for testing
            return merge_lora_weights_simple(base_path, lora_path, output_path, alpha, device)
        
        return True
        
    except Exception as e:
        logger.error(f"LoRA merge failed: {e}")
        return False

def merge_lora_weights_simple(base_path: str, lora_path: str, output_path: str, 
                             alpha: float = 1.0, device: str = "auto") -> bool:
    """Simple LoRA weight merge without full pipeline loading.
    
    This is a fallback method that works with basic weight tensors.
    """
    try:
        logger.info("Using simple weight merge approach")
        
        # Handle device selection
        actual_device = "cuda" if torch.cuda.is_available() else "cpu" if device == "auto" else device
        
        logger.info(f"Using device: {actual_device}")
        
        # Load base weights
        base_weights = {}
        with safe_open(base_path, framework="pt", device=actual_device) as f:
            for key in f.keys():
                base_weights[key] = f.get_tensor(key)
        
        # Load LoRA weights
        lora_weights = {}
        with safe_open(lora_path, framework="pt", device=actual_device) as f:
            for key in f.keys():
                lora_weights[key] = f.get_tensor(key)
        
        # Group LoRA weights by layer
        lora_pairs = {}
        for key, weight in lora_weights.items():
            if '.lora_down.' in key:
                base_key = key.replace('.lora_down.', '.')
                layer_name = base_key.split('.weight')[0]
                if layer_name not in lora_pairs:
                    lora_pairs[layer_name] = {}
                lora_pairs[layer_name]['down'] = weight
            elif '.lora_up.' in key:
                base_key = key.replace('.lora_up.', '.')
                layer_name = base_key.split('.weight')[0]
                if layer_name not in lora_pairs:
                    lora_pairs[layer_name] = {}
                lora_pairs[layer_name]['up'] = weight
        
        # Apply LoRA adaptations to base weights
        merged_weights = base_weights.copy()
        modifications = 0
        
        for layer_name, lora_pair in lora_pairs.items():
            if 'down' in lora_pair and 'up' in lora_pair:
                # Find corresponding weight in base model
                base_key = next((key for key in base_weights.keys() 
                               if layer_name in key and 'weight' in key), None)
                
                if base_key and base_key in base_weights:
                    try:
                        # Calculate LoRA delta
                        down_weight = lora_pair['down']
                        up_weight = lora_pair['up']
                        original_weight = base_weights[base_key]
                        
                        # Compute the low-rank adaptation: delta = up @ down
                        # For Conv2d layers, we need to handle the reshaping properly
                        if len(original_weight.shape) == 4:  # Conv2d weight: (out_ch, in_ch, kh, kw)
                            # Flatten spatial dimensions for computation
                            out_ch, in_ch, kh, kw = original_weight.shape
                            
                            # LoRA down should be (rank, in_ch * kh * kw)
                            # LoRA up should be (out_ch, rank)
                            if down_weight.shape[1] == in_ch * kh * kw and up_weight.shape[0] == out_ch:
                                # Compute delta in flattened space
                                delta_flat = torch.mm(up_weight, down_weight)  # (out_ch, in_ch * kh * kw)
                                # Reshape back to conv weight shape
                                delta = delta_flat.view(out_ch, in_ch, kh, kw)
                            else:
                                logger.warning(f"Shape mismatch for conv layer {base_key}, skipping")
                                continue
                                
                        elif len(original_weight.shape) == 2:  # Linear weight: (out_features, in_features)
                            # For linear layers, direct matrix multiplication
                            out_features, in_features = original_weight.shape
                            
                            # LoRA down should be (rank, in_features)
                            # LoRA up should be (out_features, rank)
                            if down_weight.shape[1] == in_features and up_weight.shape[0] == out_features:
                                delta = torch.mm(up_weight, down_weight)  # (out_features, in_features)
                            else:
                                logger.warning(f"Shape mismatch for linear layer {base_key}, skipping")
                                continue
                        else:
                            logger.warning(f"Unsupported weight shape for {base_key}: {original_weight.shape}")
                            continue
                        
                        # Apply the adaptation with alpha scaling
                        merged_weights[base_key] = original_weight + alpha * delta.to(original_weight.device)
                        modifications += 1
                        logger.debug(f"Applied LoRA to {base_key}: {original_weight.shape}")
                        
                    except Exception as layer_error:
                        logger.warning(f"Failed to apply LoRA to {base_key}: {layer_error}")
                        continue
        
        # Save merged weights
        if output_dir := os.path.dirname(output_path):  # Only create directory if output_path has a directory component
            os.makedirs(output_dir, exist_ok=True)
        save_file(merged_weights, output_path)
        
        logger.info(f"Successfully merged LoRA weights ({modifications} layers modified)")
        logger.info(f"Saved merged model to: {output_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Simple weight merge failed: {e}")
        return False

def create_dummy_checkpoint(path: str, size_mb: float = 1.0):
    """Create a dummy checkpoint for testing.
    
    Args:
        path: Path to save the dummy checkpoint
        size_mb: Size of the dummy checkpoint in MB
    """
    logger.info(f"Creating dummy checkpoint: {path}")
    
    # Create a simple dummy state dict
    dummy_state = {
        'unet.conv_in.weight': torch.randn(320, 4, 3, 3),
        'unet.conv_in.bias': torch.randn(320),
        'unet.conv_out.weight': torch.randn(4, 320, 3, 3),
        'unet.conv_out.bias': torch.randn(4),
        'unet.time_embedding.linear_1.weight': torch.randn(1280, 320),
        'unet.time_embedding.linear_1.bias': torch.randn(1280),
        'unet.time_embedding.linear_2.weight': torch.randn(1280, 1280),
        'unet.time_embedding.linear_2.bias': torch.randn(1280),
    }
    
    # Add more parameters to reach desired size
    target_params = int(size_mb * 1024 * 1024 / 4)  # 4 bytes per float32
    current_params = sum(t.numel() for t in dummy_state.values())
    
    if current_params < target_params:
        remaining_params = target_params - current_params
        dummy_state['dummy_large_weight'] = torch.randn(remaining_params)
    
    # Save as safetensors
    save_file(dummy_state, path)
    logger.info(f"Created dummy checkpoint: {path} ({os.path.getsize(path) / (1024*1024):.2f} MB)")

def create_dummy_lora(path: str, size_mb: float = 0.1):
    """Create a dummy LoRA for testing that matches the base checkpoint structure.
    
    Args:
        path: Path to save the dummy LoRA
        size_mb: Size of the dummy LoRA in MB
    """
    logger.info(f"Creating dummy LoRA: {path}")
    
    # Create dummy LoRA weights that match the base checkpoint structure
    # LoRA uses low-rank decomposition: W = W_base + alpha * (up @ down)
    rank = 16  # LoRA rank
    
    dummy_lora = {
        # For conv_in: (320, 4, 3, 3) -> down: (rank, 4*3*3), up: (320, rank)
        'unet.conv_in.lora_down.weight': torch.randn(rank, 4 * 3 * 3),
        'unet.conv_in.lora_up.weight': torch.randn(320, rank),
        
        # For conv_out: (4, 320, 3, 3) -> down: (rank, 320*3*3), up: (4, rank)
        'unet.conv_out.lora_down.weight': torch.randn(rank, 320 * 3 * 3),
        'unet.conv_out.lora_up.weight': torch.randn(4, rank),
        
        # For linear layers: (out_features, in_features) -> down: (rank, in_features), up: (out_features, rank)
        'unet.time_embedding.linear_1.lora_down.weight': torch.randn(rank, 320),
        'unet.time_embedding.linear_1.lora_up.weight': torch.randn(1280, rank),
        'unet.time_embedding.linear_2.lora_down.weight': torch.randn(rank, 1280),
        'unet.time_embedding.linear_2.lora_up.weight': torch.randn(1280, rank),
    }
    
    # Add more parameters to reach desired size
    target_params = int(size_mb * 1024 * 1024 / 4)  # 4 bytes per float32
    current_params = sum(t.numel() for t in dummy_lora.values())
    
    if current_params < target_params:
        remaining_params = target_params - current_params
        # Add some extra LoRA layers to reach target size
        extra_layers = remaining_params // (rank * 2)
        for i in range(extra_layers):
            dummy_lora[f'unet.extra_layer_{i}.lora_down.weight'] = torch.randn(rank, 64)
            dummy_lora[f'unet.extra_layer_{i}.lora_up.weight'] = torch.randn(64, rank)
    
    # Save as safetensors
    save_file(dummy_lora, path)
    logger.info(f"Created dummy LoRA: {path} ({os.path.getsize(path) / (1024*1024):.2f} MB)")

def _handle_merge_result(success: bool, output_path: str, context: str = "merge") -> None:
    """Handle the result of a LoRA merge operation."""
    if success:
        logger.info(f"LoRA {context} completed successfully")
        print(f"✅ Successfully merged LoRA into: {output_path}")
    else:
        logger.error(f"LoRA {context} failed")
        print(f"❌ LoRA {context} failed. Check logs for details.")
        sys.exit(1)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='DreamLayer LoRA Auto-Merge Utility')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Merge LoRA command
    merge_parser = subparsers.add_parser('merge-lora', help='Merge LoRA with base model')
    merge_parser.add_argument('base_model', help='Path to base model (.safetensors)')
    merge_parser.add_argument('lora_model', help='Path to LoRA model (.safetensors)')
    merge_parser.add_argument('output_model', help='Path to save merged model (.safetensors)')
    merge_parser.add_argument('--alpha', type=float, default=1.0, help='LoRA strength (default: 1.0)')
    merge_parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto', 
                             help='Device to use (default: auto)')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run test with dummy checkpoints')
    test_parser.add_argument('--temp-dir', default='./temp_test', help='Temporary directory for test files')
    
    # Create dummy files command
    dummy_parser = subparsers.add_parser('create-dummy', help='Create dummy checkpoint and LoRA files')
    dummy_parser.add_argument('base_path', help='Path to save dummy base checkpoint')
    dummy_parser.add_argument('lora_path', help='Path to save dummy LoRA')
    dummy_parser.add_argument('--base-size', type=float, default=1.0, help='Base checkpoint size in MB')
    dummy_parser.add_argument('--lora-size', type=float, default=0.1, help='LoRA size in MB')
    
    args = parser.parse_args()
    
    if args.command == 'merge-lora':
        logger.info("Starting LoRA merge operation")
        success = merge_lora_with_base(
            args.base_model, 
            args.lora_model, 
            args.output_model,
            alpha=args.alpha,
            device=args.device
        )
        _handle_merge_result(success, args.output_model, "merge")
    
    elif args.command == 'test':
        logger.info("Running test with dummy checkpoints")
        
        # Create temp directory
        temp_dir = Path(args.temp_dir)
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Create dummy files
            base_path = temp_dir / "dummy_base.safetensors"
            lora_path = temp_dir / "dummy_lora.safetensors"
            output_path = temp_dir / "dummy_merged.safetensors"
            
            create_dummy_checkpoint(str(base_path))
            create_dummy_lora(str(lora_path))
            
            # Test merge
            success = merge_lora_with_base(
                str(base_path),
                str(lora_path),
                str(output_path),
                alpha=0.8,
                device='cpu'  # Use CPU for testing
            )
            
            if success and output_path.exists() and output_path.stat().st_size > 0:
                logger.info(f"✅ Test passed! Output file size: {output_path.stat().st_size} bytes")
                print(f"✅ Test passed! Created merged model: {output_path}")
                print(f"   File size: {output_path.stat().st_size / (1024*1024):.2f} MB")
            else:
                logger.error("❌ Test failed!")
                print("❌ Test failed! Output file not created or empty.")
                sys.exit(1)
            
        except Exception as e:
            logger.error(f"Test failed with exception: {e}")
            print(f"❌ Test failed: {e}")
            sys.exit(1)
        
        finally:
            # Clean up temp files
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                logger.info("Cleaned up temporary test files")
    
    elif args.command == 'create-dummy':
        create_dummy_checkpoint(args.base_path, args.base_size)
        create_dummy_lora(args.lora_path, args.lora_size)
        print(f"✅ Created dummy files:\n  Base: {args.base_path}\n  LoRA: {args.lora_path}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()