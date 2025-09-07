import os
import csv
import json
import zipfile
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
import requests
from dream_layer import get_directories
from dream_layer_backend_utils.fetch_advanced_models import get_settings

@dataclass
class ImageRecord:
    """Schema for CSV records with required validation"""
    id: str
    filename: str
    relative_path: str  # Path within the zip file
    prompt: str
    negative_prompt: str
    model_name: str
    sampler_name: str
    steps: int
    cfg_scale: float
    width: int
    height: int
    seed: int
    timestamp: str  # ISO format
    generation_type: str  # "txt2img" or "img2img"
    batch_index: int
    denoising_strength: Optional[float] = None
    input_image_path: Optional[str] = None
    lora_models: Optional[str] = None  # JSON string of LoRA info
    controlnet_info: Optional[str] = None  # JSON string of ControlNet info
    file_size_bytes: Optional[int] = None
    
    @classmethod
    def get_required_columns(cls) -> List[str]:
        """Return list of required CSV columns for schema validation"""
        return [
            'id', 'filename', 'relative_path', 'prompt', 'negative_prompt',
            'model_name', 'sampler_name', 'steps', 'cfg_scale', 'width', 
            'height', 'seed', 'timestamp', 'generation_type', 'batch_index'
        ]
    
    @classmethod
    def validate_csv_schema(cls, csv_path: str) -> Dict[str, Any]:
        """Validate that CSV has required columns and return validation results"""
        required_cols = cls.get_required_columns()
        
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                actual_cols = reader.fieldnames or []
                
                missing_cols = set(required_cols) - set(actual_cols)
                extra_cols = set(actual_cols) - set(required_cols)
                
                return {
                    'valid': len(missing_cols) == 0,
                    'required_columns': required_cols,
                    'actual_columns': actual_cols,
                    'missing_columns': list(missing_cols),
                    'extra_columns': list(extra_cols),
                    'row_count': sum(1 for _ in reader)
                }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'required_columns': required_cols
            }

