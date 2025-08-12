import shutil
import sys
import importlib.resources as pkg_resources
from pathlib import Path
import os

def main():
    try:
        # get sample.pdf from package
        with pkg_resources.path("xyz", "sample.pdf") as src_file:
            # cross-platform Downloads folder
            downloads_path = Path.home() / "Downloads"
            downloads_path.mkdir(parents=True, exist_ok=True)
            dest_file = downloads_path / "sample.pdf"

            shutil.copy(src_file, dest_file)
            print(f"Sample PDF copied to {dest_file}")

    except FileNotFoundError:
        print("Sample PDF not found in package.", file=sys.stderr)
