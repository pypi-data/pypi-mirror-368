import argparse
import json
import mimetypes
import os
import time
from pathlib import Path

import vertexai
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not available, skip loading .env file
    pass

# Import from new modules
from app.utils.ai_handler import generate_names_with_gemini
from app.utils.file_utils import log_results
from app.utils.image_processor import process_image_data

# --- Configuration ---
# Load from environment variables with fallback defaults
PROJECT_ID = os.getenv("PROJECT_ID", "image-filename-ai")
LOCATION = os.getenv("LOCATION", "us-central1")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash-exp")
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Improved retry configuration with exponential backoff
# These can also be customized via environment variables
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
BASE_RETRY_DELAY = int(os.getenv("BASE_RETRY_DELAY", "10"))  # Base delay in seconds
MAX_RETRY_DELAY = int(os.getenv("MAX_RETRY_DELAY", "300"))  # Maximum delay (5 minutes)
RATE_LIMIT_DELAY = int(os.getenv("RATE_LIMIT_DELAY", "60"))  # Additional delay when rate limited

# --- Helper Functions ---


def load_processed_files(output_dir: Path, log_mode: str) -> set:
    """Load already processed files from existing results.json files."""
    processed_files = set()

    if log_mode == "central" or log_mode == "flat":
        # Single central log file
        log_file = output_dir / "results.json"
        if log_file.exists():
            try:
                with open(log_file) as f:
                    data = json.load(f)
                    for entry in data:
                        if "original_filename" in entry:
                            processed_files.add(entry["original_filename"])
                        elif "original_path" in entry:
                            # Fallback: extract filename from path
                            original_path = Path(entry["original_path"])
                            processed_files.add(original_path.name)
                print(f"Loaded {len(processed_files)} processed files from {log_file}")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not read log file {log_file}: {e}")

    elif log_mode == "project_level":
        # Multiple project-level log files
        for results_file in output_dir.rglob("results.json"):
            try:
                with open(results_file) as f:
                    data = json.load(f)
                    for entry in data:
                        if "original_filename" in entry:
                            processed_files.add(entry["original_filename"])
                        elif "original_path" in entry:
                            # Fallback: extract filename from path
                            original_path = Path(entry["original_path"])
                            processed_files.add(original_path.name)
                print(f"Loaded {len(data)} processed files from {results_file}")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not read log file {results_file}: {e}")

    elif log_mode == "per_folder":
        # Log files in each folder
        for results_file in output_dir.rglob("results.json"):
            try:
                with open(results_file) as f:
                    data = json.load(f)
                    for entry in data:
                        if "original_filename" in entry:
                            processed_files.add(entry["original_filename"])
                        elif "original_path" in entry:
                            # Fallback: extract filename from path
                            original_path = Path(entry["original_path"])
                            processed_files.add(original_path.name)
                print(f"Loaded {len(data)} processed files from {results_file}")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not read log file {results_file}: {e}")

    total_processed = len(processed_files)
    if total_processed > 0:
        print(f"Total processed files to skip: {total_processed}")
        print("Sample processed files:", list(processed_files)[:5])

    return processed_files


def generate_with_retry(
    model: GenerativeModel,
    image_bytes: bytes,
    mime_type: str,
    language_code: str,
    original_filename: str,
    max_retries: int = MAX_RETRIES,
) -> dict | None:
    """Generate names with exponential backoff retry logic."""

    for attempt in range(max_retries):
        try:
            print(f"  Attempt {attempt + 1}/{max_retries} for AI generation...")
            result = generate_names_with_gemini(
                model=model,
                image_bytes=image_bytes,
                mime_type=mime_type,
                language_code=language_code,
                original_filename=original_filename,
            )
            if result:
                print(f"  ✓ AI generation successful on attempt {attempt + 1}")
                return result

        except Exception as e:
            error_msg = str(e).lower()
            print(f"  ✗ Attempt {attempt + 1} failed: {e}")

            # Check if it's a rate limiting error
            is_rate_limit = any(
                keyword in error_msg
                for keyword in [
                    "rate limit",
                    "quota",
                    "too many requests",
                    "429",
                    "resource_exhausted",
                ]
            )

            if attempt < max_retries - 1:  # Don't delay after the last attempt
                if is_rate_limit:
                    # Longer delay for rate limiting + exponential backoff
                    delay = RATE_LIMIT_DELAY + (BASE_RETRY_DELAY * (2**attempt))
                    delay = min(delay, MAX_RETRY_DELAY)  # Cap the delay
                    print(f"  Rate limit detected. Waiting {delay} seconds before retry...")
                else:
                    # Regular exponential backoff
                    delay = BASE_RETRY_DELAY * (2**attempt)
                    delay = min(delay, MAX_RETRY_DELAY)  # Cap the delay
                    print(f"  Waiting {delay} seconds before retry...")

                time.sleep(delay)
            else:
                print(f"  All {max_retries} attempts failed. Skipping this image.")

    return None


