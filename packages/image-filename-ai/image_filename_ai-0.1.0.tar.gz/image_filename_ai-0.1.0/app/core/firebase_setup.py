import logging
import os

import firebase_admin
from firebase_admin import credentials, firestore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_db = None


def initialize_firebase():
    """
    Initializes the Firebase Admin SDK using credentials from a service account file.
    Looks for the key file relative to the project root.
    """
    global _db

    # Prevent re-initialization
    if firebase_admin._apps:
        logger.info("Firebase Admin SDK already initialized.")
        if _db is None:  # Attempt to get client if initialized elsewhere but not stored here
            try:
                _db = firestore.client()  # Remove database_id parameter to use default database
                logger.info("Retrieved Firestore client from existing app.")
            except Exception as e:
                logger.error(f"Error retrieving Firestore client from existing app: {e}")
        return

    try:
        # First check for GOOGLE_APPLICATION_CREDENTIALS environment variable
        creds_env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if creds_env_path and os.path.exists(creds_env_path):
            logger.info(f"Using credentials from GOOGLE_APPLICATION_CREDENTIALS: {creds_env_path}")
            cred = credentials.Certificate(creds_env_path)
        else:
            # Fallback to serviceAccountKey.json in project root
            key_filename = "serviceAccountKey.json"
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            key_path = os.path.join(project_root, key_filename)

            if not os.path.exists(key_path):
                logger.error(f"Service account key file not found at: {key_path}")
                logger.error("Please either:")
                logger.error("1. Set GOOGLE_APPLICATION_CREDENTIALS environment variable, or")
                logger.error("2. Place serviceAccountKey.json in the project root")
                _db = None
                return

            logger.info(f"Using fallback credentials from: {key_path}")
            cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()  # Remove database_id parameter to use default database
        logger.info("Firebase Admin SDK initialized successfully.")

    except Exception as e:
        logger.error(f"Error initializing Firebase Admin SDK: {e}")
        _db = None


def get_firestore_client():
    """
    Returns the initialized Firestore client instance.

    Returns:
        firestore.Client | None: The Firestore client instance or None if initialization failed.
    """
    if _db is None:
        logger.warning("Attempted to get Firestore client, but it was not initialized.")
    return _db
