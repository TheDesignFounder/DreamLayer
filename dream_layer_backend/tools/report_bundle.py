"""
Report Bundle Module for DreamLayer AI

Creates deterministic report bundles containing generation results, configuration,
and generated images for reproducibility and sharing.
"""

import csv
import hashlib
import json
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .report_schema import validate_results_csv, create_schema_header, SCHEMA_VERSION


def build_report_bundle(
    run_dir: Path, 
    out_zip: Path, 
    selected_globs: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Build a deterministic report bundle from a run directory.
    
    Args:
        run_dir: Directory containing the run results
        out_zip: Output ZIP file path
        selected_globs: Optional list of glob patterns for grid images
        
    Returns:
        Dictionary with bundle information including file list and SHA256 hash
        
    Raises:
        ValueError: If required files are missing or validation fails
        FileNotFoundError: If run directory doesn't exist
    """
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")
    
    # Default globs for grid images if none specified
    if selected_globs is None:
        selected_globs = ["grids/*.png", "grids/*.jpg", "grids/*.jpeg"]
    
    # Required files
    results_csv = run_dir / "results.csv"
    config_json = run_dir / "config.json"
    
    if not results_csv.exists():
        raise ValueError(f"Required file not found: {results_csv}")
    if not config_json.exists():
        raise ValueError(f"Required file not found: {config_json}")
    
    # Validate results.csv schema
    validate_results_csv(results_csv)
    
    # Create temporary directory for bundle preparation
    temp_dir = Path(f"temp_bundle_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Copy and process required files
        bundle_files = []
        
        # 1. Copy config.json
        shutil.copy2(config_json, temp_dir / "config.json")
        bundle_files.append("config.json")
        
        # 2. Process results.csv - rewrite image paths and add schema version
        processed_csv_path = temp_dir / "results.csv"
        _process_results_csv(results_csv, processed_csv_path, run_dir)
        bundle_files.append("results.csv")
        
        # 3. Copy grid images based on glob patterns
        grid_files = _collect_grid_images(run_dir, selected_globs, temp_dir)
        bundle_files.extend(grid_files)
        
        # 4. Create README.txt
        readme_path = temp_dir / "README.txt"
        _create_readme(readme_path, run_dir, config_json)
        bundle_files.append("README.txt")
        
        # 5. Create deterministic ZIP
        _create_deterministic_zip(temp_dir, out_zip, bundle_files)
        
        # 6. Calculate SHA256 hash
        sha256_hash = _calculate_file_hash(out_zip)
        
        return {
            "files": sorted(bundle_files),
            "sha256": sha256_hash,
            "bundle_size": out_zip.stat().st_size,
            "created_at": datetime.now().isoformat()
        }
        
    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def _process_results_csv(
    source_csv: Path, 
    target_csv: Path, 
    run_dir: Path
) -> None:
    """
    Process results.csv to rewrite image paths and add schema version.
    
    Args:
        source_csv: Source CSV file path
        target_csv: Target CSV file path
        run_dir: Run directory for path resolution
    """
    with open(source_csv, 'r', newline='', encoding='utf-8') as infile, \
         open(target_csv, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames or []
        
        # Add schema_version if not present
        if "schema_version" not in fieldnames:
            fieldnames = ["schema_version"] + fieldnames
        
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            # Add schema version
            if "schema_version" not in row:
                row["schema_version"] = SCHEMA_VERSION
            
            # Rewrite image paths to be relative to bundle root
            if "image_path" in row and row["image_path"]:
                original_path = Path(row["image_path"])
                if original_path.is_absolute():
                    # Convert absolute path to relative within run directory
                    try:
                        relative_path = original_path.relative_to(run_dir)
                        row["image_path"] = str(relative_path)
                    except ValueError:
                        # Path is outside run directory, keep as is
                        pass
                else:
                    # Already relative, ensure it's relative to run directory
                    if not (run_dir / original_path).exists():
                        # Try to find the image in common subdirectories
                        for subdir in ["output", "images", "grids"]:
                            potential_path = run_dir / subdir / original_path.name
                            if potential_path.exists():
                                row["image_path"] = f"{subdir}/{original_path.name}"
                                break
            
            writer.writerow(row)


def _collect_grid_images(
    run_dir: Path, 
    glob_patterns: List[str], 
    temp_dir: Path
) -> List[str]:
    """
    Collect grid images based on glob patterns.
    
    Args:
        run_dir: Run directory to search in
        glob_patterns: List of glob patterns
        temp_dir: Temporary directory to copy images to
        
    Returns:
        List of copied image filenames
    """
    grid_files = []
    images_dir = temp_dir / "images"
    images_dir.mkdir(exist_ok=True)
    
    for pattern in glob_patterns:
        try:
            for file_path in run_dir.glob(pattern):
                if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    # Copy to images subdirectory
                    target_path = images_dir / file_path.name
                    shutil.copy2(file_path, target_path)
                    grid_files.append(f"images/{file_path.name}")
        except Exception as e:
            print(f"Warning: Failed to process glob pattern '{pattern}': {e}")
    
    return sorted(grid_files)


def _create_readme(
    readme_path: Path, 
    run_dir: Path, 
    config_json: Path
) -> None:
    """
    Create README.txt with run information and instructions.
    
    Args:
        readme_path: Path to create README.txt
        run_dir: Run directory
        config_json: Config file path
    """
    # Load config for metadata
    config_data = {}
    try:
        with open(config_json, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except Exception:
        pass
    
    # Extract run information
    run_id = config_data.get('run_id', 'unknown')
    preset_name = config_data.get('preset_name', 'default')
    model_name = config_data.get('model_name', 'unknown')
    
    readme_content = f"""DreamLayer AI - Generation Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Run ID: {run_id}
Preset: {preset_name}
Model: {model_name}

This report contains:
- config.json: Complete generation configuration
- results.csv: Generation results with metadata
- images/: Generated grid images
- README.txt: This file

To reproduce these results:
1. Load the config.json file in DreamLayer AI
2. Ensure the same model and settings are available
3. Run the generation with the same seed values

For questions or issues, please refer to the DreamLayer AI documentation.
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)


