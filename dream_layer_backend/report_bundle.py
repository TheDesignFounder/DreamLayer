import os
import csv
import json
import zipfile
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import asdict
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import requests
from run_registry import RunRegistry, RunConfig

class ReportBundleGenerator:
    """Generates report bundles with CSV, config, images, and README"""
    
    def __init__(self, output_dir: str = "Dream_Layer_Resources/output"):
        self.output_dir = output_dir
        self.registry = RunRegistry()
        
    def generate_csv(self, runs: List[RunConfig]) -> str:
        """Generate results.csv with required columns"""
        csv_path = "temp_results.csv"
        
        # Define required CSV columns based on schema
        required_columns = [
            'run_id',
            'timestamp', 
            'model',
            'vae',
            'prompt',
            'negative_prompt',
            'seed',
            'sampler',
            'steps',
            'cfg_scale',
            'width',
            'height',
            'batch_size',
            'batch_count',
            'generation_type',
            'image_paths',
            'loras',
            'controlnets',
            'workflow_hash'
        ]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=required_columns)
            writer.writeheader()
            
            for run in runs:
                # Prepare loras and controlnets as JSON strings
                loras_json = json.dumps(run.loras) if run.loras else "[]"
                controlnets_json = json.dumps(run.controlnets) if run.controlnets else "[]"
                
                # Create workflow hash for identification
                workflow_hash = str(hash(json.dumps(run.workflow, sort_keys=True)))
                
                # Join image paths
                image_paths = ";".join(run.generated_images) if run.generated_images else ""
                
                row = {
                    'run_id': run.run_id,
                    'timestamp': run.timestamp,
                    'model': run.model,
                    'vae': run.vae or "",
                    'prompt': run.prompt,
                    'negative_prompt': run.negative_prompt,
                    'seed': run.seed,
                    'sampler': run.sampler,
                    'steps': run.steps,
                    'cfg_scale': run.cfg_scale,
                    'width': run.width,
                    'height': run.height,
                    'batch_size': run.batch_size,
                    'batch_count': run.batch_count,
                    'generation_type': run.generation_type,
                    'image_paths': image_paths,
                    'loras': loras_json,
                    'controlnets': controlnets_json,
                    'workflow_hash': workflow_hash
                }
                writer.writerow(row)
        
        return csv_path
    
    def validate_csv_schema(self, csv_path: str) -> bool:
        """Validate that CSV has all required columns"""
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                
                required_columns = [
                    'run_id', 'timestamp', 'model', 'vae', 'prompt', 
                    'negative_prompt', 'seed', 'sampler', 'steps', 'cfg_scale',
                    'width', 'height', 'batch_size', 'batch_count', 
                    'generation_type', 'image_paths', 'loras', 'controlnets', 'workflow_hash'
                ]
                
                missing_columns = [col for col in required_columns if col not in fieldnames]
                if missing_columns:
                    print(f"❌ Missing required columns: {missing_columns}")
                    return False
                
                print(f"✅ CSV schema validation passed")
                return True
                
        except Exception as e:
            print(f"❌ CSV schema validation failed: {e}")
            return False
    
    def copy_images_to_bundle(self, runs: List[RunConfig], bundle_dir: str) -> List[str]:
        """Copy selected grid images to bundle directory"""
        copied_images = []
        
        for run in runs:
            for image_filename in run.generated_images:
                if image_filename:
                    # Source path in output directory
                    src_path = os.path.join(self.output_dir, image_filename)
                    
                    if os.path.exists(src_path):
                        # Destination in bundle
                        dest_path = os.path.join(bundle_dir, "images", image_filename)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        
                        try:
                            shutil.copy2(src_path, dest_path)
                            copied_images.append(image_filename)
                            print(f"✅ Copied image: {image_filename}")
                        except Exception as e:
                            print(f"❌ Failed to copy {image_filename}: {e}")
                    else:
                        print(f"⚠️ Image not found: {src_path}")
        
        return copied_images
    
    def create_config_json(self, runs: List[RunConfig]) -> str:
        """Create config.json with run configurations"""
        config_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_runs": len(runs),
                "generation_types": list(set(run.generation_type for run in runs)),
                "models_used": list(set(run.model for run in runs))
            },
            "runs": [asdict(run) for run in runs]
        }
        
        config_path = "temp_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return config_path
    
    def create_readme(self, runs: List[RunConfig], copied_images: List[str]) -> str:
        """Create README.md for the report bundle"""
        readme_content = f"""# Dream Layer Report Bundle

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
This report bundle contains {len(runs)} completed image generation runs with their configurations and results.

## Contents
- `results.csv` - Tabular data of all runs with metadata
- `config.json` - Detailed configuration data for each run
- `images/` - Generated images from all runs
- `README.md` - This file

## Statistics
- Total runs: {len(runs)}
- Generation types: {', '.join(set(run.generation_type for run in runs))}
- Models used: {', '.join(set(run.model for run in runs))}
- Images included: {len(copied_images)}

## CSV Schema
The results.csv file contains the following columns:
- run_id: Unique identifier for each run
- timestamp: When the run was executed
- model: Model used for generation
- vae: VAE model (if any)
- prompt: Positive prompt
- negative_prompt: Negative prompt
- seed: Random seed used
- sampler: Sampling method
- steps: Number of sampling steps
- cfg_scale: CFG scale value
- width/height: Image dimensions
- batch_size/batch_count: Batch settings
- generation_type: txt2img or img2img
- image_paths: Semicolon-separated list of generated image filenames
- loras: JSON array of LoRA configurations
- controlnets: JSON array of ControlNet configurations
- workflow_hash: Hash of the workflow configuration

## File Paths
All image paths in the CSV resolve to files present in this zip bundle.
"""
        
        readme_path = "temp_README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return readme_path
    
    def create_report_bundle(self, run_ids: Optional[List[str]] = None) -> str:
        """Create a complete report bundle"""
        
        # Get runs to include
        if run_ids:
            runs = [self.registry.get_run(run_id) for run_id in run_ids if self.registry.get_run(run_id)]
        else:
            runs = self.registry.get_all_runs()
        
        if not runs:
            raise ValueError("No runs found to include in report")
        
        print(f"📊 Creating report bundle with {len(runs)} runs")
        
        # Create temporary directory for bundle
        bundle_dir = f"temp_report_bundle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(bundle_dir, exist_ok=True)
        
        try:
            # Generate CSV
            print("📝 Generating results.csv...")
            csv_path = self.generate_csv(runs)
            
            # Validate CSV schema
            if not self.validate_csv_schema(csv_path):
                raise ValueError("CSV schema validation failed")
            
            # Copy CSV to bundle
            shutil.copy2(csv_path, os.path.join(bundle_dir, "results.csv"))
            
            # Create config.json
            print("⚙️ Creating config.json...")
            config_path = self.create_config_json(runs)
            shutil.copy2(config_path, os.path.join(bundle_dir, "config.json"))
            
            # Copy images
            print("🖼️ Copying images...")
            copied_images = self.copy_images_to_bundle(runs, bundle_dir)
            
            # Create README
            print("📖 Creating README.md...")
            readme_path = self.create_readme(runs, copied_images)
            shutil.copy2(readme_path, os.path.join(bundle_dir, "README.md"))
            
            # Create zip file
            print("📦 Creating report.zip...")
            zip_path = "report.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(bundle_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, bundle_dir)
                        zipf.write(file_path, arcname)
            
            # Cleanup temp files
            for temp_file in [csv_path, config_path, readme_path]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            # Cleanup temp directory
            shutil.rmtree(bundle_dir)
            
            print(f"✅ Report bundle created: {zip_path}")
            return zip_path
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(bundle_dir):
                shutil.rmtree(bundle_dir)
            raise e

