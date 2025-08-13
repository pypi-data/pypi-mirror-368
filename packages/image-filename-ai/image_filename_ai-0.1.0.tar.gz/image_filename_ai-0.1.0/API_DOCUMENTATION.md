# Image Filename AI API Documentation

## Overview

Image Filename AI is a cloud-based service that uses Google's Gemini AI model to analyze images and generate descriptive, SEO-friendly filenames in multiple languages. The service is designed to process images stored in Google Cloud Storage (GCS) and returns optimized filenames that better describe the image content.

## API Base URL

```
https://<your-api-domain>/api/v1
```

## Authentication

⚠️ **Current Status: Authentication Not Enforced** 

**Important**: The API endpoints are currently **unauthenticated** for development/testing purposes. This means anyone with access to the API URL can make requests.

**Production TODO**: 
- Implement API authentication (API keys, JWT tokens, or OAuth)
- Add rate limiting per client
- Add request validation and sanitization

**Required Service Account Permissions**:
When deploying with proper GCP integration, ensure your service account has:
- `storage.objects.get` (read images from GCS)
- `storage.objects.list` (list bucket contents)  
- `storage.objects.create` (create renamed files)
- `datastore.user` or `cloudFirestore.user` (if using job tracking)

## Endpoints

### Health Check

```
GET /
```

Verifies the API is running and provides status information.

**Response Example:**

```json
{
  "status": "healthy",
  "api_version": "0.1.0",
  "model_status": "initialized"
}
```

**Response Fields:**
- `status`: API health status
- `api_version`: Current API version
- `model_status`: Whether the AI model is initialized ("initialized" or "not initialized")

### Process Images

```
POST /api/v1/process
```

Starts a background job to process images from a Google Cloud Storage bucket. This endpoint initiates asynchronous processing and returns a job ID for tracking.

**Request Body:**

```json
{
  "gcs_input_path": "gs://your-bucket/images-folder/",
  "language_code": "en",
  "user_id": "user123",
  "gcs_output_path": "gs://your-bucket/output-folder/",
  "gcs_log_path": "gs://your-bucket/logs-folder/"
}
```

**Required Fields:**
- `gcs_input_path`: GCS path in format `gs://bucket/prefix` where images are stored
- `language_code`: Target language code for filenames (e.g., 'en', 'sl', 'de')
- `user_id`: ID of the authenticated user making the request

**Optional Fields:**
- `gcs_output_path`: Optional GCS path for processed images
- `gcs_log_path`: Optional GCS path for logs

**Response:**

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Status Codes:**
- `202 Accepted`: Request was valid and job has been queued
- `400 Bad Request`: Invalid request parameters
- `503 Service Unavailable`: AI model not initialized or Firestore service unavailable

## Job Tracking

Job status is not available through a direct API endpoint. Instead, the service uses Firebase Firestore to store job status and results. Your client application should be configured to listen to Firestore document updates for real-time job status.

### Firestore Collection

Jobs are stored in the Firestore collection named `imageProcessingJobs` with the job ID as the document ID.

### Job Status Document Structure

```json
{
  "gcs_path": "gs://your-bucket/images-folder/",
  "language_code": "en",
  "user_id": "user123",
  "status": "processing",  // "pending", "processing", "completed", "failed"
  "created_at": "2023-06-15T10:30:00Z",
  "updated_at": "2023-06-15T10:35:00Z",
  "total_images": 10,
  "progress": 5,
  "output_gcs_path": "gs://your-bucket/images-folder/output/",
  "results": [
    {
      "original_gcs_path": "gs://your-bucket/images-folder/image1.jpg",
      "new_gcs_path": "gs://your-bucket/images-folder/output/red-sports-car-highway.jpg",
      "old_filename": "image1.jpg",
      "new_filename": "red-sports-car-highway.jpg",
      "error": null
    },
    {
      "original_gcs_path": "gs://your-bucket/images-folder/image2.jpg",
      "new_gcs_path": "gs://your-bucket/images-folder/output/mountain-sunrise-landscape.jpg",
      "old_filename": "image2.jpg",
      "new_filename": "mountain-sunrise-landscape.jpg",
      "error": null
    }
  ],
  "error_message": null
}
```

