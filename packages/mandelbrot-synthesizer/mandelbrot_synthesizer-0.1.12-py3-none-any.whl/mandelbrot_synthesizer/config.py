from pathlib import Path
import os

PACKAGE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
LIBRARY_DIR = PACKAGE_DIR / "Library"
os.makedirs(LIBRARY_DIR, exist_ok=True)
