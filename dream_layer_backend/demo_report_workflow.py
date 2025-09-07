#!/usr/bin/env python3
"""
Demo script showing the complete DreamLayer Report Generation workflow
This demonstrates the end-to-end functionality of the report system
"""

import os
import json
import tempfile
import shutil
import zipfile
import csv
from datetime import datetime
from pathlib import Path

# Import the report generator
from report_generator import ReportGenerator, ImageRecord

def create_demo_environment():
    """Create a realistic demo environment with sample data"""
    print("🏗️  Creating demo environment...")
    
    # Create temporary directory structure
    demo_dir = tempfile.mkdtemp(prefix="dreamlayer_demo_")
    served_images_dir = os.path.join(demo_dir, "served_images")
    reports_dir = os.path.join(demo_dir, "reports")
    
    os.makedirs(served_images_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    # Create sample image files with realistic names
    sample_images = [
        "txt2img_landscape_20240108_143022.png",
        "txt2img_portrait_20240108_143155.png", 
        "txt2img_cyberpunk_20240108_143301.png",
        "img2img_enhanced_photo_20240108_144523.png",
        "img2img_style_transfer_20240108_144721.png",
        "txt2img_fantasy_castle_20240108_145002.png"
    ]
    
    # Create realistic file sizes
    file_sizes = [1024*150, 1024*200, 1024*180, 1024*175, 1024*190, 1024*165]
    
    for img_name, size in zip(sample_images, file_sizes):
        img_path = os.path.join(served_images_dir, img_name)
        with open(img_path, 'wb') as f:
            f.write(b"PNG_IMAGE_DATA" * (size // 14))  # Approximate file size
    
    # Create realistic gallery data
    gallery_data = {
        "txt2img": [
            {
                "id": "txt2img_001",
                "filename": "txt2img_landscape_20240108_143022.png",
                "url": "http://localhost:5001/api/images/txt2img_landscape_20240108_143022.png",
                "prompt": "Epic mountain landscape at sunset, dramatic clouds, golden hour lighting, photorealistic, highly detailed",
                "negativePrompt": "blurry, low quality, watermark, text, signature",
                "timestamp": "2024-01-08T14:30:22.000Z",
                "settings": {
                    "model_name": "juggernautXL_v8Rundiffusion.safetensors",
                    "sampler_name": "euler",
                    "steps": 30,
                    "cfg_scale": 7.5,
                    "width": 1024,
                    "height": 768,
                    "seed": 123456789,
                    "lora": {
                        "name": "landscape_enhancer_v2.safetensors",
                        "strength": 0.8
                    }
                }
            },
            {
                "id": "txt2img_002",
                "filename": "txt2img_portrait_20240108_143155.png",
                "url": "http://localhost:5001/api/images/txt2img_portrait_20240108_143155.png",
                "prompt": "Portrait of a young woman, professional headshot, studio lighting, 85mm lens",
                "negativePrompt": "cartoon, anime, low resolution, distorted face",
                "timestamp": "2024-01-08T14:31:55.000Z",
                "settings": {
                    "model_name": "realvisxlV40_v40Bakedvae.safetensors",
                    "sampler_name": "dpmpp_2m",
                    "steps": 25,
                    "cfg_scale": 8.0,
                    "width": 768,
                    "height": 1024,
                    "seed": 987654321
                }
            },
            {
                "id": "txt2img_003",
                "filename": "txt2img_cyberpunk_20240108_143301.png",
                "url": "http://localhost:5001/api/images/txt2img_cyberpunk_20240108_143301.png",
                "prompt": "Cyberpunk city street at night, neon lights, rain reflections, futuristic vehicles",
                "negativePrompt": "bright daylight, rural, nature, vintage",
                "timestamp": "2024-01-08T14:33:01.000Z",
                "settings": {
                    "model_name": "flux1-dev-fp8.safetensors",
                    "sampler_name": "euler",
                    "steps": 20,
                    "cfg_scale": 7.0,
                    "width": 1024,
                    "height": 576,
                    "seed": 555666777
                }
            },
            {
                "id": "txt2img_004",
                "filename": "txt2img_fantasy_castle_20240108_145002.png",
                "url": "http://localhost:5001/api/images/txt2img_fantasy_castle_20240108_145002.png",
                "prompt": "Medieval fantasy castle on a hilltop, magical atmosphere, dragons flying overhead",
                "negativePrompt": "modern, contemporary, realistic architecture",
                "timestamp": "2024-01-08T14:50:02.000Z",
                "settings": {
                    "model_name": "sdXL_v10VAEFix.safetensors",
                    "sampler_name": "dpmpp_sde",
                    "steps": 35,
                    "cfg_scale": 9.0,
                    "width": 1024,
                    "height": 1024,
                    "seed": 111222333
                }
            }
        ],
        "img2img": [
            {
                "id": "img2img_001",
                "filename": "img2img_enhanced_photo_20240108_144523.png",
                "url": "http://localhost:5001/api/images/img2img_enhanced_photo_20240108_144523.png",
                "prompt": "Enhance this photo with better lighting and details, photorealistic enhancement",
                "negativePrompt": "artificial, over-processed, cartoon style",
                "timestamp": "2024-01-08T14:45:23.000Z",
                "settings": {
                    "model_name": "realvisxlV40_v40Bakedvae.safetensors",
                    "sampler_name": "euler",
                    "steps": 20,
                    "cfg_scale": 7.5,
                    "width": 768,
                    "height": 768,
                    "seed": 444555666,
                    "denoising_strength": 0.65,
                    "input_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
                }
            },
            {
                "id": "img2img_002", 
                "filename": "img2img_style_transfer_20240108_144721.png",
                "url": "http://localhost:5001/api/images/img2img_style_transfer_20240108_144721.png",
                "prompt": "Apply oil painting style to this image, artistic interpretation",
                "negativePrompt": "photorealistic, digital, sharp edges",
                "timestamp": "2024-01-08T14:47:21.000Z",
                "settings": {
                    "model_name": "sd_xl_base_1.0.safetensors",
                    "sampler_name": "dpmpp_2m",
                    "steps": 30,
                    "cfg_scale": 8.5,
                    "width": 1024,
                    "height": 768,
                    "seed": 777888999,
                    "denoising_strength": 0.75,
                    "controlnet": {
                        "enabled": True,
                        "model": "canny_controlnet_v1.safetensors",
                        "strength": 0.9
                    }
                }
            }
        ]
    }
    
    return demo_dir, served_images_dir, reports_dir, gallery_data

def create_demo_generator(demo_dir, served_images_dir, reports_dir, gallery_data):
    """Create a report generator configured for the demo"""
    
    class DemoReportGenerator(ReportGenerator):
        def __init__(self):
            self.served_images_dir = served_images_dir
            self.reports_dir = reports_dir
            self.output_dir = os.path.join(demo_dir, 'output')
            os.makedirs(self.output_dir, exist_ok=True)
        
        def fetch_gallery_data(self):
            return gallery_data
        
        def _get_models_info(self):
            return {
                'checkpoints': [
                    'juggernautXL_v8Rundiffusion.safetensors',
                    'realvisxlV40_v40Bakedvae.safetensors', 
                    'flux1-dev-fp8.safetensors',
                    'sdXL_v10VAEFix.safetensors',
                    'sd_xl_base_1.0.safetensors'
                ],
                'loras': [
                    'landscape_enhancer_v2.safetensors',
                    'portrait_fix_v1.safetensors',
                    'style_enhancer.safetensors'
                ],
                'controlnet': [
                    'canny_controlnet_v1.safetensors',
                    'depth_controlnet_v2.safetensors',
                    'openpose_controlnet.safetensors'
                ]
            }
    
    return DemoReportGenerator()

def analyze_report_bundle(report_path):
    """Analyze the generated report bundle and show detailed statistics"""
    print(f"\n📊 Analyzing report bundle: {os.path.basename(report_path)}")
    print("-" * 60)
    
    # Get bundle size
    bundle_size = os.path.getsize(report_path)
    print(f"Bundle size: {bundle_size:,} bytes ({bundle_size/1024:.1f} KB)")
    
    # Extract and analyze contents
    with zipfile.ZipFile(report_path, 'r') as zipf:
        file_list = zipf.namelist()
        print(f"Files in bundle: {len(file_list)}")
        
        # Analyze directory structure
        directories = set()
        for file_path in file_list:
            if '/' in file_path:
                directories.add(file_path.split('/')[0])
        
        print(f"Directory structure:")
        for directory in sorted(directories):
            files_in_dir = [f for f in file_list if f.startswith(directory + '/')]
            print(f"  {directory}/: {len(files_in_dir)} files")
        
        # Analyze CSV content
        if 'results.csv' in file_list:
            with zipf.open('results.csv') as csv_file:
                csv_content = csv_file.read().decode('utf-8')
                reader = csv.DictReader(csv_content.splitlines())
                rows = list(reader)
                
                print(f"\nCSV Analysis:")
                print(f"  Total records: {len(rows)}")
                
                # Count by generation type
                gen_types = {}
                models = set()
                samplers = set()
                
                for row in rows:
                    gen_type = row.get('generation_type', 'unknown')
                    gen_types[gen_type] = gen_types.get(gen_type, 0) + 1
                    models.add(row.get('model_name', 'unknown'))
                    samplers.add(row.get('sampler_name', 'unknown'))
                
                for gen_type, count in gen_types.items():
                    print(f"  {gen_type}: {count} images")
                
                print(f"  Unique models: {len(models)}")
                print(f"  Unique samplers: {len(samplers)}")
        
        # Analyze config.json
        if 'config.json' in file_list:
            with zipf.open('config.json') as config_file:
                config = json.load(config_file)
                
                print(f"\nConfiguration Analysis:")
                print(f"  Report format version: {config.get('report_metadata', {}).get('report_format_version', 'unknown')}")
                print(f"  Available checkpoints: {len(config.get('available_models', {}).get('checkpoints', []))}")
                print(f"  Available LoRAs: {len(config.get('available_models', {}).get('loras', []))}")
                print(f"  Available ControlNets: {len(config.get('available_models', {}).get('controlnet', []))}")
        
        # Check README.md
        if 'README.md' in file_list:
            with zipf.open('README.md') as readme_file:
                readme_content = readme_file.read().decode('utf-8')
                lines = readme_content.count('\n')
                words = len(readme_content.split())
                print(f"\nREADME Analysis:")
                print(f"  Lines: {lines}")
                print(f"  Words: {words}")

def demo_workflow():
    """Run the complete demo workflow"""
    print("🚀 DreamLayer Report Generation Demo")
    print("=" * 70)
    
    try:
        # Step 1: Create demo environment
        demo_dir, served_images_dir, reports_dir, gallery_data = create_demo_environment()
        print(f"✅ Demo environment created at: {demo_dir}")
        
        # Step 2: Show gallery data statistics
        total_txt2img = len(gallery_data['txt2img'])
        total_img2img = len(gallery_data['img2img'])
        total_images = total_txt2img + total_img2img
        
        print(f"\n📸 Gallery Data Summary:")
        print(f"   txt2img images: {total_txt2img}")
        print(f"   img2img images: {total_img2img}")
        print(f"   Total images: {total_images}")
        
        # Step 3: Create and configure report generator
        print(f"\n⚙️  Configuring report generator...")
        generator = create_demo_generator(demo_dir, served_images_dir, reports_dir, gallery_data)
        
        # Step 4: Generate report bundle
        print(f"\n📦 Generating report bundle...")
        result = generator.create_report_bundle("dreamlayer_demo_report.zip")
        
        if result['status'] == 'success':
            print(f"✅ Report generated successfully!")
            print(f"   Filename: {result['report_filename']}")
            print(f"   Path: {result['report_path']}")
            print(f"   Total images: {result['total_images']}")
            print(f"   Bundle size: {result['bundle_size_bytes']:,} bytes")
            print(f"   Generation types: {', '.join(result['generation_types'])}")
            
            # Step 5: Validate report
            print(f"\n🔍 Validation Results:")
            csv_valid = result['csv_validation']['valid']
            path_valid = result['path_validation']['valid']
            print(f"   CSV schema: {'✅ Valid' if csv_valid else '❌ Invalid'}")
            print(f"   Path resolution: {'✅ All paths resolved' if path_valid else '❌ Missing paths'}")
            
            if not csv_valid:
                print(f"   Missing CSV columns: {result['csv_validation']['missing_columns']}")
            
            if not path_valid:
                print(f"   Missing paths: {result['path_validation']['missing_paths']}")
            
            # Step 6: Analyze the generated report
            analyze_report_bundle(result['report_path'])
            
            # Step 7: Demonstrate CSV schema validation
            print(f"\n🧪 Testing CSV Schema Validation:")
            csv_path = os.path.join(demo_dir, 'extracted_results.csv')
            with zipfile.ZipFile(result['report_path'], 'r') as zipf:
                with zipf.open('results.csv') as csv_file:
                    with open(csv_path, 'wb') as f:
                        f.write(csv_file.read())
            
            validation = ImageRecord.validate_csv_schema(csv_path)
            print(f"   Schema validation: {'✅ Passed' if validation['valid'] else '❌ Failed'}")
            print(f"   Required columns: {len(validation['required_columns'])}")
            print(f"   Actual columns: {len(validation['actual_columns'])}")
            print(f"   Rows processed: {validation['row_count']}")
            
            return result['report_path']
            
        else:
            print(f"❌ Report generation failed: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        # Cleanup
        if 'demo_dir' in locals():
            print(f"\n🧹 Cleaning up demo environment...")
            shutil.rmtree(demo_dir)
            print(f"✅ Demo environment cleaned up")

if __name__ == "__main__":
    print("Starting DreamLayer Report Generation Demo...")
    result_path = demo_workflow()
    
    if result_path:
        print(f"\n🎉 Demo completed successfully!")
        print(f"Report was generated at: {result_path}")
        print(f"\nThe report bundle contains:")
        print(f"  • Standardized CSV with image metadata")
        print(f"  • Complete system configuration")
        print(f"  • Organized image collections")
        print(f"  • Human-readable documentation")
        print(f"  • Full path validation and schema compliance")
    else:
        print(f"\n❌ Demo failed to complete")
    
    print(f"\n" + "=" * 70)
