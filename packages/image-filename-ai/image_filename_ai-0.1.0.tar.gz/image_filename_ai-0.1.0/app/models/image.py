from pydantic import BaseModel, Field, field_validator


class ProcessRequest(BaseModel):
    """Request model for the image processing API."""

    gcs_input_path: str = Field(..., description="GCS path in format gs://bucket/prefix")
    language_code: str = Field(
        ..., min_length=2, max_length=5, description="Target language code (e.g., 'en', 'sl', 'de')"
    )
    user_id: str = Field(..., description="ID of the authenticated user making the request")
    gcs_output_path: str | None = Field(None, description="Optional GCS path for processed images")
    gcs_log_path: str | None = Field(None, description="Optional GCS path for logs")

    @field_validator("gcs_input_path", "gcs_output_path", "gcs_log_path")
    @classmethod
    def validate_gcs_path(cls, v: str | None):
        if v is not None and not v.startswith("gs://"):
            raise ValueError(f"GCS path must start with 'gs://': {v}")
        return v


class ImageResult(BaseModel):
    """Result for a single processed image."""

    original_gcs_uri: str
    status: str = Field(
        ...,
        description="'processed', 'skipped_unsupported', 'error_generation', 'error_gcs', 'processed_and_moved', 'error_moving'",
    )
    new_filename_stem: str | None = None
    new_filename: str | None = None
    alt_text: str | None = None
    final_gcs_uri: str | None = None
    error_message: str | None = None


class ProcessResponse(BaseModel):
    """Response model for the image processing API."""

    message: str
    processed_count: int = 0
    failed_or_skipped_count: int = 0
    results: list[ImageResult] = []
