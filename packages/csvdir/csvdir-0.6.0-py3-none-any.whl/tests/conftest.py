import sys
from pathlib import Path
import pytest
import csv

# Ensure we can import csvdir from project root when running tests directly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

@pytest.fixture
def write_csv(tmp_path):
    """Helper to write a CSV with header and rows. Returns path to file."""
    def _write(name, header, rows, *, delimiter=",", encoding="utf-8", newline=""):
        p = tmp_path / name
        with p.open("w", encoding=encoding, newline=newline) as f:
            w = csv.writer(f, delimiter=delimiter)
            w.writerow(header)
            for r in rows:
                w.writerow(r)
        return p
    return _write
