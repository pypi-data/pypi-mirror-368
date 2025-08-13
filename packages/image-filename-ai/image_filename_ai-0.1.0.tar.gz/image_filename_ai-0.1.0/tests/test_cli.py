import csv
import json
from unittest.mock import MagicMock

import pytest

# We need to import the function we want to test
# This might require adding the project root to sys.path if running pytest directly
# or configuring pytest to recognize the project structure.
# For now, let's assume pytest runs from the root where `cli.py` is.
from cli import process_images  # Assuming we can import this directly


@pytest.fixture
def temp_dirs(tmp_path):
    """Create temporary input and output directories for testing."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()  # process_images will create subdirs
    return input_dir, output_dir


@pytest.fixture
def dummy_image(temp_dirs):
    """Create a dummy image file in the temporary input directory."""
    input_dir, _ = temp_dirs
    test_subdir = input_dir / "test"
    test_subdir.mkdir()
    image_path = test_subdir / "WhatsApp Image 2025-04-10 at 09.46.28.jpeg"
    image_path.touch()  # Create an empty file, content doesn't matter for this test
    return image_path, test_subdir


def test_process_images_success(temp_dirs, dummy_image, mocker):
    """Test the successful processing of a single image."""
    input_dir, output_dir = temp_dirs
    original_image_path, input_test_subdir = dummy_image
    language_code = "en"
    mock_model = MagicMock()  # Mock the Gemini Model object

    # Define the mock return value for the AI function
    mock_filename = "test-image-of-something"
    mock_alt_text = "Alt text for test image"
    mock_ai_result = {"filename": mock_filename, "alt_text": mock_alt_text}

    # Mock the generate_names_with_gemini function within the cli module
    # Use the correct path to where the function is *used* in cli.py
    mocker.patch("cli.generate_names_with_gemini", return_value=mock_ai_result)

    # Mock mimetypes.guess_type to avoid issues with the dummy file
    mocker.patch("cli.mimetypes.guess_type", return_value=("image/jpeg", None))

    # Run the function under test
    process_images(input_dir, output_dir, language_code, mock_model)

    # Assertions
    # 1. Original file should be gone
    assert not original_image_path.exists()

    # 2. New file should exist in the correct output subdirectory
    expected_output_subdir = output_dir / "test"
    expected_new_path = expected_output_subdir / f"{mock_filename}.jpeg"
    assert expected_new_path.exists()

    # 3. Log files should exist and contain the correct data
    expected_log_json_path = expected_output_subdir / "results.json"
    expected_log_csv_path = expected_output_subdir / "results.csv"

    assert expected_log_json_path.exists()
    assert expected_log_csv_path.exists()

    # Check JSON content
    with open(expected_log_json_path) as f:
        log_data = json.load(f)
        assert len(log_data) == 1
        entry = log_data[0]
        assert entry["original_path"] == str(original_image_path)  # Original path before move
        assert entry["new_path"] == str(expected_new_path)
        assert entry["alt_text"] == mock_alt_text

    # Check CSV content
    with open(expected_log_csv_path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == [
            "timestamp",
            "original_path",
            "new_path",
            "original_filename",
            "new_filename",
            "alt_text",
        ]
        rows = list(reader)
        assert len(rows) == 1
        row = rows[0]
        # Timestamp is tricky, just check other fields
        assert row[1] == str(original_image_path)  # original_path
        assert row[2] == str(expected_new_path)  # new_path
        assert row[3] == original_image_path.name  # original_filename
        assert row[4] == f"{mock_filename}.jpeg"  # new_filename
        assert row[5] == mock_alt_text  # alt_text
