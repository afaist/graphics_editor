#!/usr/bin/env python3
"""
Script to download DejaVu fonts into assets/fonts/dejavu/.
Used to prepare font bundle for PyInstaller builds.

Fonts are downloaded from GitHub releases:
https://github.com/dejavu-fonts/dejavu-fonts
"""

import sys
import urllib.request
import zipfile
from pathlib import Path


def download_dejavu_fonts(output_dir: str = "assets/fonts/dejavu"):
    """Downloads and extracts DejaVu TTF fonts."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Check if fonts already exist
    ttf_files = list(output_path.glob("*.ttf"))
    if ttf_files:
        print(f"[OK] DejaVu fonts already present in {output_dir} ({len(ttf_files)} files)")
        return

    print("[INFO] Downloading DejaVu fonts...")

    # Use GitHub release archive
    dejavu_version = "2.37"
    archive_url = (
        f"https://github.com/dejavu-fonts/dejavu-fonts/releases/"
        f"download/v{dejavu_version}/dejavu-fonts-ttf-{dejavu_version}.zip"
    )

    archive_path = Path("dejavu-fonts.zip")

    try:
        # Download archive
        print(f"[INFO] URL: {archive_url}")
        urllib.request.urlretrieve(archive_url, archive_path)

        # Extract only TTF fonts
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith(".ttf"):
                    # Extract files from the ttf/ directory
                    if "/ttf/" in file or file.count("/") <= 2:
                        zip_ref.extract(file, output_path)
                        print(f"  Extracted: {file}")

        archive_path.unlink()
        print(f"[OK] Done! {len(list(output_path.glob('*.ttf')))} files saved")

    except Exception as e:
        print(f"[ERROR] Download failed: {e}", file=sys.stderr)
        if archive_path.exists():
            archive_path.unlink()
        sys.exit(1)


if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "assets/fonts/dejavu"
    download_dejavu_fonts(output_dir)
