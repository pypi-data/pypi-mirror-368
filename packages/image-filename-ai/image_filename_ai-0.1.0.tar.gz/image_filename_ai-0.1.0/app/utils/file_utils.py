import csv
import json
import re
import time
from pathlib import Path


def sanitize_filename(name):
    """Removes invalid characters and replaces spaces for filenames."""
    # Replace diacritical characters with English equivalents
    replacements = {
        # Slovenian and similar
        "č": "c",
        "Č": "C",
        "š": "s",
        "Š": "S",
        "ž": "z",
        "Ž": "Z",
        # German
        "ä": "a",
        "Ä": "A",
        "ö": "o",
        "Ö": "O",
        "ü": "u",
        "Ü": "U",
        "ß": "ss",
        # French
        "à": "a",
        "á": "a",
        "â": "a",
        "ã": "a",
        "å": "a",
        "À": "A",
        "Á": "A",
        "Â": "A",
        "Ã": "A",
        "Å": "A",
        "è": "e",
        "é": "e",
        "ê": "e",
        "ë": "e",
        "È": "E",
        "É": "E",
        "Ê": "E",
        "Ë": "E",
        "ì": "i",
        "í": "i",
        "î": "i",
        "ï": "i",
        "Ì": "I",
        "Í": "I",
        "Î": "I",
        "Ï": "I",
        "ò": "o",
        "ó": "o",
        "ô": "o",
        "õ": "o",
        "ø": "o",
        "Ò": "O",
        "Ó": "O",
        "Ô": "O",
        "Õ": "O",
        "Ø": "O",
        "ù": "u",
        "ú": "u",
        "û": "u",
        "Ù": "U",
        "Ú": "U",
        "Û": "U",
        "ý": "y",
        "ÿ": "y",
        "Ý": "Y",
        "ç": "c",
        "Ç": "C",
        "ñ": "n",
        "Ñ": "N",
        # Polish
        "ą": "a",
        "Ą": "A",
        "ć": "c",
        "Ć": "C",
        "ę": "e",
        "Ę": "E",
        "ł": "l",
        "Ł": "L",
        "ń": "n",
        "Ń": "N",
        "ś": "s",
        "Ś": "S",
        "ź": "z",
        "Ź": "Z",
        "ż": "z",
        "Ż": "Z",
        # Czech
        "ř": "r",
        "Ř": "R",
        "ď": "d",
        "Ď": "D",
        "ť": "t",
        "Ť": "T",
        "ň": "n",
        "Ň": "N",
        "ů": "u",
        "Ů": "U",
        # Other common
        "æ": "ae",
        "Æ": "AE",
        "œ": "oe",
        "Œ": "OE",
    }

    # Apply character replacements
    for old_char, new_char in replacements.items():
        name = name.replace(old_char, new_char)

    # Remove invalid characters
    name = re.sub(r'[\/*?:"<>|]', "", name)
    # Replace spaces with hyphens
    name = name.replace(" ", "-").lower()
    # Consolidate multiple hyphens
    name = re.sub(r"-+", "-", name)
    # Remove leading/trailing hyphens
    name = name.strip("-")
    # Limit length (optional)
    # name = name[:100]
    return name


def log_results(original_path, new_path, alt_text, log_json_file: Path, log_csv_file: Path):
    """Appends processing results to JSON and CSV log files."""
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "original_path": str(original_path),
        "new_path": str(new_path),
        "original_filename": original_path.name,
        "new_filename": new_path.name,
        "alt_text": alt_text,
    }

    # Ensure log directory exists (it should, as it's the image output subdir)
    log_json_file.parent.mkdir(parents=True, exist_ok=True)

    # Log to JSON
    try:
        data = []
        if log_json_file.exists() and log_json_file.stat().st_size > 0:
            with open(log_json_file) as f:
                try:
                    data = json.load(f)
                    if not isinstance(
                        data, list
                    ):  # Handle case where file exists but is not a list
                        print(
                            f"Warning: JSON log file {log_json_file} does not contain a list. Reinitializing."
                        )
                        data = []
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from {log_json_file}. Reinitializing.")
                    data = []  # Reinitialize if file is corrupted
        data.append(log_entry)
        with open(log_json_file, "w") as f:
            json.dump(data, f, indent=4)
    except OSError as e:
        print(f"Error writing to JSON log {log_json_file}: {e}")

    # Log to CSV
    try:
        file_exists = log_csv_file.exists()
        is_empty = not file_exists or log_csv_file.stat().st_size == 0
        with open(log_csv_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=log_entry.keys())
            if is_empty:  # Write header only if file is new or empty
                writer.writeheader()
            writer.writerow(log_entry)
    except OSError as e:
        print(f"Error writing to CSV log {log_csv_file}: {e}")
