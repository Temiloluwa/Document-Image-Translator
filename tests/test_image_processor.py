"""
Tests for the image_processor module, including enhance_image, compress_image, and process_input_image.
Covers:
- Enhancement effects and output type
- Compression effectiveness
- Input handling (file path, bytes)
- Output format
"""

import os
import tempfile
import numpy as np
from PIL import Image
import pytest
import io
from pipeline.image_processor import process_input_image, compress_image, enhance_image


def create_test_image(mode="RGB", size=(100, 100), color=(255, 0, 0)):
    """Create a simple test image of the given mode, size, and color."""
    img = Image.new(mode, size, color)
    return img


def test_enhance_image_runs_and_returns_image():
    """Test that enhance_image returns a PIL Image of the same size."""
    img = create_test_image()
    enhanced = enhance_image(img)
    assert isinstance(enhanced, Image.Image)
    assert enhanced.size == img.size


def test_enhance_image_changes_pixels():
    """Test that enhance_image actually changes pixel values."""
    img = create_test_image(color=(128, 128, 128))
    enhanced = enhance_image(img)
    orig_arr = np.array(img)
    enh_arr = np.array(enhanced)
    assert not np.array_equal(orig_arr, enh_arr)


def test_compress_image_reduces_and_respects_max_size():
    """Test that compress_image reduces file size and does not exceed max_size_kb."""
    img = create_test_image(size=(500, 500))
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        img.save(tmp, format="JPEG", quality=95)
        orig_size = os.path.getsize(tmp.name)
    max_size_kb = 10
    compressed = compress_image(img, max_size_kb=max_size_kb, initial_quality=95)
    buf = io.BytesIO()
    compressed.save(buf, format="JPEG")
    comp_size = len(buf.getvalue()) / 1024
    assert comp_size < orig_size
    assert comp_size <= max_size_kb, (
        f"Compressed image size {comp_size:.2f} KB exceeds max {max_size_kb} KB"
    )


def test_compress_image_raises_on_uncompressible_image():
    """Test that compress_image raises ValueError if image cannot be compressed below max_size_kb."""
    img = create_test_image(size=(500, 500), color=(0, 0, 0))
    with pytest.raises(
        ValueError, match="cannot be compressed below the specified size"
    ):
        compress_image(img, max_size_kb=0.1, initial_quality=10)


def test_process_input_image_accepts_pil_bytes():
    """Test that process_input_image accepts image bytes as input and returns a base64 data URL string."""
    img = create_test_image()
    buf = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img.save(buf, format="JPEG")
    buf.close()
    with open(buf.name, "rb") as f:
        img_bytes = f.read()
    processed = process_input_image(img_bytes)
    assert isinstance(processed, str)
    assert processed.startswith("data:image/")
    os.remove(buf.name)


def test_process_input_image_accepts_file_path(tmp_path):
    """Test that process_input_image accepts a file path as input and returns a base64 data URL string."""
    img = create_test_image()
    file_path = tmp_path / "test.jpg"
    img.save(file_path, format="JPEG")
    processed = process_input_image(str(file_path))
    assert isinstance(processed, str)
    assert processed.startswith("data:image/")


def test_process_input_image_output_is_jpeg():
    """Test that process_input_image output is a base64-encoded JPEG data URL string."""
    img = create_test_image()
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()
    processed = process_input_image(img_bytes)
    assert isinstance(processed, str)
    assert processed.startswith("data:image/jpeg;base64,")
