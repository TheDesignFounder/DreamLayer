"""
Batch Report Generator Utility

This module provides utilities to generate batch reports containing CSV data, 
configuration JSON, image grids, and documentation for generated images.
"""

import os
import csv
import json
import zipfile
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Constants
REQUIRED_CSV_COLUMNS = [
    'filename',
    'prompt', 
    'negative_prompt',
    'model',
    'sampler',
    'steps',
    'cfg_scale',
    'seed',
    'width',
    'height',
    'timestamp'
]

class BatchReportGenerator:
    """
    Generate batch reports containing CSV, JSON, grids, and README files.
    
    The generator creates a deterministic ZIP file structure with all necessary
    metadata and image files for batch analysis and archival.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the BatchReportGenerator.
        
        Args:
            output_dir: Directory to save the report. Defaults to served_images/reports
        """
        if output_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(current_dir)
            self.output_dir = os.path.join(backend_dir, 'served_images', 'reports')
        else:
            self.output_dir = output_dir
            
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"BatchReportGenerator initialized with output directory: {self.output_dir}")
    
    def generate_report(self, 
                       images_data: List[Dict[str, Any]], 
                       config: Dict[str, Any],
                       report_name: Optional[str] = None) -> str:
        """
        Generate a complete batch report bundle.
        
        Args:
            images_data: List of image data dictionaries containing metadata
            config: Configuration dictionary for the generation session
            report_name: Optional custom name for the report
            
        Returns:
            Path to the generated report.zip file
        """
        try:
            # Generate deterministic report name
            if report_name is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_name = f"report_{timestamp}"
            
            logger.info(f"Generating batch report: {report_name}")
            
            # Create temporary directory for report contents
            temp_dir = os.path.join(self.output_dir, f"{report_name}_temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            try:
                # Create results.csv
                csv_path = os.path.join(temp_dir, 'results.csv')
                self._create_csv(csv_path, images_data)
                logger.info(f"Created CSV file with {len(images_data)} entries")
                
                # Create config.json
                config_path = os.path.join(temp_dir, 'config.json')
                self._create_config_json(config_path, config)
                logger.info("Created config.json")
                
                # Copy selected grids/images
                grids_dir = os.path.join(temp_dir, 'grids')
                os.makedirs(grids_dir, exist_ok=True)
                copied_count = self._copy_images(images_data, grids_dir)
                logger.info(f"Copied {copied_count} images to grids directory")
                
                # Create README
                readme_path = os.path.join(temp_dir, 'README.txt')
                self._create_readme(readme_path, images_data, config)
                logger.info("Created README.txt")
                
                # Create the zip file
                zip_path = os.path.join(self.output_dir, f"{report_name}.zip")
                self._create_zip(temp_dir, zip_path)
                logger.info(f"Created ZIP file: {zip_path}")
                
                return zip_path
                
            finally:
                # Clean up temporary directory
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    logger.info("Cleaned up temporary directory")
                    
        except Exception as e:
            logger.error(f"Error generating batch report: {str(e)}")
            raise
    
    def _create_csv(self, csv_path: str, images_data: List[Dict[str, Any]]) -> None:
        """
        Create results.csv with image metadata.
        
        Args:
            csv_path: Path where the CSV file will be created
            images_data: List of image data dictionaries
        """
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = REQUIRED_CSV_COLUMNS + ['grid_path']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for idx, image_data in enumerate(images_data):
                    # Extract settings from nested structure
                    settings = image_data.get('settings', {})
                    
                    # Determine grid filename with deterministic naming
                    original_filename = image_data.get('filename', f'image_{idx}.png')
                    grid_filename = f"grid_{idx:04d}_{Path(original_filename).stem}.png"
                    
                    row = {
                        'filename': original_filename,
                        'prompt': image_data.get('prompt', ''),
                        'negative_prompt': image_data.get('negativePrompt', ''),
                        'model': settings.get('model', 'unknown'),
                        'sampler': settings.get('sampler', 'unknown'),
                        'steps': settings.get('steps', 20),
                        'cfg_scale': settings.get('cfg_scale', 7.0),
                        'seed': settings.get('seed', -1),
                        'width': settings.get('width', 512),
                        'height': settings.get('height', 512),
                        'timestamp': image_data.get('timestamp', datetime.now().isoformat()),
                        'grid_path': f"grids/{grid_filename}"
                    }
                    writer.writerow(row)
                    
        except Exception as e:
            logger.error(f"Error creating CSV file: {str(e)}")
            raise
    
    def _create_config_json(self, config_path: str, config: Dict[str, Any]) -> None:
        """
        Create config.json with generation configuration.
        
        Args:
            config_path: Path where the JSON file will be created
            config: Configuration dictionary
        """
        try:
            # Add metadata to config
            config_with_metadata = {
                'generation_config': config,
                'report_metadata': {
                    'created_at': datetime.now().isoformat(),
                    'version': '1.0',
                    'generator': 'DreamLayer Batch Report Generator'
                }
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_with_metadata, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error creating config.json: {str(e)}")
            raise
    
    def _copy_images(self, images_data: List[Dict[str, Any]], grids_dir: str) -> int:
        """
        Copy image files to the grids directory with deterministic names.
        
        Args:
            images_data: List of image data dictionaries
            grids_dir: Destination directory for images
            
        Returns:
            Number of successfully copied images
        """
        # Get the served images directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)
        served_images_dir = os.path.join(backend_dir, 'served_images')
        
        copied_count = 0
        
        for idx, image_data in enumerate(images_data):
            try:
                original_filename = image_data.get('filename')
                if not original_filename:
                    logger.warning(f"Image {idx} has no filename, skipping")
                    continue
                    
                # Source path
                src_path = os.path.join(served_images_dir, original_filename)
                
                # Deterministic destination filename
                grid_filename = f"grid_{idx:04d}_{Path(original_filename).stem}.png"
                dest_path = os.path.join(grids_dir, grid_filename)
                
                # Copy file if it exists
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dest_path)
                    copied_count += 1
                else:
                    logger.warning(f"Image file not found: {src_path}")
                    
            except Exception as e:
                logger.error(f"Error copying image {idx}: {str(e)}")
                
        return copied_count
    
    def _create_readme(self, readme_path: str, images_data: List[Dict[str, Any]], config: Dict[str, Any]) -> None:
        """
        Create README.txt with report information.
        
        Args:
            readme_path: Path where the README file will be created
            images_data: List of image data dictionaries
            config: Configuration dictionary
        """
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write("DreamLayer Batch Report\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Images: {len(images_data)}\n\n")
                
                f.write("Contents:\n")
                f.write("---------\n")
                f.write("- results.csv: Detailed metadata for all generated images\n")
                f.write("- config.json: Complete generation configuration\n")
                f.write("- grids/: Directory containing all generated images\n\n")
                
                f.write("CSV Schema:\n")
                f.write("-----------\n")
                for column in REQUIRED_CSV_COLUMNS:
                    f.write(f"- {column}\n")
                f.write("- grid_path: Path to image file within this archive\n\n")
                
                f.write("Usage:\n")
                f.write("------\n")
                f.write("1. Extract this ZIP file to access all contents\n")
                f.write("2. Use results.csv for batch analysis or import\n")
                f.write("3. Reference grid_path column to locate specific images\n")
                f.write("4. config.json contains full generation parameters\n")
                
        except Exception as e:
            logger.error(f"Error creating README: {str(e)}")
            raise
    
    def _create_zip(self, source_dir: str, zip_path: str) -> None:
        """
        Create ZIP file from the temporary directory.
        
        Args:
            source_dir: Directory containing files to zip
            zip_path: Path where the ZIP file will be created
        """
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Calculate archive name to maintain directory structure
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
                        
        except Exception as e:
            logger.error(f"Error creating ZIP file: {str(e)}")
            raise
    
    def validate_csv_schema(self, csv_path: str) -> bool:
        """
        Validate that a CSV file contains all required columns.
        
        Args:
            csv_path: Path to the CSV file to validate
            
        Returns:
            True if all required columns are present
        """
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                headers = reader.fieldnames or []
                
                # Check if all required columns are present
                missing_columns = set(REQUIRED_CSV_COLUMNS) - set(headers)
                if missing_columns:
                    logger.warning(f"Missing required columns: {missing_columns}")
                    return False
                    
                return True
                
        except Exception as e:
            logger.error(f"Error validating CSV schema: {str(e)}")
            return False
    
    def validate_zip_contents(self, zip_path: str) -> bool:
        """
        Validate that all paths in the CSV resolve to files in the ZIP.
        
        Args:
            zip_path: Path to the ZIP file to validate
            
        Returns:
            True if all referenced files exist in the ZIP
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # Get list of files in ZIP
                zip_files = set(zipf.namelist())
                
                # Extract and read the CSV
                csv_content = zipf.read('results.csv').decode('utf-8')
                
                # Parse CSV from string
                from io import StringIO
                csvfile = StringIO(csv_content)
                reader = csv.DictReader(csvfile)
                
                # Check each grid_path
                missing_files = []
                for row in reader:
                    grid_path = row.get('grid_path', '')
                    if grid_path and grid_path not in zip_files:
                        missing_files.append(grid_path)
                
                if missing_files:
                    logger.warning(f"Missing files in ZIP: {missing_files}")
                    return False
                    
                return True
                
        except Exception as e:
            logger.error(f"Error validating ZIP contents: {str(e)}")
            return False