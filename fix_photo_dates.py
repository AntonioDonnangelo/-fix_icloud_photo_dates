"""
fix_photo_dates.py
==================
Restores original creation/modification dates of photos exported from iCloud
using the metadata CSV files generated during export.

Requirements:
    pip install pandas filedate

Usage:
    python fix_photo_dates.py --folder /path/to/your/photos
    python fix_photo_dates.py --folder /path/to/your/photos --dry-run
"""

import os
import argparse
import pandas as pd

try:
    import filedate
except ImportError:
    raise ImportError("Missing dependency: install it with pip install filedate")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DATE_FORMAT = "%A %B %d,%Y %I:%M %p GMT"   # format used in iCloud CSV exports
OUTPUT_FORMAT = "%d.%m.%Y %H:%M"


def load_metadata(folder: str) -> pd.DataFrame:
    """Load and merge all CSV metadata files found in *folder*."""
    frames = []
    for file in os.listdir(folder):
        if file.lower().endswith(".csv"):
            path = os.path.join(folder, file)
            frames.append(pd.read_csv(path))

    if not frames:
        raise FileNotFoundError(f"No CSV metadata files found in: {folder}")

    df = pd.concat(frames, ignore_index=True)
    print(f"[INFO] Loaded metadata for {len(df)} records from {len(frames)} CSV file(s).")
    return df


def get_non_csv_extensions(folder: str) -> set:
    """Return the set of file extensions (lowercase, no dot) excluding 'csv'."""
    extensions = set()
    for file in os.listdir(folder):
        _, ext = os.path.splitext(file)
        if ext:
            extensions.add(ext.lstrip(".").lower())
    extensions.discard("csv")
    return extensions


def list_media_files(folder: str, extensions: set) -> list:
    """Return the list of media files matching the given extensions."""
    media = [
        f for f in os.listdir(folder)
        if os.path.splitext(f)[1].lstrip(".").lower() in extensions
    ]
    print(f"[INFO] Found {len(media)} media file(s) with extensions: {extensions}")
    return media


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def fix_dates(folder: str, df: pd.DataFrame, dry_run: bool = False) -> None:
    """
    For every file in *folder*, look up its original creation date in *df*
    and update the filesystem timestamps accordingly.

    Parameters
    ----------
    folder  : path to the directory containing the photos
    df      : DataFrame with at least columns 'imgName' and 'originalCreationDate'
    dry_run : if True, print what would be done without actually changing anything
    """
    success = 0
    errors = 0

    for filename in os.listdir(folder):
        # Skip CSV files themselves
        if filename.lower().endswith(".csv"):
            continue

        file_path = os.path.join(folder, filename)

        try:
            # Keep only the first occurrence if the image appears multiple times
            match = df[df["imgName"] == filename]["originalCreationDate"]
            if match.empty:
                print(f"[SKIP]  No metadata found for: {filename}")
                continue

            raw_date = match.iloc[0]
            original_dt = pd.to_datetime(raw_date, format=DATE_FORMAT)
            date_str = original_dt.strftime(OUTPUT_FORMAT)

            if dry_run:
                print(f"[DRY-RUN] Would set {filename} → {date_str}")
            else:
                print(f"[OK]    Setting {filename} → {date_str}")
                f = filedate.File(file_path)
                f.created  = date_str
                f.modified = date_str

            success += 1

        except Exception as exc:
            print(f"[ERROR] {filename}: {exc}")
            errors += 1

    print(f"\n--- Done: {success} updated, {errors} errors ---")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Restore iCloud photo timestamps from exported CSV metadata."
    )
    parser.add_argument(
        "--folder",
        required=True,
        help="Path to the folder containing photos and CSV metadata files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying any file.",
    )
    args = parser.parse_args()

    folder = args.folder

    if not os.path.isdir(folder):
        raise NotADirectoryError(f"Folder not found: {folder}")

    df = load_metadata(folder)
    extensions = get_non_csv_extensions(folder)
    list_media_files(folder, extensions)   # just for informational output
    fix_dates(folder, df, dry_run=args.dry_run)


if __name__ == "__main__":
    main()