class ReportGenerator:
    """Generates comprehensive report bundles with images, CSV data, and configuration"""
    
    def __init__(self):
        self.served_images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'served_images')
        self.output_dir, _ = get_directories()
        self.reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.served_images_dir, exist_ok=True)
    
    def fetch_gallery_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch current gallery data from frontend stores via API"""
        # Try to load from temporary gallery data file first
        gallery_file = os.path.join(os.path.dirname(__file__), 'temp_gallery_data.json')
        
        if os.path.exists(gallery_file):
            try:
                with open(gallery_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and ('txt2img' in data or 'img2img' in data or 'extras' in data):
                        return data
            except Exception as e:
                print(f"Warning: Could not load gallery data from file: {e}")
        
        # Fallback: scan served_images directory and build records
        return self._scan_served_images()
    
    def _scan_served_images(self) -> Dict[str, List[Dict[str, Any]]]:
        """Scan served images directory and build image records"""
        txt2img_images = []
        img2img_images = []
        extras_images = []
        
        if not os.path.exists(self.served_images_dir):
            return {'txt2img': txt2img_images, 'img2img': img2img_images, 'extras': extras_images}
        
        for filename in os.listdir(self.served_images_dir):
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                continue
                
            filepath = os.path.join(self.served_images_dir, filename)
            if not os.path.isfile(filepath):
                continue
            
            # Create basic record from available file info
            stat = os.stat(filepath)
            timestamp = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            image_record = {
                'id': f"scanned_{filename}_{int(stat.st_mtime)}",
                'filename': filename,
                'url': f"http://localhost:5001/api/images/{filename}",
                'prompt': 'Generated image',  # Default placeholder
                'negativePrompt': '',
                'timestamp': timestamp,
                'file_size': stat.st_size,
                'settings': {
                    'model_name': 'unknown',
                    'sampler_name': 'unknown',
                    'steps': 20,
                    'cfg_scale': 7.0,
                    'width': 512,
                    'height': 512,
                    'seed': -1
                }
            }
            
            # Simple heuristic: classify based on filename keywords
            if any(keyword in filename.lower() for keyword in ['img2img', 'controlnet']):
                img2img_images.append(image_record)
            elif any(keyword in filename.lower() for keyword in ['upscaled', 'extras', 'enhanced']):
                extras_images.append(image_record)
            else:
                txt2img_images.append(image_record)
        
        return {'txt2img': txt2img_images, 'img2img': img2img_images, 'extras': extras_images}
    
    def create_csv_records(self, gallery_data: Dict[str, List[Dict[str, Any]]]) -> List[ImageRecord]:
        """Convert gallery data to structured CSV records"""
        records = []
        
        for generation_type, images in gallery_data.items():
            for batch_index, image in enumerate(images):
                settings = image.get('settings', {})
                
                # Extract LoRA information if available
                lora_info = None
                if settings.get('lora'):
                    lora_info = json.dumps(settings['lora'])
                
                # Extract ControlNet information if available  
                controlnet_info = None
                if settings.get('controlnet'):
                    controlnet_info = json.dumps(settings['controlnet'])
                
                # Extract filename from URL if 'filename' is not provided
                if 'filename' in image:
                    filename = image['filename']
                elif 'url' in image:
                    # Extract filename from URL like "http://localhost:5001/api/images/DreamLayer_00029_.png"
                    filename = image['url'].split('/')[-1]
                else:
                    filename = f"image_{batch_index}.png"
                
                record = ImageRecord(
                    id=image.get('id', f"{generation_type}_{batch_index}"),
                    filename=filename,
                    relative_path=f"grids/{generation_type}/{filename}",
                    prompt=image.get('prompt', ''),
                    negative_prompt=image.get('negativePrompt', ''),
                    model_name=settings.get('model_name', 'unknown'),
                    sampler_name=settings.get('sampler_name', 'unknown'),
                    steps=int(settings.get('steps', 20)),
                    cfg_scale=float(settings.get('cfg_scale', 7.0)),
                    width=int(settings.get('width', 512)),
                    height=int(settings.get('height', 512)),
                    seed=int(settings.get('seed', -1)),
                    timestamp=image.get('timestamp', datetime.now().isoformat()),
                    generation_type=generation_type,
                    batch_index=batch_index,
                    denoising_strength=settings.get('denoising_strength'),
                    input_image_path=f"grids/input_images/{filename}" if settings.get('input_image') else None,
                    lora_models=lora_info,
                    controlnet_info=controlnet_info,
                    file_size_bytes=image.get('file_size')
                )
                records.append(record)
        
        return records
    
    def write_csv(self, records: List[ImageRecord], csv_path: str) -> None:
        """Write records to CSV file with proper schema"""
        if not records:
            # Create empty CSV with headers
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=ImageRecord.get_required_columns())
                writer.writeheader()
            return
        
        # Convert records to dictionaries
        data = [asdict(record) for record in records]
        
        # Write CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
    
    def generate_config_json(self) -> Dict[str, Any]:
        """Generate comprehensive configuration JSON"""
        settings = get_settings()
        
        # Get ComfyUI model information
        models_info = self._get_models_info()
        
        config = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'dreamlayer_version': '1.0.0',
                'report_format_version': '1.0'
            },
            'system_settings': settings,
            'available_models': models_info,
            'directory_structure': {
                'output_directory': self.output_dir,
                'served_images_directory': self.served_images_dir,
                'reports_directory': self.reports_dir
            }
        }
        
        return config
    
    def _get_models_info(self) -> Dict[str, List[str]]:
        """Get information about available models"""
        try:
            # Try to fetch from ComfyUI API
            response = requests.get("http://127.0.0.1:8188/models/checkpoints", timeout=5)
            if response.status_code == 200:
                checkpoints = response.json()
            else:
                checkpoints = []
        except:
            checkpoints = []
        
        return {
            'checkpoints': checkpoints,
            'loras': [],  # Could extend this to fetch LoRA models
            'controlnet': []  # Could extend this to fetch ControlNet models
        }
    
    def generate_readme(self, total_images: int, generation_types: List[str]) -> str:
        """Generate README content for the report bundle"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        readme_content = f"""# DreamLayer Generation Report

Generated on: {timestamp}

## Report Contents

This report bundle contains a comprehensive snapshot of your DreamLayer image generation session.

### Files Included

- **`results.csv`**: Complete metadata for all generated images
  - Contains {total_images} image records
  - Includes prompts, settings, model information, and file paths
  - All paths are relative to this report bundle

- **`config.json`**: System configuration and available models
  - Current DreamLayer settings
  - Available models and their details
  - Directory structure information

- **`grids/`**: Organized image collections
  {chr(10).join(f'  - `{gen_type}/`: Images generated via {gen_type}' for gen_type in generation_types)}

- **`README.md`**: This documentation file

### Using This Report

