import asyncio
import io  # For handling image bytes
import logging
import os
import shutil
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from firebase_admin import firestore
from google.cloud import storage
from PIL import Image  # Import Pillow
from pydantic import BaseModel
from vertexai.generative_models import GenerativeModel, Part  # Import Gemini classes

from app.core.config import settings

# from app.services.image_service import process_images_from_gcs # No longer needed directly
from app.core.firebase_setup import get_firestore_client
from app.core.state import app_state  # Import from new state module
from app.models.image import ProcessRequest

# Configure logging for this module
logger = logging.getLogger(__name__)

router = APIRouter()


# New response model for returning the job ID
class JobResponse(BaseModel):
    job_id: str


# Placeholder helper function for Gemini call (adapt from original service later)
async def generate_filename_from_image(
    model: GenerativeModel,
    image_bytes: bytes,
    filename: str,
    language_code: str,
    mime_type: str | None = None,  # Add optional mime_type argument
) -> str:
    """Generates a descriptive filename using the Gemini model based on image content."""
    max_retries = 3
    retry_count = 0
    base_delay = 4  # Increase base delay from 2 to 4 seconds

    while retry_count <= max_retries:
        try:
            # Determine the image MIME type IF NOT PROVIDED
            if not mime_type:
                # A more robust solution might use python-magic
                _, ext = os.path.splitext(filename)
                mime_type_map = {
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".png": "image/png",
                    ".webp": "image/webp",
                }
                mime_type = mime_type_map.get(ext.lower())
                if not mime_type:
                    logger.warning(
                        f"Could not determine MIME type for {filename}, defaulting to image/jpeg"
                    )
                    mime_type = "image/jpeg"  # Default or raise error
            # else: use the provided mime_type

            # Prepare the image Part for the model
            image_part = Part.from_data(image_bytes, mime_type=mime_type)

            # Define the prompt for the model
            # TODO: Refine this prompt for better results and consistency
            prompt = f"""
Analyze the content of the following image.
Generate a concise, descriptive, SEO-friendly filename suggestion in the language '{language_code}'.
- Use lowercase letters.
- Replace spaces with hyphens.
- Include the most relevant keywords describing the image content.
- Do not include the file extension.
- Respond ONLY with the suggested filename.

Example:
If the image shows a black cat sitting on a red sofa, a good filename in English would be 'black-cat-red-sofa'.

Original Filename (for context only, do not include in response): {filename}
Language: {language_code}

Suggested Filename:"""

            # Combine prompt and image
            content = [prompt, image_part]

            logger.info(f"Calling Gemini model for {filename} in {language_code}...")
            # Call the Gemini model asynchronously
            # TODO: Add generation_config if needed (temperature, max_output_tokens, etc.)
            response = await model.generate_content_async(content)

            # Extract the text response
            # TODO: Add more robust parsing/validation of the response format
            suggested_filename = response.text.strip()
            logger.info(f"Gemini suggested filename for {filename}: {suggested_filename}")

            # Basic validation/cleanup (optional)
            if not suggested_filename:
                raise ValueError("Gemini model returned an empty response.")
            # Remove potential leading/trailing quotes if the model included them
            suggested_filename = suggested_filename.strip("\"'")
            # Ensure basic format (lowercase, hyphens) - model should handle this based on prompt
            suggested_filename = suggested_filename.lower().replace(" ", "-")
            # Remove any potentially remaining problematic characters (simple example)
            suggested_filename = "".join(c for c in suggested_filename if c.isalnum() or c == "-")

            return suggested_filename

        except Exception as e:
            # Check if this is a rate limit error (429)
            if "429 Quota exceeded" in str(e) and retry_count < max_retries:
                retry_count += 1
                # More aggressive formula: base_delay * 3^retry_count instead of 2^retry_count
                delay = base_delay * (3 ** (retry_count - 1))
                logger.warning(
                    f"Rate limit reached for {filename}. Retrying in {delay} seconds (attempt {retry_count}/{max_retries})..."
                )
                await asyncio.sleep(delay)
                continue
            else:
                # Either not a 429 error or we've exhausted our retries
                logger.error(f"Error generating filename for {filename} using Gemini: {e}")
                # Re-raise the exception to be caught by the main processing loop
                raise

    # This should never be reached due to the raise in the else clause above
    # But adding as a fallback just in case
    raise Exception(f"Failed to generate filename for {filename} after {max_retries} retries")


