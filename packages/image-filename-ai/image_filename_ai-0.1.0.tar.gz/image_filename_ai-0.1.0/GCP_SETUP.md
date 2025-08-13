# Minimal GCP Setup

This guide shows the minimal steps to run the CLI and API.

## 1) Enable required APIs

Enable these in your Google Cloud project:
- Vertex AI API
- Cloud Firestore API (API mode only)
- Cloud Storage API (API mode only)

You can enable via the Cloud Console or:
```bash
gcloud services enable aiplatform.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com
```

## 2) Create a service account and key

1. Create service account (or reuse an existing one):
   - Name: image-filename-ai
2. Grant roles (attach to this service account):
   - For CLI-only:
     - roles/aiplatform.user (Vertex AI User)
   - For API mode (GCS + Firestore):
     - roles/aiplatform.user
     - roles/storage.objectViewer (read objects)
     - roles/storage.objectCreator (create objects)
     - roles/datastore.user (Firestore read/write)
3. Create and download a JSON key for this service account.

Keep this key private. Do not commit it to version control.

## 3) Configure credentials locally

Choose one method:

- Environment variable (recommended):
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/service-account-key.json"
```

- Or place `serviceAccountKey.json` in the project root (gitignored). The API and CLI will detect it if the env var is not set.

## 4) Set project configuration

Create `.env` at the repo root or export environment variables:
```bash
PROJECT_ID=your-gcp-project-id
LOCATION=us-central1
MODEL_NAME=gemini-2.0-flash-exp
```

## 5) Verify

- CLI quick test:
```bash
python cli.py --input-dir input --output-dir output --lang en
```

- API quick test (if using Docker):
```bash
docker compose up --build
# Then open http://localhost:8000/ and http://localhost:8000/docs
```

If you use the API to process GCS paths, ensure your service account has the Storage and Firestore roles listed above.

## Notes
- CLI mode does not require Firestore or Storage permissions unless you use helper scripts to upload results.
- API mode relies on Firestore for job tracking and on GCS for listing/copying images.