1. **CSV Analysis**: Import `results.csv` into any spreadsheet application or data analysis tool
2. **Image Review**: Browse the `grids/` folders to review generated images
3. **Configuration Backup**: Use `config.json` to restore or replicate your setup
4. **Path Verification**: All paths in the CSV resolve to files within this bundle

### Schema Information

The `results.csv` file follows a standardized schema with the following required columns:
- `id`, `filename`, `relative_path`, `prompt`, `negative_prompt`
- `model_name`, `sampler_name`, `steps`, `cfg_scale`, `width`, `height`
- `seed`, `timestamp`, `generation_type`, `batch_index`

Optional columns include denoising strength, LoRA models, ControlNet information, and file sizes.

### Support

For questions about this report format or DreamLayer functionality, refer to the project documentation.
"""
        return readme_content
    
    def copy_images_to_bundle(self, records: List[ImageRecord], bundle_dir: str) -> Dict[str, List[str]]:
        """Copy images to bundle directory structure and return path validation info"""
        grids_dir = os.path.join(bundle_dir, 'grids')
        os.makedirs(grids_dir, exist_ok=True)
        
        # Create subdirectories for each generation type
        generation_types = set(record.generation_type for record in records)
        for gen_type in generation_types:
            os.makedirs(os.path.join(grids_dir, gen_type), exist_ok=True)
        
        copied_files = []
        missing_files = []
        
        for record in records:
            src_path = os.path.join(self.served_images_dir, record.filename)
            dest_path = os.path.join(bundle_dir, record.relative_path)
            
            if os.path.exists(src_path):
                try:
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    copied_files.append(record.relative_path)
                except Exception as e:
                    missing_files.append(f"{record.relative_path}: {str(e)}")
            else:
                missing_files.append(f"{record.relative_path}: Source file not found")
        
        return {
            'copied_files': copied_files,
            'missing_files': missing_files,
            'generation_types': list(generation_types)
        }
    
    def create_report_bundle(self, output_filename: str = None) -> Dict[str, Any]:
        """Create complete report bundle as ZIP file"""
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"dreamlayer_report_{timestamp}.zip"
        
        output_path = os.path.join(self.reports_dir, output_filename)
        
        # Create temporary directory for bundle assembly
        temp_dir = os.path.join(self.reports_dir, f"temp_bundle_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # 1. Fetch gallery data
            gallery_data = self.fetch_gallery_data()
            
            # 2. Create CSV records
            records = self.create_csv_records(gallery_data)
            
            # 3. Write CSV file
            csv_path = os.path.join(temp_dir, 'results.csv')
            self.write_csv(records, csv_path)
            
            # 4. Validate CSV schema
            csv_validation = ImageRecord.validate_csv_schema(csv_path)
            
            # 5. Generate configuration JSON
            config = self.generate_config_json()
            config_path = os.path.join(temp_dir, 'config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 6. Copy images to bundle structure
            copy_info = self.copy_images_to_bundle(records, temp_dir)
            
            # 7. Generate README
            readme_content = self.generate_readme(
                len(records), 
                copy_info['generation_types']
            )
            readme_path = os.path.join(temp_dir, 'README.md')
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # 8. Create ZIP bundle
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            # 9. Validate all paths in CSV resolve to files in ZIP
            path_validation = self._validate_csv_paths_in_zip(csv_path, output_path)
            
            result = {
                'status': 'success',
                'report_path': output_path,
                'report_filename': output_filename,
                'total_images': len(records),
                'csv_validation': csv_validation,
                'path_validation': path_validation,
                'copied_files': len(copy_info['copied_files']),
                'missing_files': copy_info['missing_files'],
                'generation_types': copy_info['generation_types'],
                'bundle_size_bytes': os.path.getsize(output_path) if os.path.exists(output_path) else 0
            }
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'report_path': None
            }
        finally:
            # Clean up temporary directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def _validate_csv_paths_in_zip(self, csv_path: str, zip_path: str) -> Dict[str, Any]:
        """Validate that all paths in CSV resolve to files present in the ZIP"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zip_files = set(zipf.namelist())
            
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                csv_paths = [row.get('relative_path', '') for row in reader if row.get('relative_path')]
            
            missing_paths = [path for path in csv_paths if path not in zip_files]
            valid_paths = [path for path in csv_paths if path in zip_files]
            
            return {
                'valid': len(missing_paths) == 0,
                'total_csv_paths': len(csv_paths),
                'valid_paths': len(valid_paths),
                'missing_paths': missing_paths,
                'validation_passed': len(missing_paths) == 0
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