async def process_images_background(job_id: str, gcs_path: str, language_code: str):
    """Background task to download, process images, copy to output in GCS, and update Firestore."""
    logger.info(f"Background task started for job {job_id} with path {gcs_path}")

    db = get_firestore_client()
    gemini_model = app_state.get("gemini_model")

    if not db:
        logger.error(f"Job {job_id}: Firestore client not available. Aborting task.")
        # No easy way to update Firestore here, job will remain 'pending'
        return
    if not gemini_model:
        logger.error(f"Job {job_id}: Gemini model not available. Aborting task.")
        # Update Firestore status to failed
        try:
            job_ref_fail = db.collection(settings.FIRESTORE_JOBS_COLLECTION).document(job_id)
            update_data = {
                "status": "failed",
                "error_message": "AI model not initialized during task execution.",
                "updated_at": firestore.SERVER_TIMESTAMP,
            }
            await asyncio.to_thread(job_ref_fail.update, update_data)
        except Exception as firestore_e:
            logger.error(
                f"Job {job_id}: Failed to update Firestore status to failed after model init error: {firestore_e}"
            )
        return

    job_ref = db.collection(settings.FIRESTORE_JOBS_COLLECTION).document(job_id)
    temp_input_dir = f"./input/{job_id}"

    try:
        # 1. Setup Temporary Storage
        os.makedirs(temp_input_dir, exist_ok=True)
        logger.info(f"Job {job_id}: Created temporary directory: {temp_input_dir}")

        # 2. Download Images from GCS and setup GCS output path
        logger.info(f"Job {job_id}: Downloading images from {gcs_path}...")
        try:
            storage_client = storage.Client()
            bucket_name, prefix = gcs_path.replace("gs://", "").split("/", 1)

            # Add more logging
            logger.info(f"Job {job_id}: Using bucket '{bucket_name}' with prefix '{prefix}'")

            # Setup the output path structure (putting output folder within the input prefix)
            if not prefix.endswith("/"):
                prefix += "/"
            output_prefix = prefix + "output/"
            output_gcs_path = f"gs://{bucket_name}/{output_prefix}"

            logger.info(f"Job {job_id}: Determined output GCS path: {output_gcs_path}")

            # Log bucket details
            try:
                bucket = storage_client.bucket(bucket_name)
                logger.info(f"Job {job_id}: Successfully accessed bucket '{bucket_name}'")

                # List blobs and log count before filtering
                blobs_list = list(bucket.list_blobs(prefix=prefix))
                logger.info(
                    f"Job {job_id}: Found {len(blobs_list)} items in path with prefix '{prefix}'"
                )

                # Log names of first few blobs to debug
                if blobs_list:
                    sample_blobs = blobs_list[:5]  # Show up to first 5 blobs
                    logger.info(
                        f"Job {job_id}: Sample blob names: {[b.name for b in sample_blobs]}"
                    )

                blobs = blobs_list  # Keep the list to avoid re-listing
            except Exception as bucket_err:
                logger.error(f"Job {job_id}: Error accessing bucket '{bucket_name}': {bucket_err}")
                raise ValueError(
                    f"Cannot access bucket '{bucket_name}': {bucket_err}"
                ) from bucket_err

            downloaded_files = []
            blob_map = {}  # Map of local path to original blob object

            # Log message about supported extensions
            logger.info(
                f"Job {job_id}: Looking for files with extensions: {settings.SUPPORTED_EXTENSIONS}"
            )

            for blob in blobs:
                # Skip "directory" blobs and files already in output folder
                if blob.name.endswith("/") or blob.name.startswith(output_prefix):
                    logger.debug(
                        f"Job {job_id}: Skipping blob '{blob.name}' (directory or in output folder)"
                    )
                    continue
                # Check extension
                _, ext = os.path.splitext(blob.name)
                if ext.lower() not in settings.SUPPORTED_EXTENSIONS:
                    logger.warning(
                        f"Job {job_id}: Skipping unsupported file type: {blob.name} with extension {ext}"
                    )
                    continue

                destination_file_name = os.path.join(temp_input_dir, os.path.basename(blob.name))
                blob.download_to_filename(destination_file_name)
                downloaded_files.append(destination_file_name)
                blob_map[destination_file_name] = blob  # Store blob reference for later use
                logger.info(f"Job {job_id}: Downloaded {blob.name} to {destination_file_name}")

            if not downloaded_files:
                logger.warning(f"Job {job_id}: No supported images found in {gcs_path}")
                raise ValueError(
                    f"No supported images found in specified path: {gcs_path}. Found {len(blobs_list)} total items, but none with supported extensions {settings.SUPPORTED_EXTENSIONS}."
                )
        except Exception as gcs_err:
            logger.error(f"Job {job_id}: Error working with GCS: {gcs_err}")
            raise

        # 3. Count Images & Update Status to Processing
        total_images = len(downloaded_files)
        logger.info(
            f"Job {job_id}: Downloaded {total_images} images. Updating status to 'processing'."
        )
        update_data = {
            "status": "processing",
            "total_images": total_images,
            "output_gcs_path": output_gcs_path,  # Store output path in job document
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
        await asyncio.to_thread(job_ref.update, update_data)

        # 4. Determine batch size based on total number of images
        if total_images <= 5:
            batch_size = total_images  # Update only once at the end
        else:
            batch_size = 5  # Update every 5 images for larger batches

        logger.info(f"Job {job_id}: Using batch size of {batch_size} for Firestore updates")

        # 5. Iterate and Process Images with batched updates
        processed_count = 0
        results_batch = []

        for image_path in downloaded_files:
            original_filename = os.path.basename(image_path)
            original_blob = blob_map[image_path]  # Get the original blob reference
            original_gcs_path = f"gs://{bucket_name}/{original_blob.name}"

            logger.info(
                f"Job {job_id}: Processing image {processed_count + 1}/{total_images}: {original_filename}"
            )

            # Add a standard delay between ALL API calls to avoid hitting rate limits
            # This is in addition to the exponential backoff for 429 errors
            await asyncio.sleep(
                3.0
            )  # Increased from 1.5 to 3.0 seconds to further reduce rate limit errors

            try:
                # Read image bytes
                with open(image_path, "rb") as f:
                    image_bytes = f.read()

                # --- Add Image Resizing ---
                try:
                    img = Image.open(io.BytesIO(image_bytes))

                    # Calculate new size (max 250px on longest side)
                    max_dimension = 250
                    width, height = img.size
                    if max(width, height) > max_dimension:
                        if width > height:
                            new_width = max_dimension
                            new_height = int(height * (max_dimension / width))
                        else:
                            new_height = max_dimension
                            new_width = int(width * (max_dimension / height))
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        logger.info(
                            f"Job {job_id}: Resized {original_filename} from {width}x{height} to {new_width}x{new_height}"
                        )
                    else:
                        logger.info(
                            f"Job {job_id}: Image {original_filename} ({width}x{height}) is within size limits, no resize needed."
                        )

                    # Save resized image to bytes buffer as JPEG (controls compression)
                    output_buffer = io.BytesIO()
                    img.save(
                        output_buffer, format="JPEG", quality=85
                    )  # Save as JPEG with quality 85
                    resized_image_bytes = output_buffer.getvalue()
                    logger.info(
                        f"Job {job_id}: Converted/Compressed {original_filename} to JPEG format for API call (original size: {len(image_bytes)} bytes, new size: {len(resized_image_bytes)} bytes)"
                    )

                    # Use resized bytes and update mime type for Gemini call
                    image_bytes_for_api = resized_image_bytes
                    mime_type_for_api = "image/jpeg"

                except Exception as resize_err:
                    logger.warning(
                        f"Job {job_id}: Failed to resize/reformat {original_filename}: {resize_err}. Sending original image."
                    )
                    # Fallback: Send original bytes if resizing fails
                    image_bytes_for_api = image_bytes
                    # We still need to determine the mime type for the original image
                    _, original_ext = os.path.splitext(original_filename)
                    mime_type_map = {
                        ".jpg": "image/jpeg",
                        ".jpeg": "image/jpeg",
                        ".png": "image/png",
                        ".webp": "image/webp",
                    }
                    mime_type_for_api = mime_type_map.get(
                        original_ext.lower(), "image/jpeg"
                    )  # Default if unknown

                # Process image with Gemini to get base filename (without extension)
                # Pass potentially resized bytes and appropriate mime type
                new_filename_base = await generate_filename_from_image(
                    model=gemini_model,
                    image_bytes=image_bytes_for_api,  # Use potentially resized bytes
                    filename=original_filename,  # Keep original filename for context in prompt
                    language_code=language_code,
                    mime_type=mime_type_for_api,  # Pass mime_type directly to avoid recalculation inside the function
                )

                # Get the original file extension and create the new full filename
                _, file_ext = os.path.splitext(original_filename)
                new_filename_with_ext = f"{new_filename_base}{file_ext.lower()}"

                # Construct the full destination path in GCS
                new_blob_name = f"{output_prefix}{new_filename_with_ext}"
                new_gcs_path = f"gs://{bucket_name}/{new_blob_name}"

                # Copy the blob directly in GCS
                logger.info(
                    f"Job {job_id}: Copying blob from {original_blob.name} to {new_blob_name}"
                )
                bucket.copy_blob(original_blob, bucket, new_blob_name)

                # Prepare result data with original and new GCS paths
                result_data = {
                    "original_gcs_path": original_gcs_path,
                    "new_gcs_path": new_gcs_path,
                    "old_filename": original_filename,
                    "new_filename": new_filename_with_ext,
                    "error": None,
                }

            except Exception as img_proc_error:
                logger.error(
                    f"Job {job_id}: Error processing {original_filename}: {img_proc_error}"
                )
                result_data = {
                    "original_gcs_path": original_gcs_path,
                    "new_gcs_path": None,
                    "old_filename": original_filename,
                    "new_filename": None,
                    "error": str(img_proc_error),
                }

            # Add to batch instead of updating immediately
            results_batch.append(result_data)
            processed_count += 1

            # Update Firestore when batch size is reached or all images processed
            if processed_count % batch_size == 0 or processed_count == total_images:
                logger.info(
                    f"Job {job_id}: Updating Firestore with batch of {len(results_batch)} results"
                )
                batch_update_data = {
                    "progress": processed_count,
                    "updated_at": firestore.SERVER_TIMESTAMP,
                }

                # Add results to update data by appending to the array
                await asyncio.to_thread(
                    job_ref.update,
                    {**batch_update_data, "results": firestore.ArrayUnion(results_batch)},
                )
                logger.debug(f"Job {job_id}: Updated progress to {processed_count}/{total_images}")

                # Clear batch after update
                results_batch = []

        # 6. Handle Success
        logger.info(
            f"Job {job_id}: Processing completed successfully. Updating status to 'completed'."
        )
        final_update = {"status": "completed", "updated_at": firestore.SERVER_TIMESTAMP}
        await asyncio.to_thread(job_ref.update, final_update)

    except Exception as e:
        # 7. Handle Errors
        logger.error(f"Job {job_id}: An error occurred during processing: {e}", exc_info=True)
        try:
            # If we have any unsaved results in the batch, save those too
            error_update = {
                "status": "failed",
                "error_message": str(e),
                "updated_at": firestore.SERVER_TIMESTAMP,
            }

            # Include any unsaved results in the final error update
            if results_batch:
                error_update["results"] = firestore.ArrayUnion(results_batch)
                error_update["progress"] = processed_count

            await asyncio.to_thread(job_ref.update, error_update)
            logger.info(f"Job {job_id}: Updated status to 'failed' in Firestore.")
        except Exception as firestore_e:
            logger.error(
                f"Job {job_id}: Critical error - failed to update Firestore status to 'failed': {firestore_e}"
            )

    finally:
        # 8. Cleanup
        if os.path.exists(temp_input_dir):
            try:
                shutil.rmtree(temp_input_dir)
                logger.info(
                    f"Job {job_id}: Successfully removed temporary directory: {temp_input_dir}"
                )
            except Exception as cleanup_e:
                logger.error(
                    f"Job {job_id}: Error cleaning up temporary directory {temp_input_dir}: {cleanup_e}"
                )
        logger.info(f"Background task finished for job {job_id}")


@router.post(
    "/process",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start image processing job via GCS path",
    description="Accepts a GCS path and language code, starts a background job "
    "to process images, and returns a job ID for progress tracking.",
)
async def process_images(request: ProcessRequest, background_tasks: BackgroundTasks):
    """
    Starts a background job to process images from a Google Cloud Storage bucket.

    - **gcs_input_path**: GCS path in format gs://bucket/prefix where images are stored
    - **language_code**: Target language code for filenames/alt-text (e.g., 'en', 'sl')
    - **user_id**: ID of the authenticated user making the request

    Returns the job ID immediately.
    """
    # Generate job ID immediately
    job_id = str(uuid.uuid4())

    # Do minimal checks before returning job_id
    # Get Firestore client
    db = get_firestore_client()
    if not db:
        logger.error("API Error: Firestore client not available.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not available. Cannot create job.",
        )

    # Check for model availability before queuing
    if not app_state.get("gemini_model"):
        logger.error("API Error: Gemini model not initialized.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI model not initialized. Cannot start job.",
        )

    # Define initial job data
    initial_data = {
        "gcs_path": request.gcs_input_path,
        "language_code": request.language_code,
        "user_id": request.user_id,
        "status": "pending",
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "total_images": 0,
        "progress": 0,
        "results": [],
        "error_message": None,
    }

    # Move Firestore document creation to the background task
    # Just set up the background task and return immediately
    background_tasks.add_task(
        setup_and_process_images_background,
        job_id=job_id,
        initial_data=initial_data,
        gcs_path=request.gcs_input_path,
        language_code=request.language_code,
    )

    logger.info(
        f"Created job ID: {job_id} for user: {request.user_id} - starting background processing"
    )

    # Return the job ID immediately
    return JobResponse(job_id=job_id)


# New function to setup the job and then process images
async def setup_and_process_images_background(
    job_id: str, initial_data: dict, gcs_path: str, language_code: str
):
    """First creates the Firestore document, then processes images in the background."""
    logger.info(f"Setting up background task for job {job_id}")

    db = get_firestore_client()
    if not db:
        logger.error(f"Job {job_id}: Firestore client not available. Cannot create job document.")
        return

    try:
        # Create the Firestore document
        job_ref = db.collection(settings.FIRESTORE_JOBS_COLLECTION).document(job_id)
        await asyncio.to_thread(job_ref.set, initial_data)
        logger.info(f"Created Firestore job document for job ID: {job_id}")

        # Now start the actual image processing
        await process_images_background(job_id, gcs_path, language_code)

    except Exception as e:
        logger.error(f"Failed to setup job {job_id}: {e}")
        # Try to update Firestore with the error if possible
        try:
            if db:
                job_ref = db.collection(settings.FIRESTORE_JOBS_COLLECTION).document(job_id)
                error_data = {
                    "status": "failed",
                    "error_message": f"Failed to setup job: {str(e)}",
                    "updated_at": firestore.SERVER_TIMESTAMP,
                }
                await asyncio.to_thread(job_ref.set, error_data, merge=True)
        except Exception as update_error:
            logger.error(f"Also failed to update error status for job {job_id}: {update_error}")
