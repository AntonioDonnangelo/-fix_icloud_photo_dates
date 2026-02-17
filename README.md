# fix_icloud_photo_dates

Restore the original creation and modification dates of photos exported from **iCloud Photos** on Windows, using the CSV metadata files generated during export.

When you download your photos through the [iCloud privacy](https://privacy.apple.com/), Apple provides a ZIP archive that includes the image files and one or more .csv files containing the original metadata (creation date, GPS coordinates, etc.).
However, the exported photos inherit the download timestamp at the filesystem level, which overwrites the original capture date. This can disrupt chronological sorting and media library organization.

This script parses the accompanying CSV metadata files and restores the correct creation timestamps to each corresponding photo file, ensuring the filesystem dates accurately reflect the original capture time.

---

## Features

- Works on **Windows, macOS, and Linux**
- Supports **any file format** present in the folder (HEIC, JPG, PNG, MOV, MP4, …)
- `--dry-run` mode to preview changes before applying them
- Clear per-file logging with a final summary (`updated / errors`)
- Handles duplicate metadata entries gracefully

---

## Requirements

- Python 3.7+
- [pandas](https://pandas.pydata.org/)
- [filedate](https://github.com/kubinka0505/filedate)

Install dependencies with:

```bash
pip install pandas filedate
```

---

## Usage

```bash
python fix_photo_dates.py --folder "/path/to/your/photos"
```

### Preview changes without modifying any file

```bash
python fix_photo_dates.py --folder "/path/to/your/photos" --dry-run
```

### Windows example

```bash
python fix_photo_dates.py --folder "C:\Users\YourName\Pictures\iCloud Photos\Photos"
```

---

## Expected folder structure

The script expects the target folder to contain both the media files **and** the CSV metadata files exported by iCloud for Windows, all in the same directory:

```
Photos/
├── IMG_0001.HEIC
├── IMG_0002.JPG
├── IMG_0003.MOV
├── iCloud Photos Part 1.csv
├── iCloud Photos Part 2.csv
└── ...
```

The CSV files must have at least the following columns:

| Column | Description |
|---|---|
| `imgName` | Filename of the media file (e.g. `IMG_0001.HEIC`) |
| `originalCreationDate` | Date string in the format `Monday January 01,2023 10:30 AM GMT` |

---

## How it works

1. All `.csv` files in the folder are loaded and merged into a single metadata table.
2. For each media file found in the folder, the script looks up its original creation date in the table.
3. The filesystem `created` and `modified` timestamps are updated to match the original date.

---

## Notes

- On **Windows**, modifying the `created` timestamp requires the script to be run with sufficient permissions. If dates are not updating, try running the terminal as Administrator.
- On **macOS/Linux**, only the `modified` date can be reliably set via `filedate`; the `created` date behavior depends on the filesystem.
- If a file appears multiple times in the CSV, the first occurrence is used.
