import io

from PIL import Image

# Pillow format mapping
FORMAT_MAP = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "avif": "AVIF",  # Requires pillow-avif-plugin or Pillow >= 9. AVIF support might vary.
}

# Default quality settings
DEFAULT_QUALITY = {
    "JPEG": 90,
    "WEBP": 90,
    "AVIF": 85,  # Adjust as needed
}


def process_image_data(
    image_bytes: bytes, target_format: str | None, max_width: int | None, original_mime_type: str
):
    """
    Resizes and/or converts the format of image data.

    Args:
        image_bytes: The raw image data.
        target_format: The desired output format ('jpg', 'png', 'webp', 'avif') or None to keep original.
        max_width: The maximum desired width in pixels, or None to keep original size.
        original_mime_type: The original MIME type of the image.

    Returns:
        A tuple (processed_bytes, output_extension) or (None, None) if processing fails.
        output_extension includes the leading dot (e.g., '.jpg').
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        original_format = img.format
        needs_resizing = max_width is not None and img.width > max_width
        needs_format_change = (
            target_format is not None and FORMAT_MAP.get(target_format.lower()) != original_format
        )

        # 1. Handle potential transparency issues if converting to JPEG
        output_pillow_format = original_format
        if target_format:
            target_pillow_format = FORMAT_MAP.get(target_format.lower())
            if not target_pillow_format:
                print(
                    f"Warning: Unsupported target format '{target_format}'. Keeping original format '{original_format}'."
                )
            else:
                output_pillow_format = target_pillow_format
                needs_format_change = output_pillow_format != original_format  # Re-evaluate

        if output_pillow_format == "JPEG" and img.mode in ("RGBA", "LA", "P"):
            # Convert to RGB if saving as JPEG, handling transparency
            print(f"Info: Converting image with mode '{img.mode}' to RGB for JPEG output.")
            # Create a white background image
            bg = Image.new("RGB", img.size, (255, 255, 255))
            try:
                # Paste the image onto the background using the alpha channel as a mask
                bg.paste(img, (0, 0), img.convert("RGBA").split()[-1])
                img = bg
            except Exception as paste_err:
                print(
                    f"Warning: Could not properly handle transparency for JPEG conversion: {paste_err}. Using simple RGB conversion."
                )
                img = img.convert("RGB")

        elif (
            img.mode == "P" and output_pillow_format != "PNG"
        ):  # Palette mode often needs conversion
            print("Info: Converting image with mode 'P' to RGB.")
            img = img.convert("RGB")

        # 2. Resize if necessary
        if needs_resizing:
            print(f"Info: Resizing image from {img.width}px wide to max {max_width}px.")
            aspect_ratio = img.height / img.width
            new_height = int(max_width * aspect_ratio)
            # Use LANCZOS for high-quality downsampling
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # 3. Save to buffer if changes were made
        if needs_resizing or needs_format_change:
            output_buffer = io.BytesIO()
            save_params = {}
            quality = DEFAULT_QUALITY.get(output_pillow_format)
            if quality:
                save_params["quality"] = quality
            if output_pillow_format == "PNG":
                save_params["optimize"] = True  # Add optimization for PNG
            # Handle AVIF specific parameters if needed in the future

            try:
                print(
                    f"DEBUG: Attempting to save image with mode '{img.mode}', format '{output_pillow_format}', params: {save_params}"
                )  # DEBUG print
                img.save(output_buffer, format=output_pillow_format, **save_params)
                processed_bytes = output_buffer.getvalue()
                print(
                    f"Info: Image processed. Format: {output_pillow_format}, Size: {len(processed_bytes)} bytes."
                )
            except OSError as save_err:
                # Handle Pillow errors like 'cannot write mode RGBA as AVIF'
                print("DEBUG: Caught OSError during save.")  # DEBUG print
                print(
                    f"Error saving image in format {output_pillow_format}: {save_err} (Type: {type(save_err)})"
                )  # Added type
                # Attempt fallback (e.g., save as PNG if AVIF failed?) - Optional
                # For now, signal failure:
                return None, None
            except ValueError as val_err:
                # Handle potential Pillow value errors during save
                print("DEBUG: Caught ValueError during save.")  # DEBUG print
                print(
                    f"Error during image save operation: {val_err} (Type: {type(val_err)})"
                )  # Added type
                return None, None

        else:
            # No changes needed, return original bytes
            print("Info: No resizing or format change needed.")
            processed_bytes = image_bytes
            output_pillow_format = original_format  # Ensure this is set correctly

        # Determine final extension
        output_extension = ".png"  # Default fallback
        for ext, fmt in FORMAT_MAP.items():
            if fmt == output_pillow_format:
                output_extension = f".{ext}"
                break  # Use first match (e.g., prefer .jpg over .jpeg)

        return processed_bytes, output_extension

    except ImportError:
        print("Error: Pillow library not found. Please install it (`pip install Pillow`)")
        return None, None
    except FileNotFoundError:  # Although we use BytesIO, Pillow might internally reference paths
        print("Error: Image data could not be processed (FileNotFound internally?).")
        return None, None
    except Exception as e:
        print("DEBUG: Caught unexpected exception in process_image_data.")  # DEBUG print
        print(
            f"Error processing image: {e} (Type: {type(e)}, Representation: {repr(e)})"
        )  # Added type and repr
        # Consider more specific error handling for Pillow exceptions if needed
        return None, None