def _create_deterministic_zip(
    source_dir: Path, 
    zip_path: Path, 
    file_list: List[str]
) -> None:
    """
    Create a deterministic ZIP file with sorted entries and fixed permissions.
    
    Args:
        source_dir: Source directory
        zip_path: Output ZIP path
        file_list: List of files to include (sorted)
    """
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add files in sorted order for determinism
        for filename in sorted(file_list):
            file_path = source_dir / filename
            if file_path.exists():
                # Use fixed permissions and timestamp for determinism
                zipf.write(
                    file_path, 
                    filename,
                    compress_type=zipfile.ZIP_DEFLATED
                )
                
                # Set fixed timestamp and permissions for deterministic SHA256
                info = zipf.getinfo(filename)
                info.date_time = (1980, 1, 1, 0, 0, 0)  # Fixed date for determinism
                info.external_attr = 0o644 << 16  # Fixed permissions


def _calculate_file_hash(file_path: Path) -> str:
    """
    Calculate SHA256 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        SHA256 hash string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def validate_bundle(zip_path: Path) -> Dict[str, Any]:
    """
    Validate a report bundle ZIP file.
    
    Args:
        zip_path: Path to the ZIP file
        
    Returns:
        Dictionary with validation results
    """
    if not zip_path.exists():
        return {"valid": False, "error": "ZIP file not found"}
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            file_list = sorted(zipf.namelist())
            
            # Check required files
            required_files = ["config.json", "results.csv", "README.txt"]
            missing_files = [f for f in required_files if f not in file_list]
            
            if missing_files:
                return {
                    "valid": False,
                    "error": f"Missing required files: {missing_files}",
                    "file_list": file_list
                }
            
            # Validate results.csv schema
            try:
                with zipf.open("results.csv") as csv_file:
                    # Create temporary file for validation
                    temp_csv = Path("temp_validation.csv")
                    with open(temp_csv, 'wb') as f:
                        f.write(csv_file.read())
                    
                    try:
                        validate_results_csv(temp_csv)
                        csv_valid = True
                    except Exception as e:
                        csv_valid = False
                        csv_error = str(e)
                    finally:
                        temp_csv.unlink(missing_ok=True)
            except Exception as e:
                csv_valid = False
                csv_error = str(e)
            
            return {
                "valid": len(missing_files) == 0 and csv_valid,
                "file_list": file_list,
                "total_files": len(file_list),
                "csv_valid": csv_valid,
                "csv_error": csv_error if not csv_valid else None,
                "bundle_size": zip_path.stat().st_size
            }
            
    except Exception as e:
        return {
            "valid": False,
            "error": f"ZIP validation failed: {str(e)}"
        }
