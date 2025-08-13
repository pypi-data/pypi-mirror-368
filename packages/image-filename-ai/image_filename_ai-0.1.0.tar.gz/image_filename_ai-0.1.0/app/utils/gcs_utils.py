import logging
import os

from google.cloud import storage

logger = logging.getLogger(__name__)


def upload_directory_to_gcs(local_directory: str, gcs_destination_prefix: str):
    """Uploads all files from a local directory to a GCS prefix.

    Args:
        local_directory: Path to the local directory containing files to upload.
        gcs_destination_prefix: GCS path prefix (e.g., gs://your-bucket/your/folder/).
                                The bucket name is extracted from this.
    """
    try:
        storage_client = storage.Client()

        # Ensure prefix ends with a slash
        if not gcs_destination_prefix.endswith("/"):
            gcs_destination_prefix += "/"

        # Extract bucket name and directory path within the bucket
        if not gcs_destination_prefix.startswith("gs://"):
            raise ValueError("gcs_destination_prefix must start with gs://")

        path_parts = gcs_destination_prefix.replace("gs://", "").split("/", 1)
        bucket_name = path_parts[0]
        gcs_folder = path_parts[1] if len(path_parts) > 1 else ""

        bucket = storage_client.bucket(bucket_name)

        logger.info(f"Uploading files from '{local_directory}' to '{gcs_destination_prefix}'")

        # Walk through the local directory
        for local_root, _, filenames in os.walk(local_directory):
            for filename in filenames:
                local_path = os.path.join(local_root, filename)

                # Create the relative path for GCS
                relative_path = os.path.relpath(local_path, local_directory)
                # Construct the full GCS blob name
                blob_name = os.path.join(gcs_folder, relative_path).replace(
                    "\\", "/"
                )  # Ensure forward slashes

                blob = bucket.blob(blob_name)

                try:
                    blob.upload_from_filename(local_path)
                    logger.info(f"Uploaded '{local_path}' to 'gs://{bucket_name}/{blob_name}'")
                except Exception as upload_err:
                    logger.error(f"Failed to upload '{local_path}' to '{blob_name}': {upload_err}")

        logger.info("Upload complete.")

    except Exception as e:
        logger.error(f"An error occurred during GCS upload: {e}", exc_info=True)
        raise  # Re-raise after logging
