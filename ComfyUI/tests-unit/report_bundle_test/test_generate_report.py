import zipfile
import csv
from pathlib import Path

def test_report_zip():
    base_dir = Path(__file__).resolve().parent.parent / "utils"
    report_zip_path = base_dir / "report" / "report.zip"

    assert report_zip_path.exists(), "report.zip was not created."

    with zipfile.ZipFile(report_zip_path, 'r') as zipf:
        names = zipf.namelist()

        # Check required files
        assert "config.json" in names, "Missing config.json in ZIP"
        assert "results.csv" in names, "Missing results.csv in ZIP"
        assert "README.txt" in names, "Missing README.txt in ZIP"

        # Check image references in CSV exist in ZIP
        with zipf.open("results.csv") as csvfile:
            reader = csv.DictReader(line.decode('utf-8') for line in csvfile)
            for row in reader:
                image_name = f"grids/{row['image_file']}"
                assert image_name in names, f"Missing image file {image_name} in ZIP"

    print("✅ All report.zip checks passed.")

if __name__ == "__main__":
    test_report_zip()