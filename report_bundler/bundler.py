import csv
import json
import zipfile
from pathlib import Path

# These are the columns we expect in the results.csv
REQUIRED_COLUMNS = {"image_path", "sampler", "steps", "cfg", "preset", "seed"}

def validate_csv_schema(csv_path):
    """
    Opens the CSV file and checks if it has all required columns.
    If not, throws an error so we don't bundle bad data.
    """
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        header_fields = set(reader.fieldnames)
        
        if not REQUIRED_COLUMNS.issubset(header_fields):
            missing = REQUIRED_COLUMNS - header_fields
            raise ValueError(f"Oops...Missing required columns: {missing}")
        
        return list(reader)

def collect_files(csv_rows):
    """
    From the rows in the CSV, grab all image paths that need to be bundled.
    We use a set to avoid duplicates just in case.
    """
    files = set()
    for row in csv_rows:
        files.add(row["image_path"])
    return files

def create_report_zip(output_path="report.zip"):
    """
    This function does the real work:
    - validates CSV
    - checks all files exist
    - packages everything neatly into a zip
    """
    base_dir = Path(__file__).parent
    csv_path = base_dir / "results.csv"
    config_path = base_dir / "config.json"
    readme_path = base_dir / "README.md"
    zip_path = base_dir / output_path

    # Step 1: Load and validate the CSV
    csv_rows = validate_csv_schema(csv_path)

    # Step 2: Grab image file paths from CSV
    image_paths = collect_files(csv_rows)

    # Step 3: Zip it all up!
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add metadata and config
        zipf.write(csv_path, arcname="results.csv")
        zipf.write(config_path, arcname="config.json")
        zipf.write(readme_path, arcname="README.md")

        # Add each grid image
        for path in image_paths:
            full_path = base_dir / path
            if not full_path.exists():
                raise FileNotFoundError(f"Missing image file: {full_path}")
            
            # This keeps the zip path clean and relative (like grids/image1.png)
            zipf.write(full_path, arcname=path)

    print(f"Done! Report created: {zip_path}")

# Run it as a script (not when imported)
if __name__ == "__main__":
    create_report_zip()
