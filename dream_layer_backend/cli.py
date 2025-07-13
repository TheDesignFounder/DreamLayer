#!/usr/bin/env python3
"""
DreamLayer CLI

Command-line interface for DreamLayer AI utilities, including LoRA merging functionality.
"""

import argparse
import sys
import os
import logging
from pathlib import Path

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from .dream_layer_backend_utils.lora_merger_bridge import (
        merge_lora_weights,
        validate_safetensors_file,
        test_merge_functionality,
        check_comfyui_availability,
        get_comfyui_version
    )
except ImportError:
    # Fallback for when running as script
    from dream_layer_backend_utils.lora_merger_bridge import (
        merge_lora_weights,
        validate_safetensors_file,
        test_merge_functionality,
        check_comfyui_availability,
        get_comfyui_version
    )


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def merge_lora_command(args: argparse.Namespace) -> int:
    """
    Handle the merge-lora command.

    Args:
        args: Parsed command line arguments

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        # Check ComfyUI availability
        if not check_comfyui_availability():
            print("❌ Error: ComfyUI is not available. Please ensure ComfyUI is properly installed.")
            return 1

        comfyui_version = get_comfyui_version()
        if comfyui_version:
            logging.info(f"🔧 Using ComfyUI version: {comfyui_version}")

        # Validate input files
        if not validate_safetensors_file(args.base):
            logging.error(f"❌ Error: Invalid base model file: {args.base}")
            return 1

        if not validate_safetensors_file(args.lora):
            logging.error(f"❌ Error: Invalid LoRA file: {args.lora}")
            return 1

        # Ensure output directory exists
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logging.info(f"🔄 Starting LoRA merge...")
        logging.info(f"   Base model: {args.base}")
        logging.info(f"   LoRA model: {args.lora}")
        logging.info(f"   Output: {args.output}")
        logging.info(f"   Scale: {args.scale}")

        # Perform the merge
        success = merge_lora_weights(
            base_path=args.base,
            lora_path=args.lora,
            output_path=args.output,
            lora_scale=args.scale,
            alpha=args.alpha
        )

        if success:
            # Verify output file
            if os.path.exists(args.output):
                stat = os.stat(args.output)
                if stat.st_size > 0:
                    logging.info(f"✅ LoRA merge completed successfully!")
                    logging.info(f"   Output file size: {stat.st_size:,} bytes")
                    return 0
                else:
                    logging.error(f"❌ Error: Output file is empty")
                    return 1
            else:
                logging.error(f"❌ Error: Output file was not created")
                return 1
        else:
            logging.error(f"❌ Error: LoRA merge failed")
            return 1

    except Exception as e:
        logging.error(f"❌ Error during LoRA merge: {e}")
        return 1


def test_command(args: argparse.Namespace) -> int:
    """
    Handle the test command.

    Args:
        args: Parsed command line arguments

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        # Check ComfyUI availability
        if not check_comfyui_availability():
            logging.error("❌ Error: ComfyUI is not available. Please ensure ComfyUI is properly installed.")
            return 1

        comfyui_version = get_comfyui_version()
        if comfyui_version:
            logging.info(f"🔧 Using ComfyUI version: {comfyui_version}")

        logging.info("🧪 Testing LoRA merge functionality...")

        success = test_merge_functionality()

        if success:
            logging.info("✅ All tests passed!")
            return 0
        else:
            logging.error("❌ Tests failed!")
            return 1

    except Exception as e:
        logging.error(f"❌ Error during testing: {e}")
        return 1


def main() -> int:
    """
    Main CLI entry point.

    Returns:
        int: Exit code
    """
    parser = argparse.ArgumentParser(
        description="DreamLayer AI CLI - LoRA merging and utilities (powered by ComfyUI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dreamlayer merge-lora base.safetensors lora.safetensors merged.safetensors
  dreamlayer merge-lora base.safetensors lora.safetensors merged.safetensors --scale 0.8
  dreamlayer test

Note: This CLI requires ComfyUI to be installed and available in the project.
        """
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
    )

    # merge-lora command
    merge_parser = subparsers.add_parser(
        'merge-lora',
        help='Merge LoRA weights with a base model'
    )
    merge_parser.add_argument(
        'base',
        help='Path to the base model .safetensors file'
    )
    merge_parser.add_argument(
        'lora',
        help='Path to the LoRA .safetensors file'
    )
    merge_parser.add_argument(
        'output',
        help='Path for the output merged model .safetensors file'
    )
    merge_parser.add_argument(
        '--scale', '-s',
        type=float,
        default=1.0,
        help='LoRA scaling factor (default: 1.0)'
    )
    merge_parser.add_argument(
        '--alpha', '-a',
        type=float,
        default=1.0,
        help='Alpha parameter for LoRA merging (default: 1.0)'
    )

    # test command
    test_parser = subparsers.add_parser(
        'test',
        help='Test the LoRA merge functionality with dummy checkpoints'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Handle commands
    if args.command == 'merge-lora':
        return merge_lora_command(args)
    elif args.command == 'test':
        return test_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())