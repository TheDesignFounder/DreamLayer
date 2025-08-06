def test_csv_schema():
    """
    Validate that results.csv contains all expected columns:
    both required and optional metadata fields.
    """
    expected_columns = {
        "image_path", "sampler", "steps", "cfg", "preset", "seed",
        "width", "height", "grid_label", "notes"
    }

    with open("results.csv", newline='') as f:
        reader = csv.DictReader(f)
        header = set(reader.fieldnames)

        assert expected_columns.issubset(header), f"Missing: {expected_columns - header}"