**Job Status Fields:**
- `status`: Current job status
  - `pending`: Job created but processing not started yet
  - `processing`: Job is currently processing images
  - `completed`: All images have been processed
  - `failed`: Job encountered an error
- `total_images`: Total number of images found for processing
- `progress`: Number of images processed so far
- `output_gcs_path`: Path where renamed images are stored
- `results`: Array of result objects for each processed image containing:
  - `original_gcs_path`: Full GCS path to the original image
  - `new_gcs_path`: Full GCS path to the renamed image
  - `old_filename`: Original filename without path
  - `new_filename`: New AI-generated filename with extension
  - `error`: Contains error information if processing this image failed
- `error_message`: Contains error information if the job failed

## Supported File Types

The API supports the following image file extensions:
- .jpg
- .jpeg
- .png
- .webp

## Error Handling

Errors are returned with appropriate HTTP status codes and detailed error messages in the response body.

Common error scenarios:
- Invalid GCS path format
- No supported images found in the specified GCS path
- AI model initialization failure
- Firestore connectivity issues

## Rate Limiting

The API implements rate limiting to ensure service stability. Specific limits may vary based on your service tier.

## Example Client Usage

### JavaScript Example

```javascript
// Example code for starting a job
async function processImages() {
  const response = await fetch('https://your-api-domain/api/v1/process', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer YOUR_AUTH_TOKEN'
    },
    body: JSON.stringify({
      gcs_input_path: 'gs://your-bucket/images/',
      language_code: 'en',
      user_id: 'user123'
    })
  });
  
  const data = await response.json();
  const jobId = data.job_id;
  
  // Setup Firestore listener for job updates
  db.collection('imageProcessingJobs')
    .doc(jobId)
    .onSnapshot((doc) => {
      const jobData = doc.data();
      console.log(`Job Status: ${jobData.status}, Progress: ${jobData.progress}/${jobData.total_images}`);
      
      if (jobData.status === 'completed' || jobData.status === 'failed') {
        // Handle job completion or failure
        console.log('Job results:', jobData.results);
      }
    });
}
```

### Python Example

```python
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate('path/to/serviceAccount.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Start a job
response = requests.post(
    'https://your-api-domain/api/v1/process',
    headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_AUTH_TOKEN'
    },
    json={
        'gcs_input_path': 'gs://your-bucket/images/',
        'language_code': 'en',
        'user_id': 'user123'
    }
)

job_id = response.json()['job_id']
print(f"Job started with ID: {job_id}")

# You can then query Firestore for job status
job_ref = db.collection('imageProcessingJobs').document(job_id)
job = job_ref.get()
print(f"Job status: {job.get('status')}")
```

## Large Language Model (LLM) Integration Guide

For AI systems and large language models interacting with this API:

1. **Endpoint Structure**: The API follows RESTful principles with a base path of `/api/v1`.

2. **Asynchronous Processing**: All image processing is handled asynchronously. The API returns a job ID immediately, but actual processing happens in the background.

3. **State Management**: Job state must be tracked through Firestore. No direct API endpoints exist for checking job status.

4. **Input Requirements**:
   - GCS paths must be in the format `gs://bucket-name/path/to/folder/`
   - Language codes follow ISO standards (e.g., 'en', 'fr', 'de', 'sl')
   - User authentication/identification is required

5. **Response Processing**: When consuming this API, always check for:
   - Appropriate HTTP status codes (202 for accepted jobs)
   - Error messages in response bodies
   - Job ID for subsequent tracking

6. **Firestore Document Structure**: When reading job status from Firestore, parse the document structure as described in the Job Tracking section.

## Best Practices

1. **Batch Processing**: For optimal performance, process images in batches rather than individually.

2. **Error Handling**: Implement robust error handling for both API requests and Firestore operations.

3. **Monitoring**: Monitor job progress through Firestore to provide feedback to users.

4. **Language Support**: The system supports multiple languages for generating filenames. Always specify the desired language code. 