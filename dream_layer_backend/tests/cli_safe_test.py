import subprocess
import sys

def test_safe_flag_sets_config():
    result = subprocess.run(
        [sys.executable, "cli.py", "--safe"],
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()
    assert "batch_size=1" in output
    assert "precision=fp16" in output