# --- Main Processing Logic ---


def process_images(
    input_dir: Path,
    output_dir: Path,
    language_code: str,
    model: GenerativeModel,
    target_format: str | None,
    max_width: int | None,
    log_mode: str = "per_folder",
):
    """Finds images in the input directory, processes them using AI, resizes/reformats, and saves them."""

    print(f"Starting image processing run at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Target language: {language_code}")
    print(f"Target format: {target_format or 'Original'}")
    print(f"Max width: {max_width or 'Original'}")
    print(f"Log mode: {log_mode}")

    # Load already processed files for resume functionality
    print("\nChecking for already processed files...")
    processed_files = load_processed_files(output_dir, log_mode)

    processed_count = 0
    failed_count = 0
    skipped_count = 0

    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' not found.")
        return

    if not output_dir.exists():
        print(f"Output directory '{output_dir}' not found. Creating it.")
        output_dir.mkdir(parents=True, exist_ok=True)

    # Set up logging based on log_mode
    if log_mode == "central":
        central_log_json = output_dir / "results.json"
        central_log_csv = output_dir / "results.csv"
    elif log_mode == "flat":
        central_log_json = output_dir / "results.json"
        central_log_csv = output_dir / "results.csv"
    elif log_mode == "project_level":
        project_logs = {}

    print("\nStarting to process images...")
    print("=" * 50)

    for item in input_dir.rglob("*"):
        if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
            original_path = item
            original_filename = original_path.name

            # Check if this file was already processed
            if original_filename in processed_files:
                print(f"⏭️  Skipping already processed: {original_filename}")
                skipped_count += 1
                continue

            print("-" * 30)
            print(f"📁 Processing: {original_filename}")

            # Determine output path structure
            relative_path = original_path.relative_to(input_dir)

            if log_mode == "flat":
                output_subdir = output_dir
            else:
                output_subdir = output_dir / relative_path.parent

            output_subdir.mkdir(parents=True, exist_ok=True)

            # Determine log file paths based on log_mode
            if log_mode == "central" or log_mode == "flat":
                log_json_file = central_log_json
                log_csv_file = central_log_csv
            elif log_mode == "project_level":
                if len(relative_path.parts) > 1:
                    project_name = relative_path.parts[0]
                else:
                    project_name = "root"

                project_output_dir = output_dir / project_name
                project_output_dir.mkdir(parents=True, exist_ok=True)

                if project_name not in project_logs:
                    project_logs[project_name] = {
                        "json": project_output_dir / "results.json",
                        "csv": project_output_dir / "results.csv",
                    }

                log_json_file = project_logs[project_name]["json"]
                log_csv_file = project_logs[project_name]["csv"]
            else:  # per_folder mode
                log_json_file = output_subdir / "results.json"
                log_csv_file = output_subdir / "results.csv"

            # Read and prepare image data
            try:
                original_image_bytes = original_path.read_bytes()
                mime_type = mimetypes.guess_type(original_path)[0]
                if not mime_type or not mime_type.startswith("image/"):
                    print(f"❌ Skipping {original_path}: Invalid image mime type ({mime_type})")
                    failed_count += 1
                    continue
            except Exception as e:
                print(f"❌ Error reading image {original_path}: {e}")
                failed_count += 1
                continue

            # Generate new names using Gemini with retry logic
            generation_result = generate_with_retry(
                model=model,
                image_bytes=original_image_bytes,
                mime_type=mime_type,
                language_code=language_code,
                original_filename=original_filename,
            )

            if generation_result:
                new_filename_stem = generation_result["filename"]
                alt_text = generation_result["alt_text"]

                # Process image data (resize/reformat)
                processed_bytes, output_extension = process_image_data(
                    image_bytes=original_image_bytes,
                    target_format=target_format,
                    max_width=max_width,
                    original_mime_type=mime_type,
                )

                if processed_bytes is None:
                    print(f"❌ Error processing image data for {original_path}")
                    failed_count += 1
                    continue

                new_path = output_subdir / f"{new_filename_stem}{output_extension}"

                # Handle filename conflicts in flat mode
                if log_mode == "flat":
                    counter = 1
                    original_stem = new_filename_stem
                    while new_path.exists():
                        new_filename_stem = f"{original_stem}-{counter}"
                        new_path = output_subdir / f"{new_filename_stem}{output_extension}"
                        counter += 1

                # Check if target file already exists (for non-flat modes)
                if new_path.exists() and log_mode != "flat":
                    print(f"⏭️  Target file already exists: {new_path}")
                    continue

                # Save the processed file
                try:
                    new_path.write_bytes(processed_bytes)
                    print(f"✅ Successfully processed '{original_filename}' → '{new_path.name}'")

                    # Log the success
                    log_results(original_path, new_path, alt_text, log_json_file, log_csv_file)
                    processed_count += 1

                    # Small delay between successful operations to be nice to the API
                    time.sleep(1)

                except OSError as e:
                    print(f"❌ Error writing file {new_path}: {e}")
                    failed_count += 1
                except Exception as e:
                    print(f"❌ Unexpected error writing file {new_path}: {e}")
                    failed_count += 1
            else:
                print(f"❌ Failed to generate names after all retries: {original_filename}")
                failed_count += 1

    print("=" * 50)
    print(f"Processing finished at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"✅ Successfully processed: {processed_count}")
    print(f"❌ Failed/Errored: {failed_count}")
    print(f"⏭️  Skipped (already done): {skipped_count}")
    print(f"📊 Total files encountered: {processed_count + failed_count + skipped_count}")

    # Print summary of log file locations
    if log_mode == "central":
        print(f"📝 Results logged to: {central_log_json} and {central_log_csv}")
    elif log_mode == "flat":
        print(f"📝 Results logged to (flat): {central_log_json} and {central_log_csv}")
    elif log_mode == "project_level":
        print("📝 Results logged to project-level files:")
        for project, logs in project_logs.items():
            print(f"   {project}: {logs['json']} and {logs['csv']}")
    else:
        print("📝 Results logged to individual folder log files")


def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="Rename images using Gemini based on content and language."
    )
    parser.add_argument(
        "--input-dir", type=str, default="input", help="Directory containing input images."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Base directory for processed images and logs.",
    )
    parser.add_argument(
        "--lang", type=str, default="en", help="Target language code for filename/alt text."
    )
    parser.add_argument(
        "--format",
        type=str,
        default=None,
        choices=["jpg", "png", "webp", "avif", None],
        help="Output image format. Defaults to original format.",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=None,
        help="Maximum width in pixels for output images. Aspect ratio is preserved.",
    )
    parser.add_argument(
        "--log-mode",
        type=str,
        default="per_folder",
        choices=["central", "project_level", "per_folder", "flat"],
        help="Logging mode for results files.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=MAX_RETRIES,
        help=f"Maximum number of retry attempts for failed API calls (default: {MAX_RETRIES})",
    )

    args = parser.parse_args()

    INPUT_DIR = Path(args.input_dir)
    OUTPUT_DIR = Path(args.output_dir)
    LANGUAGE_CODE = args.lang
    TARGET_FORMAT = args.format
    MAX_WIDTH = args.max_width
    LOG_MODE = args.log_mode
    MAX_RETRIES_ARG = args.max_retries

    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # SDK Initialization
    gemini_model = None
    try:
        print("🔧 Configuration:")
        print(
            f"   Project ID: {PROJECT_ID} {'(from env)' if os.getenv('PROJECT_ID') else '(default)'}"
        )
        print(f"   Location: {LOCATION} {'(from env)' if os.getenv('LOCATION') else '(default)'}")
        print(f"   Model: {MODEL_NAME} {'(from env)' if os.getenv('MODEL_NAME') else '(default)'}")
        print(
            f"   Max retries: {MAX_RETRIES_ARG} {'(from args)' if args.max_retries != MAX_RETRIES else '(from env)' if os.getenv('MAX_RETRIES') else '(default)'}"
        )

        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print("✅ Vertex AI SDK initialized successfully")

        gemini_model = GenerativeModel(MODEL_NAME)
        print(f"🤖 Model loaded: {MODEL_NAME}")

    except Exception as e:
        print(f"❌ Error initializing Vertex AI SDK or loading model: {e}")
        exit(1)

    if gemini_model:
        process_images(
            INPUT_DIR, OUTPUT_DIR, LANGUAGE_CODE, gemini_model, TARGET_FORMAT, MAX_WIDTH, LOG_MODE
        )
    else:
        print("❌ Exiting due to failed AI model initialization.")
        exit(1)


if __name__ == "__main__":
    main()
