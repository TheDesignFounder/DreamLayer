import os
import csv
import json
import zipfile
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "sample_data"
REPORT_DIR = BASE_DIR / "report"
REPORT_ZIP = REPORT_DIR / "report.zip"
README_CONTENT = """# DreamLayer Inference Report

This bundle contains:
- Inference results (results.csv)
- Configuration used (config.json)
- Grid images with seeds and parameters
"""

def create_report():
    REPORT_DIR.mkdir(exist_ok=True)

    with zipfile.ZipFile(REPORT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add config.json
        config_path = DATA_DIR / "config.json"
        if config_path.exists():
            zipf.write(config_path, arcname="config.json")

        # Add results.csv and referenced images
        results_path = DATA_DIR / "results.csv"
        if results_path.exists():
            zipf.write(results_path, arcname="results.csv")
            with open(results_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    image_file = DATA_DIR / row["image_file"]
                    if image_file.exists():
                        zipf.write(image_file, arcname=f"grids/{image_file.name}")

        # Add readme
        readme_path = REPORT_DIR / "README.txt"
        with open(readme_path, 'w') as f:
            f.write(README_CONTENT)
        zipf.write(readme_path, arcname="README.txt")

    print(f"Report generated at: {REPORT_ZIP.resolve()}")

if __name__ == "__main__":
    create_report()