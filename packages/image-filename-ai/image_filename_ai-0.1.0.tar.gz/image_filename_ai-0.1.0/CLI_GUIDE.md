# Image Filename AI – CLI Guide

This guide explains how to use the command-line interface (CLI) to process local images with AI-generated, SEO-friendly filenames and alt text.

## Prerequisites

- Python 3.11+ (tested on 3.11, 3.12, 3.13)
- A Google Cloud project with Vertex AI enabled
- A service account with required roles (see below)
- Google Cloud credentials configured locally

### Required IAM permissions (service account)

- Vertex AI prediction access
- Storage read/list (for reading inputs if needed in scripts)
- Storage object create (for writing outputs if you later upload to GCS)

At minimum for CLI-only local processing, you need Vertex AI and general auth; GCS is not required unless you use helper scripts to upload results.

## Install and set up

```bash
git clone <repository-url>
cd image-filename-ai

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Configure credentials

Set the environment variable to your service account key file:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

Alternatively, place `serviceAccountKey.json` in the repository root (gitignored). The API prefers the environment variable; the CLI only needs Google auth available to the Vertex AI SDK.

## Quick start

Process images from `input/` to `output/` in English, preserving subfolders:

```bash
python cli.py --input-dir input --output-dir output --lang en
```

Common variations:

```bash
# Convert to WebP and resize to max width 1600px
python cli.py --input-dir input --output-dir output --lang en --format webp --max-width 1600

# Central logging (single results.json/results.csv in output root)
python cli.py --input-dir input --output-dir output --lang en --log-mode central

# Flat output (all files in a single folder with conflict-safe names)
python cli.py --input-dir input --output-dir output --lang en --log-mode flat
```

## CLI arguments

- `--input-dir` (str): Source directory containing images. Default: `input`
- `--output-dir` (str): Destination base directory. Default: `output`
- `--lang` (str): Language code for filename/alt text (e.g., `en`, `de`, `sl`). Default: `en`
- `--format` (str|None): Output format: `jpg`, `png`, `webp`, `avif`. Default: keep original
- `--max-width` (int|None): Max output width in pixels. Aspect ratio preserved
- `--log-mode` (str): `central` | `project_level` | `per_folder` (default) | `flat`
- `--max-retries` (int): Max retry attempts for AI calls (exponential backoff)

Supported input file extensions: `.jpg`, `.jpeg`, `.png`, `.webp`.

## Input directory examples

You can mirror any nested structure under your `--input-dir`. The tool preserves the same structure under `--output-dir` (except in `flat` mode).

Example input structures (based on typical contents of `./input`):

```
input/
├── client-a/
│   ├── project-1/
│   │   ├── IMG_0012.jpg
│   │   └── IMG_0013.jpg
│   └── project-2/
│       └── hero.png
└── client-b/
    └── campaign/
        ├── product1.webp
        └── product2.jpg
```

Output with default mode (`per_folder`):

```
output/
├── client-a/
│   ├── project-1/
│   │   ├── results.json
│   │   ├── results.csv
│   │   ├── golden-retriever-playing-fetch.webp
│   │   └── modern-kitchen-interior.webp
│   └── project-2/
│       ├── results.json
│       ├── results.csv
│       └── site-hero-banner.webp
└── client-b/
    └── campaign/
        ├── results.json
        ├── results.csv
        ├── product-1-beauty-shot.webp
        └── product-2-closeup.webp
```

## Logging modes

- `per_folder` (default): Each output subfolder gets its own `results.json` and `results.csv`.
- `project_level`: One log per top-level folder under the input directory.
- `central`: Single `results.json` and `results.csv` in the output root.
- `flat`: Flattens structure; single output directory; central logs. Filename conflicts are auto-resolved with numeric suffixes.

## What gets logged

Each processed image appends an entry to JSON and CSV logs with:

- `timestamp`
- `original_path`
- `new_path`
- `original_filename`
- `new_filename`
- `alt_text`

## Resume functionality

The CLI scans existing `results.json` logs and skips already-processed files (by `original_filename`). This allows safe re-runs and interrupted job resumes.

## Image processing

- Resizing: If `--max-width` is set and the image is wider, the image is resized using high-quality downsampling.
- Format conversion: If `--format` is set, images are converted accordingly. Transparency is handled when converting to JPEG (background applied).
- Defaults: WebP quality ~90; JPEG quality ~90.

## Examples

```bash
# English names, keep original format/size
python cli.py --input-dir input/photos --output-dir output/renamed --lang en

# German names, resize to 1024px
python cli.py --input-dir input/photos --output-dir output/optimized --lang de --max-width 1024

# WebP conversion with project-level logs
python cli.py --input-dir input/company --output-dir output/company --lang en --format webp --log-mode project_level

# Flatten deeply nested folders into a single output directory
python cli.py --input-dir input/nested --output-dir output/flat --lang en --format webp --log-mode flat
```

## Troubleshooting

### Credentials / auth

- Error like "Could not automatically determine credentials": ensure `GOOGLE_APPLICATION_CREDENTIALS` is set to a valid JSON key file, or you have run `gcloud auth application-default login` (not recommended for CI).

### AVIF conversion

- Pillow AVIF support may require `libavif`. On macOS:
  - `brew install libavif`
  - Reinstall Pillow from source so it picks up AVIF: `pip install --force-reinstall --no-cache-dir --no-binary Pillow Pillow`
- If issues persist, use `--format webp`.

### Rate limiting / retries

- The CLI uses exponential backoff and a special delay when a rate limit is detected. Increase `--max-retries` for large batches or stricter quotas.
- Consider adding small pauses between large directory batches if you still hit quotas.

### File types

- Files with unknown or unsupported MIME types are skipped. Ensure files have proper extensions and are valid images.

## Configuration notes

- The CLI initializes Vertex AI using default constants defined near the top of `cli.py` (`PROJECT_ID`, `LOCATION`, `MODEL_NAME`). Update these to match your GCP project.
- For API/server usage, see `README.md` and `API_DOCUMENTATION.md`.

## Verifying your setup

1. Create `input/` with a couple of test images.
2. Run a basic command (see Quick start).
3. Check `output/` for processed files and `results.json`/`results.csv` logs.

If it works locally, you can proceed to larger batches and advanced logging modes.


