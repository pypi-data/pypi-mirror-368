import logging
from contextlib import asynccontextmanager

import vertexai
from fastapi import FastAPI
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel

from app.api.endpoints import image_processing
from app.core.config import settings
from app.core.firebase_setup import initialize_firebase  # Import Firebase initializer
from app.core.state import app_state  # Import app_state from the new module

# Global dictionary to store app state like the initialized model
# app_state = {} # Remove this line

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to initialize and clean up resources.
    Runs when the app starts and shuts down.
    """
    # Startup: Initialize Vertex AI
    try:
        aiplatform.init(project=settings.PROJECT_ID, location=settings.LOCATION)
        vertexai.init(project=settings.PROJECT_ID, location=settings.LOCATION)
        logger.info(
            f"Vertex AI SDK initialized for project {settings.PROJECT_ID} in {settings.LOCATION}"
        )

        # Initialize the Gemini model
        gemini_model = GenerativeModel(settings.MODEL_NAME)
        app_state["gemini_model"] = gemini_model
        logger.info(f"Successfully loaded model: {settings.MODEL_NAME}")

    except Exception as e:
        logger.error(f"Error initializing Vertex AI SDK or loading model: {e}")
        app_state["gemini_model"] = None

    # Startup: Initialize Firebase
    try:
        initialize_firebase()  # Call initializer
        # Logging of success/failure is handled within initialize_firebase
        logger.info("Attempted Firebase Admin SDK initialization.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Firebase initialization trigger: {e}")

    yield

    # Shutdown: Clean up resources if needed
    logger.info("Shutting down application and cleaning up resources...")
    app_state.clear()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include routers
app.include_router(image_processing.router, prefix=settings.API_PREFIX, tags=["Image Processing"])


@app.get("/", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API is running.
    Also indicates if the AI model is initialized properly.
    """
    model_status = "initialized" if app_state.get("gemini_model") else "not initialized"
    return {"status": "healthy", "api_version": settings.APP_VERSION, "model_status": model_status}
