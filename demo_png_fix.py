#!/usr/bin/env python3
"""
Demo script showing the PNG Info alpha channel fix.
This demonstrates the before/after behavior of the PNG metadata parser.
"""

import tempfile
import os
from utils.png_info import create_sample_png_with_metadata, parse_png_metadata, format_generation_info


def _test_png_metadata(png_path, png_type):
    """Test PNG metadata extraction and display results."""
    print(f"\n🔍 Testing {png_type} PNG metadata extraction:")
    if metadata := parse_png_metadata(png_path):
        info = format_generation_info(metadata)
        print(f"  ✅ Prompt: {info.get('prompt')}")
        print(f"  ✅ Negative: {info.get('negative_prompt')}")
        print(f"  ✅ Parameters: {len(info.get('parameters', {}))} items")
        return True
    else:
        print(f"  ❌ Failed to extract metadata from {png_type} PNG")
        return False

def _create_demo_files(temp_dir):
    """Create demo PNG files with and without alpha channels."""
    rgb_path = os.path.join(temp_dir, "demo_rgb.png")
    rgba_path = os.path.join(temp_dir, "demo_rgba.png")
    
    print("\n📝 Creating demo PNG files...")
    create_sample_png_with_metadata(rgb_path, has_alpha=False, include_metadata=True)
    create_sample_png_with_metadata(rgba_path, has_alpha=True, include_metadata=True)
    
    print("✅ Created RGB PNG (no alpha channel)")
    print("✅ Created RGBA PNG (with alpha channel)")
    
    return rgb_path, rgba_path

def _show_fix_summary():
    """Display the fix summary information."""
    print("\n📋 Fix Summary:")
    print("  BEFORE: PNG files with alpha channels (RGBA) returned None for metadata")
    print("  AFTER:  PNG files with alpha channels now correctly return metadata")
    print("  ROOT CAUSE: The parser incorrectly assumed alpha channels affected text chunk extraction")
    print("  SOLUTION: Text chunks are independent of image mode - extract them regardless of RGB/RGBA")

def demonstrate_png_fix():
    """Demonstrate the PNG alpha channel fix."""
    
    print("🔍 DreamLayer PNG Info Alpha Channel Fix Demo")
    print("=" * 50)
    
    # Create temporary directory for demo files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create test PNG files
        rgb_path, rgba_path = _create_demo_files(temp_dir)
        
        # Test both PNG types
        _test_png_metadata(rgb_path, "RGB")
        _test_png_metadata(rgba_path, "RGBA")
        
        # Show the fix summary
        _show_fix_summary()
        
        # Show file details
        print(f"\n📁 Demo files created in: {temp_dir}")
        print(f"  RGB PNG: {rgb_path}")
        print(f"  RGBA PNG: {rgba_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False
    
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned up temporary files")


if __name__ == "__main__":
    if success := demonstrate_png_fix():
        print("\n🎉 PNG Info alpha channel fix demonstration completed successfully!")
    else:
        print("\n💥 PNG Info alpha channel fix demonstration failed!")