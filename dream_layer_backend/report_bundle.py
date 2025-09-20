"""
Report Bundle Generator with ClipScore Integration
"""

import os
import csv
import json
import zipfile
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import asdict
from flask import Flask, jsonify, request, send_file, make_response
from flask_cors import CORS

# Import consolidated enhancement module
try:
    from dream_layer_backend_utils.run_enhancement import get_enhanced_runs
    ENHANCEMENT_AVAILABLE = True
except ImportError:
    ENHANCEMENT_AVAILABLE = False

# Import run registry
try:
    from run_registry import RunRegistry
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False

class ReportBundleGenerator:
    """Report bundle generator reading exclusively from database"""
    
    def __init__(self, output_dir: str = "Dream_Layer_Resources/output"):
        self.output_dir = output_dir
        # Keep registry only for fallback, primary source is database
        self.registry = RunRegistry() if REGISTRY_AVAILABLE else None
        
    def get_enhanced_runs_data(self, limit: int = None, run_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Get runs data from database (not JSON registry)"""
        try:
            from dream_layer_backend_utils.unified_database_queries import get_all_runs_with_metrics
            
            # Primary: Read from database
            enhanced_runs = get_all_runs_with_metrics()
            
            # Filter by run_ids if provided
            if run_ids:
                enhanced_runs = [run for run in enhanced_runs if run.get('run_id') in run_ids]
            
            if limit:
                enhanced_runs = enhanced_runs[:limit]
            
            print(f"✅ Retrieved {len(enhanced_runs)} runs from database")
            return enhanced_runs
            
        except Exception as e:
            print(f"⚠️ Database read failed: {e}")
            
            # Fallback: Read from JSON registry only if database fails
            if self.registry:
                print("🔄 Falling back to JSON registry...")
                runs = self.registry.get_all_runs()
                if limit:
                    runs = runs[:limit]
                
                fallback_runs = [asdict(run) for run in runs]
                print(f"✅ Retrieved {len(fallback_runs)} runs from JSON fallback")
                return fallback_runs
            else:
                print("❌ No fallback available")
                return []
    
    def generate_csv(self, runs: List = None) -> str:
        """Generate CSV with metrics data (ClipScore focused)"""
        csv_path = "results.csv"
        enhanced_runs = self.get_enhanced_runs_data(run_ids=runs)
        
        if not enhanced_runs:
            # Create empty CSV
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['run_id', 'timestamp', 'model', 'prompt', 'clip_score_mean'])
            return csv_path
        
        # Define CSV columns (metrics focused)
        columns = [
            'run_id', 'timestamp', 'model', 'prompt', 'negative_prompt',
            'seed', 'steps', 'cfg_scale', 'width', 'height',
            'image_count', 'filenames', 'clip_score_mean', 'fid_score', 'macro_precision', 'macro_recall', 'macro_f1'
        ]
        
        # Write CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for run in enhanced_runs:
                csv_row = {}
                for col in columns:
                    if col == 'image_count':
                        images = run.get('generated_images', [])
                        csv_row[col] = len(images) if images else 0
                    elif col == 'filenames':
                        images = run.get('generated_images', [])
                        csv_row[col] = '; '.join(images) if images else ''
                    else:
                        csv_row[col] = run.get(col, '')
                
                writer.writerow(csv_row)
        
        print(f"✅ Generated results.csv with {len(enhanced_runs)} runs")
        return csv_path
    
    def generate_config_json(self, runs: List = None) -> str:
        """Generate config JSON with runs data"""
        config_path = "config.json"
        enhanced_runs = self.get_enhanced_runs_data(run_ids=runs)
        
        # Create runs config (full run data)
        config_data = {
            "runs": [],
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "total_runs": len(enhanced_runs),
                "runs_with_clipscore": len([r for r in enhanced_runs if r.get('clip_score_mean') is not None])
            }
        }
        
        for run in enhanced_runs:
            run_config = {
                key: run.get(key) for key in [
                    'run_id', 'timestamp', 'model', 'vae', 'prompt', 'negative_prompt',
                    'seed', 'sampler', 'steps', 'cfg_scale', 'width', 'height',
                    'batch_size', 'batch_count', 'generation_type', 'loras', 'controlnets',
                    'generated_images', 'workflow', 'version'
                ]
            }
            config_data["runs"].append(run_config)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Generated config.json with {len(enhanced_runs)} runs")
        return config_path
    
    def generate_bundle(self, limit: int = None, include_images: bool = True, run_ids: List[str] = None) -> str:
        """Generate complete report bundle"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_name = f"dreamlayer_report_{timestamp}"
        
        # Read existing metrics from database for report generation
        print("📊 Generating report from existing database metrics...")
        
        # Generate files
        csv_path = self.generate_csv(run_ids)
        config_path = self.generate_config_json(run_ids)
        
        # Create ZIP bundle with Mac compatibility
        zip_path = f"{bundle_name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            zipf.write(csv_path, "results.csv")
            zipf.write(config_path, "config.json")
            
            if include_images:
                self.add_images_to_zip(zipf, run_ids)
        
        # Cleanup temp files
        for temp_file in [csv_path, config_path]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        print(f"✅ Generated bundle: {zip_path}")
        return zip_path
    
    def add_images_to_zip(self, zipf: zipfile.ZipFile, run_ids: List[str] = None):
        """Add image files to ZIP bundle"""
        enhanced_runs = self.get_enhanced_runs_data(run_ids=run_ids)
        added_images = set()
        
        for run in enhanced_runs:
            for filename in run.get('generated_images', []):
                full_path = os.path.join(self.output_dir, filename)
                if os.path.exists(full_path) and filename not in added_images:
                    zipf.write(full_path, f"images/{filename}")
                    added_images.add(filename)

# Flask API
app = Flask(__name__)
CORS(app)

@app.route('/api/report-bundle', methods=['POST'])
def generate_report_bundle_api():
    """Generate report bundle"""
    try:
        data = request.get_json() or {}
        run_ids = data.get('run_ids', [])
        include_images = data.get('include_images', True)
        
        generator = ReportBundleGenerator()
        bundle_path = generator.generate_bundle(include_images=include_images, run_ids=run_ids)
        
        return jsonify({
            'success': True,
            'download_url': f'http://localhost:5006/api/report-bundle/download/{os.path.basename(bundle_path)}',
            'bundle_path': bundle_path,
            'enhancement_available': ENHANCEMENT_AVAILABLE
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/report-bundle/download/<filename>', methods=['GET'])
def download_report_bundle(filename):
    """Download report bundle with Mac compatibility"""
    try:
        if not filename.endswith('.zip'):
            return jsonify({'error': 'Invalid file type'}), 400
        
        file_path = os.path.join('.', filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Read file and create response with explicit headers for Mac
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        response = make_response(file_data)
        response.headers['Content-Type'] = 'application/zip'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Content-Length'] = len(file_data)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/report-status', methods=['GET'])
def report_status_api():
    """Report system status"""
    return jsonify({
        'success': True,
        'status': {
            'enhancement_available': ENHANCEMENT_AVAILABLE,
            'registry_available': REGISTRY_AVAILABLE,
            'data_source': 'enhanced' if ENHANCEMENT_AVAILABLE else 'basic'
        }
    })

if __name__ == "__main__":
    print("🚀 Starting Report Bundle Generator")
    print(f"📊 Enhancement available: {ENHANCEMENT_AVAILABLE}")
    app.run(host='0.0.0.0', port=5006, debug=True)
