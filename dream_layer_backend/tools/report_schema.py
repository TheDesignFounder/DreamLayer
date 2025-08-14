"""
Report Schema Validation Module for DreamLayer AI

Defines the schema for results.csv files and provides validation functions.
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


# Required columns for results.csv (core columns)
CORE_COLUMNS = [
    "run_id", "image_path", "seed", "sampler", "steps", "cfg", 
    "preset_name", "preset_hash"
]

# Optional metric columns
METRIC_COLUMNS = ["ssim", "clip_score", "lpips"]

# Schema version for backward compatibility
SCHEMA_VERSION = "1.0"


def validate_results_csv(csv_path: Path, bundle_root: Optional[Path] = None, config_data: Optional[Dict[str, Any]] = None) -> None:
    """
    Validate a results.csv file against the required schema.
    
    Args:
        csv_path: Path to the results.csv file
        bundle_root: Optional root directory for validating image paths
        config_data: Optional config data to check which metrics are enabled
        
    Raises:
        ValueError: If validation fails
    """
    if not csv_path.exists():
        raise ValueError(f"Results CSV file not found: {csv_path}")
    
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Check if required columns are present
        fieldnames = reader.fieldnames or []
        
        # Determine which metric columns are required based on config
        required_columns = CORE_COLUMNS.copy()
        if config_data and "metrics_meta" in config_data:
            metrics_meta = config_data["metrics_meta"]
            if metrics_meta.get("ssim_enabled", False):
                required_columns.append("ssim")
            if metrics_meta.get("clip_enabled", False):
                required_columns.append("clip_score")
            if metrics_meta.get("lpips_enabled", False):
                required_columns.append("lpips")
        else:
            # If no config or metrics_meta, all metric columns are optional
            # This maintains backward compatibility
            pass
        
        missing_columns = [col for col in required_columns if col not in fieldnames]
        
        if missing_columns:
            # Check if this is an older schema version
            if "schema_version" in fieldnames:
                # Allow missing metric columns for older schemas
                missing_metric_columns = [col for col in missing_columns if col in METRIC_COLUMNS]
                if len(missing_metric_columns) == len(missing_columns):
                    # Only metric columns are missing, which is acceptable for older schemas
                    pass
                else:
                    raise ValueError(f"Missing required columns: {missing_columns}")
            else:
                raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Validate image paths if bundle_root is provided
        if bundle_root:
            for row_num, row in enumerate(reader, start=2):  # Start at 2 for header row
                image_path = row.get('image_path', '')
                if image_path:
                    # Convert relative path to absolute within bundle
                    full_image_path = bundle_root / image_path
                    if not full_image_path.exists():
                        raise ValueError(
                            f"Image path not found in row {row_num}: {image_path} "
                            f"(resolved to: {full_image_path})"
                        )


def get_schema_version(csv_path: Path) -> str:
    """
    Get the schema version from a results.csv file.
    
    Args:
        csv_path: Path to the results.csv file
        
    Returns:
        Schema version string
    """
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            
            if "schema_version" in fieldnames:
                # Read first row to get schema version
                f.seek(0)
                next(f)  # Skip header
                first_row = next(csv.DictReader(f))
                return first_row.get('schema_version', "1.0")
            else:
                return "1.0"  # Default for older files
    except Exception:
        return "1.0"  # Default on error


def create_schema_header() -> List[str]:
    """
    Create a schema header row for results.csv.
    
    Returns:
        List of column names including schema_version
    """
    return ["schema_version"] + CORE_COLUMNS + METRIC_COLUMNS


def validate_csv_structure(csv_path: Path) -> Dict[str, Any]:
    """
    Validate the structure of a results.csv file.
    
    Args:
        csv_path: Path to the results.csv file
        
    Returns:
        Dictionary with validation results
    """
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            
            # Count rows
            rows = list(reader)
            row_count = len(rows)
            
            # Check for schema version
            has_schema_version = "schema_version" in fieldnames
            
            # Check core columns
            missing_core = [col for col in CORE_COLUMNS if col not in fieldnames]
            core_valid = len(missing_core) == 0
            
            # Check metric columns
            missing_metrics = [col for col in METRIC_COLUMNS if col not in fieldnames]
            metrics_valid = len(missing_metrics) == 0
            
            # Check if all required columns are present
            all_required = CORE_COLUMNS + METRIC_COLUMNS
            missing_required = [col for col in all_required if col not in fieldnames]
            
            return {
                "valid": core_valid and (has_schema_version or metrics_valid),
                "row_count": row_count,
                "has_schema_version": has_schema_version,
                "core_columns_valid": core_valid,
                "metric_columns_valid": metrics_valid,
                "missing_core_columns": missing_core,
                "missing_metric_columns": missing_metrics,
                "missing_required_columns": missing_required,
                "fieldnames": fieldnames
            }
            
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "row_count": 0,
            "has_schema_version": False,
            "core_columns_valid": False,
            "metric_columns_valid": False,
            "missing_core_columns": CORE_COLUMNS,
            "missing_metric_columns": METRIC_COLUMNS,
            "missing_required_columns": CORE_COLUMNS + METRIC_COLUMNS,
            "fieldnames": []
        }
