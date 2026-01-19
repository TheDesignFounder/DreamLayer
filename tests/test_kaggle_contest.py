#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from kaggle_contest import score

# Use path relative to this test file
SUBMISSION_ZIP = Path(__file__).resolve().parent / "submissions.zip"


def test_scoring():
    # Skip test if submission zip doesn't exist
    if not SUBMISSION_ZIP.exists():
        print(f"⚠️ Skipping test: {SUBMISSION_ZIP} not found")
        print("To run this test, place a submissions.zip file in the tests/ directory")
        return

    # Create mock solution DataFrame
    solution_df = pd.DataFrame({'id': [1]})

    print("Testing full scoring pipeline...")
    try:
        final_score = score(
            solution=solution_df,
            submission_zip_path=str(SUBMISSION_ZIP),
            row_id_column_name='id',
            labels=None,
            pos_label=1,
            average='binary',
            weights_column_name=None
        )
        print(f"✅ Final Score: {final_score}")
        print(f"Score breakdown: 0.5 × CLIPScore - 0.5 × FID_norm = {final_score}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_scoring()
