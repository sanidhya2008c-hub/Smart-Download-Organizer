"""Automatically sort new browser downloads into semester course folders.

Examples (assuming S:\\Year 2\\Sem 3 exists):
    notes_gis.pdf       -> S:\\Year 2\\Sem 3\\Introduction to Geographical Information Systems\\PDF\\notes_gis.pdf
    survey_gis.xlsx     -> S:\\Year 2\\Sem 3\\Introduction to Geographical Information Systems\\Excel\\survey_gis.xlsx
    essay_writing.docx  -> S:\\Year 2\\Sem 3\\Technical and Scientific Writing\\Word\\essay_writing.docx

Unknown/new labels are placed in a new or existing folder on the Desktop:
    notes_climate.pdf -> Desktop\\Climate\\PDF\\notes_climate.pdf

Only files that arrive or change after this script starts are processed.
Uses only the Python standard library. Designed for Windows 10/11.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import time
from pathlib import Path
from typing import Dict, Tuple

# Usually correct on Windows. Change this if your browser saves downloads elsewhere.
DOWNLOADS_DIR = Path.home() / "Downloads"

# The existing subject/course folders shown in your screenshot.
SEMESTER_ROOT = Path(r"S:\Year 2\Sem 3")

# Use the actual Windows Desktop location, including when it is redirected to OneDrive.
def get_desktop_dir() -> Path:
    if os.name == "nt":
        try:
            import winreg  # Windows standard library

            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                desktop_value, _ = winreg.QueryValueEx(key, "Desktop")
            return Path(os.path.expandvars(desktop_value))
        except (OSError, ImportError):
            pass
    return Path.home() / "Desktop"


DESKTOP_ROOT = get_desktop_dir()

# Edit/add aliases here. Each key is a filename tag, and each value is the exact
# existing course folder name shown in File Explorer.
COURSE_FOLDER_BY_TAG = {
    # Critical thinking and Philosophy
    "ctp": "Critical thinking and Philosophy",
    "critical": "Critical thinking and Philosophy",
    "philosophy": "Critical thinking and Philosophy",
    "criticalthinking": "Critical thinking and Philosophy",

    # Foundations of Social Research
    "fsr": "Foundations of Social Research",
    "research": "Foundations of Social Research",
    "socialresearch": "Foundations of Social Research",
    "foundations": "Foundations of Social Research",

    # Introduction to Geographical Information Systems
    "gis": "Introduction to Geographical Information Systems",
    "qgis": "Introduction to Geographical Information Systems",
    "geography": "Introduction to Geographical Information Systems",
    "geographicalinformation": "Introduction to Geographical Information Systems",

    # Introduction to MATLAB
    "matlab": "Introduction to MATLAB",

    # Introduction to R programming
    "r": "Introduction to R programming",
    "rprogramming": "Introduction to R programming",

    # Micro and Macro Databases (STEM)
    "db": "Micro and Macro Databases (STEM)",
    "database": "Micro and Macro Databases (STEM)",
    "databases": "Micro and Macro Databases (STEM)",

    # Natural and Man-made Disasters
    "nmd": "Natural and Man-made Disasters",
    "disaster": "Natural and Man-made Disasters",
    "disasters": "Natural and Man-made Disasters",
    "naturaldisasters": "Natural and Man-made Disasters",

    # Sustainable Development Analytics (STEM)
    "sdg": "Sustainable Development Analytics (STEM)",
    "sda": "Sustainable Development Analytics (STEM)",
    "sustainability": "Sustainable Development Analytics (STEM)",
    "sustainabledevelopmentanalytics": "Sustainable Development Analytics (STEM)",

    # Technical and Scientific Writing
    "tsw": "Technical and Scientific Writing",
    "writing": "Technical and Scientific Writing",
    "scientificwriting": "Technical and Scientific Writing",
}

# Scan every 2 seconds and wait for 3 unchanged checks before moving a file.
POLL_SECONDS = 2
STABLE_CHECKS = 3

# Temporary extensions used while browsers are still downloading.
TEMP_EXTENSIONS = {".crdownload", ".part", ".download", ".tmp"}

# File-type subfolders. CSV files are grouped with Excel/spreadsheet files by default.
EXTENSION_FOLDERS = {
    ".pdf": "PDF",
    ".xls": "Excel",
    ".xlsx": "Excel",
    ".xlsm": "Excel",
    ".xlsb": "Excel",
    ".ods": "Excel",
    ".csv": "Excel",
    ".tsv": "Excel",
    ".doc": "Word",
    ".docx": "Word",
    ".odt": "Word",
    ".ppt": "PowerPoint",
    ".pptx": "PowerPoint",
    ".odp": "PowerPoint",
    ".txt": "Text",
    ".md": "Text",
    ".rtf": "Text",
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".webp": "Images",
    ".svg": "Images",
    ".zip": "Archives",
    ".7z": "Archives",
    ".rar": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
}

# Common abbreviations should look natural as new Desktop folder names.
KNOWN_LABELS = {
    "gis": "GIS", "qgis": "QGIS", "ai": "AI", "ml": "ML", "sql": "SQL",
    "spss": "SPSS", "sdg": "SDG", "tiss": "TISS", "api": "API",
    "db": "Databases", "nmd": "Disasters", "fsr": "Social Research",
    "ctp": "Critical Thinking", "tsw": "Scientific Writing",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

FileSignature = Tuple[int, int]  # (file size, modified time in nanoseconds)


def signature(path: Path) -> FileSignature:
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns


def is_temporary_download(path: Path) -> bool:
    return path.suffix.lower() in TEMP_EXTENSIONS or path.name.startswith("~$")


def category_from_filename(path: Path) -> str | None:
    """Return the final underscore tag, e.g. 'gis' from 'map_gis.pdf'."""
    stem = path.stem
    if "_" not in stem:
        return None

    base, tag = stem.rsplit("_", 1)
    tag = tag.strip()
    if not base.strip() or not tag:
        return None

    # Prevent unsafe characters from becoming Windows folder names.
    tag = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", tag).strip(" ._")
    return tag or None


def normalize_label(value: str) -> str:
    """Normalize a label so GIS, gis, and g-i-s compare consistently."""
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def display_folder_name(tag: str) -> str:
    normalized = normalize_label(tag)
    if normalized in KNOWN_LABELS:
        return KNOWN_LABELS[normalized]
    return re.sub(r"[-_]", " ", tag).strip().title()


def find_child_folder_case_insensitive(parent: Path, wanted_name: str) -> Path | None:
    """Find an immediate child folder by exact name, ignoring capitalization."""
    try:
        for child in parent.iterdir():
            if child.is_dir() and child.name.casefold() == wanted_name.casefold():
                return child
    except OSError as exc:
        logging.warning("Could not search folder %s: %s", parent, exc)
    return None


def find_course_folder(wanted_name: str) -> Path | None:
    """Find the mapped course folder. Never create a missing folder on the S: drive."""
    if not SEMESTER_ROOT.is_dir():
        logging.error(
            "Semester folder is unavailable: %s. Check that drive S: is connected and SEMESTER_ROOT is correct.",
            SEMESTER_ROOT,
        )
        return None

    exact = find_child_folder_case_insensitive(SEMESTER_ROOT, wanted_name)
    if exact:
        return exact

    # Handle a folder name that differs only by a small trailing truncation/wording variation.
    wanted_compact = normalize_label(wanted_name)
    try:
        possible = []
        for child in SEMESTER_ROOT.iterdir():
            if not child.is_dir():
                continue
            actual_compact = normalize_label(child.name)
            if (
                len(actual_compact) >= int(len(wanted_compact) * 0.75)
                and (wanted_compact.startswith(actual_compact) or actual_compact.startswith(wanted_compact))
            ):
                possible.append(child)
        if len(possible) == 1:
            logging.info("Using matching course folder: %s", possible[0])
            return possible[0]
    except OSError as exc:
        logging.warning("Could not search semester folder %s: %s", SEMESTER_ROOT, exc)

    logging.error(
        "The known course folder '%s' was not found under %s. Leaving the file in Downloads; "
        "check COURSE_FOLDER_BY_TAG and the folder name.",
        wanted_name,
        SEMESTER_ROOT,
    )
    return None


def resolve_subject_folder(tag: str) -> Path | None:
    """Known tags go to mapped semester courses; new tags get a folder on Desktop."""
    normalized_tag = normalize_label(tag)
    mapped_course = COURSE_FOLDER_BY_TAG.get(normalized_tag)

    if mapped_course:
        return find_course_folder(mapped_course)

    # An unrecognized/new category is kept separate on the Desktop, not in Sem 3.
    new_folder_name = display_folder_name(tag)
    new_folder = DESKTOP_ROOT / new_folder_name
    try:
        new_folder.mkdir(parents=True, exist_ok=True)
        logging.info("New/unknown label '%s': using Desktop folder %s", tag, new_folder)
        return new_folder
    except OSError as exc:
        logging.error("Could not create Desktop folder %s: %s", new_folder, exc)
        return None


def resolve_type_folder(subject_folder: Path, type_name: str) -> Path | None:
    """Reuse an existing immediate file-type folder, or create it if missing."""
    existing = find_child_folder_case_insensitive(subject_folder, type_name)
    if existing is not None:
        return existing

    new_folder = subject_folder / type_name
    try:
        new_folder.mkdir(parents=True, exist_ok=True)
        return new_folder
    except OSError as exc:
        logging.error("Could not create file-type folder %s: %s", new_folder, exc)
        return None


def unique_destination(destination: Path) -> Path:
    """Avoid overwriting an existing file by adding (1), (2), etc."""
    if not destination.exists():
        return destination

    counter = 1
    while True:
        candidate = destination.with_name(f"{destination.stem} ({counter}){destination.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def organize_file(path: Path) -> bool:
    tag = category_from_filename(path)
    if tag is None:
        logging.info("Skipped (no _tag before extension): %s", path.name)
        return False

    type_name = EXTENSION_FOLDERS.get(path.suffix.lower(), "Other")
    subject_folder = resolve_subject_folder(tag)
    if subject_folder is None:
        return False

    destination_dir = resolve_type_folder(subject_folder, type_name)
    if destination_dir is None:
        return False

    try:
        destination = unique_destination(destination_dir / path.name)
        shutil.move(str(path), str(destination))
        logging.info("Moved: %s  ->  %s", path.name, destination)
        return True
    except (OSError, shutil.Error) as exc:
        logging.error("Could not move %s: %s", path.name, exc)
        return False


def main() -> None:
    if not DOWNLOADS_DIR.exists():
        raise SystemExit(
            f"Downloads folder not found: {DOWNLOADS_DIR}\n"
            "Edit DOWNLOADS_DIR near the top of this script to match your browser's download folder."
        )

    # Record files already in Downloads. They must not be organized at startup.
    initial_snapshot: Dict[str, FileSignature] = {}
    for path in DOWNLOADS_DIR.iterdir():
        try:
            if path.is_file() and not is_temporary_download(path):
                initial_snapshot[path.name] = signature(path)
        except OSError:
            pass

    # filename -> (last signature, number of identical checks)
    stability: Dict[str, Tuple[FileSignature, int]] = {}

    logging.info("Watching new downloads in: %s", DOWNLOADS_DIR)
    logging.info("Known course destinations are under: %s", SEMESTER_ROOT)
    logging.info("Unknown/new labels will use Desktop: %s", DESKTOP_ROOT)
    logging.info("Naming rule: file_label.ext (example: notes_gis.pdf)")
    logging.info("Files already present at startup will be left alone. Press Ctrl+C to stop.")

    try:
        while True:
            try:
                paths = list(DOWNLOADS_DIR.iterdir())
            except OSError as exc:
                logging.error("Cannot read Downloads folder: %s", exc)
                time.sleep(POLL_SECONDS)
                continue

            present_names = set()
            for path in paths:
                try:
                    if not path.is_file() or is_temporary_download(path):
                        continue
                    present_names.add(path.name)
                    current_signature = signature(path)

                    if initial_snapshot.get(path.name) == current_signature:
                        continue

                    previous = stability.get(path.name)
                    if previous and previous[0] == current_signature:
                        stable_count = previous[1] + 1
                    else:
                        stable_count = 1
                    stability[path.name] = (current_signature, stable_count)

                    if stable_count >= STABLE_CHECKS:
                        moved = organize_file(path)
                        stability.pop(path.name, None)
                        if moved:
                            initial_snapshot.pop(path.name, None)
                        else:
                            # Remember skipped files so they aren't repeatedly logged.
                            initial_snapshot[path.name] = current_signature
                except FileNotFoundError:
                    # The browser or another process may still be renaming the file.
                    stability.pop(path.name, None)
                except OSError as exc:
                    logging.debug("Could not inspect %s: %s", path.name, exc)

            for name in list(stability):
                if name not in present_names:
                    stability.pop(name, None)

            time.sleep(POLL_SECONDS)

    except KeyboardInterrupt:
        logging.info("Sorter stopped.")


if __name__ == "__main__":
    main()
