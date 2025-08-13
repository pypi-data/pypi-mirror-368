from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Vertex AI / Google Cloud Settings
    PROJECT_ID: str = "image-filename-ai"
    LOCATION: str = "us-central1"
    MODEL_NAME: str = "gemini-2.0-flash-exp"

    # File Processing Settings
    SUPPORTED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp"}

    # API Settings
    APP_NAME: str = "Image Filename AI API"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"

    # Retry Settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5  # seconds

    # Firestore Settings
    FIRESTORE_JOBS_COLLECTION: str = "imageProcessingJobs"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Create settings instance
settings = Settings()