# Flask app for report bundle API
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:*", "http://127.0.0.1:*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

generator = ReportBundleGenerator()

@app.route('/api/report-bundle', methods=['POST'])
def create_report_bundle():
    """Create a report bundle with selected runs"""
    try:
        data = request.json or {}
        run_ids = data.get('run_ids', [])  # Empty list means all runs
        
        zip_path = generator.create_report_bundle(run_ids)
        
        return jsonify({
            "status": "success",
            "message": "Report bundle created successfully",
            "file_path": zip_path
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/report-bundle/download', methods=['GET'])
def download_report_bundle():
    """Download the generated report.zip file"""
    try:
        zip_path = "report.zip"
        if not os.path.exists(zip_path):
            return jsonify({
                "status": "error",
                "message": "Report bundle not found. Please generate one first."
            }), 404
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name="report.zip",
            mimetype="application/zip"
        )
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/report-bundle/validate', methods=['POST'])
def validate_report_bundle():
    """Validate a report bundle schema"""
    try:
        data = request.json or {}
        csv_content = data.get('csv_content', '')
        
        # Write CSV content to temp file for validation
        temp_csv = "temp_validation.csv"
        with open(temp_csv, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        is_valid = generator.validate_csv_schema(temp_csv)
        
        # Cleanup
        if os.path.exists(temp_csv):
            os.remove(temp_csv)
        
        return jsonify({
            "status": "success",
            "valid": is_valid
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True) 