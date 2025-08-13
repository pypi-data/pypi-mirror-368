import json
import time
from pathlib import Path

import vertexai.preview.generative_models as generative_models
from vertexai.generative_models import FinishReason, GenerativeModel, Part

from app.core.config import settings
from app.utils.file_utils import sanitize_filename


def generate_names_with_gemini(
    model: GenerativeModel,
    image_bytes: bytes,
    mime_type: str,
    language_code: str,
    original_filename: str = "",
):
    """
    Uses Vertex AI Gemini model to generate a filename and alt text for an image
    in the specified language.

    Args:
        model: The initialized Vertex AI GenerativeModel.
        image_bytes: The image data as bytes.
        mime_type: The MIME type of the image.
        language_code: The target language code (e.g., 'en', 'sl', 'de').
        original_filename: The original filename to use as fallback if generation fails.

    Returns:
        A dictionary containing 'filename' and 'alt_text', or None if generation fails completely.
    """
    print(f"Processing image with mime type: {mime_type} for language: {language_code}")
    fallback_stem = Path(original_filename).stem if original_filename else "image"

    retries = 0
    while retries < settings.MAX_RETRIES:
        try:
            # --- Actual Gemini API Call ---
            if not mime_type or not mime_type.startswith("image/"):
                print(f"Invalid image mime type: {mime_type}. Skipping.")
                return None

            image_part = Part.from_data(data=image_bytes, mime_type=mime_type)

            prompt = f"""Analyze this image. Provide the following in the language specified by the code '{language_code}':
1. A concise, SEO-friendly filename based on the main subject(s). Use 3-5 words, use hyphens for spaces, and do not include a file extension. Example (for English): 'golden-retriever-playing-fetch'.
2. Descriptive alt text for SEO purposes, clearly describing the image content in 1-2 sentences. Example (for English): 'A happy golden retriever dog catches a red ball in a sunny park.'

Format the output strictly as a valid JSON object with keys "filename" and "alt_text". Example (for English):
{{"filename": "your-seo-filename", "alt_text": "Your descriptive alt text."}}
"""
            # Configure generation to expect JSON
            generation_config = generative_models.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.3,  # Slightly lower temp for more predictable naming
            )

            response = model.generate_content(
                [image_part, prompt],
                generation_config=generation_config,
                # safety_settings=... # Optional safety settings can be passed here if needed
            )
            # --- End Actual Gemini API Call ---

            # --- Parse Gemini Response ---
            if not response.candidates or response.candidates[0].finish_reason != FinishReason.STOP:
                finish_reason = (
                    response.candidates[0].finish_reason.name if response.candidates else "UNKNOWN"
                )
                print(f"Warning: Gemini response finished with reason '{finish_reason}'.")
                if finish_reason == "SAFETY":
                    print("Skipping image due to safety block.")
                    return None
                raise ValueError(
                    f"Gemini response did not finish successfully (Reason: {finish_reason})"
                )

            response_text = response.text
            print(f"  Gemini Raw Response Text: {response_text[:200]}...")

            try:
                response_data = json.loads(response_text)
            except json.JSONDecodeError as json_err:
                print(
                    f"Error: Failed to decode JSON response from Gemini. Response: {response_text}"
                )
                print(f"  JSONDecodeError: {json_err}")
                raise ValueError("Invalid JSON response from Gemini") from json_err

            if "filename" in response_data and "alt_text" in response_data:
                sanitized = sanitize_filename(response_data["filename"])
                if not sanitized:
                    print("Warning: Gemini proposed an empty filename. Using original stem.")
                    sanitized = sanitize_filename(fallback_stem)

                print(f"  Suggested filename: {sanitized}")
                print(f"  Suggested alt text: {response_data['alt_text']}")
                return {"filename": sanitized, "alt_text": response_data["alt_text"]}
            else:
                print(
                    f"Error: Gemini response missing 'filename' or 'alt_text'. Response: {response_text}"
                )
                # Raise an error to trigger retry, as this might be a transient issue
                raise ValueError("Gemini response JSON missing required keys")

        except Exception as e:
            retries += 1
            print(f"Error calling Gemini API (Attempt {retries}/{settings.MAX_RETRIES}): {e}")
            if retries >= settings.MAX_RETRIES:
                print(f"Failed to process image after {settings.MAX_RETRIES} attempts.")
                return None  # Indicate failure
            print(f"Retrying in {settings.RETRY_DELAY} seconds...")
            time.sleep(settings.RETRY_DELAY)
    return None  # Should not be reached if retries loop works correctly
