"""
Unit tests for the image translation pipeline, including OCR, translation, and edge cases.
"""

from unittest.mock import patch, MagicMock, AsyncMock
from PIL import Image
from pipeline.image_translator import translate_image
import pytest


def create_test_image(mode="RGB", size=(100, 100), color=(255, 0, 0)):
    """Create a test image with the specified mode, size, and color."""
    img = Image.new(mode, size, color)
    return img


@patch("pipeline.image_translator.MistralOCR")
@patch("pipeline.image_translator.Gemini")
@patch("pipeline.image_translator.get_config")
@patch("pipeline.image_translator.Prompt")
@pytest.mark.asyncio
async def test_translate_image_success(
    mock_prompt, mock_get_config, mock_gemini, mock_mistral
):
    """Test successful image translation with mocked OCR and Gemini responses."""
    # Setup mocks
    mock_config = MagicMock()
    mock_config.ocr_model.id = "mistral-ocr-latest"
    mock_config.translator_model.id = "gemini-pro"
    mock_get_config.return_value = mock_config
    mock_prompt.get_system_translation_prompt.return_value = "system-prompt"
    mock_prompt.get_user_translation_prompt.return_value = "user-prompt"
    # Mock OCR response to return a valid JSON string
    mock_ocr_response = MagicMock()
    mock_ocr_response.json.return_value = '{"model": "mistral-ocr-latest", "pages": [{"index": 0, "markdown": "OCR_MARKDOWN"}]}'
    mock_mistral.return_value.process_image.return_value = mock_ocr_response
    # Mock Gemini response for translation and HTML (in order)
    mock_gemini_instance = MagicMock()
    mock_gemini_instance.generate = AsyncMock(
        side_effect=[
            MagicMock(contents=["TRANSLATED_TEXT"]),
            MagicMock(contents=["<html><body>TRANSLATED_HTML</body></html>"]),
        ]
    )
    mock_gemini.return_value = mock_gemini_instance

    img = create_test_image()
    result = await translate_image(img, "fr")
    # Check the returned OcrResponse object
    assert result.pages[0].page_text.markdown == "TRANSLATED_TEXT"
    assert result.pages[0].page_text.html is not None
    assert result.metadata.model == "mistral-ocr-latest"


@patch("pipeline.image_translator.MistralOCR")
@patch("pipeline.image_translator.Gemini")
@patch("pipeline.image_translator.get_config")
@patch("pipeline.image_translator.Prompt")
@pytest.mark.asyncio
async def test_translate_image_handles_missing_ocr_markdown(
    mock_prompt, mock_get_config, mock_gemini, mock_mistral
):
    """Test translation when OCR response page has no markdown attribute."""
    mock_config = MagicMock()
    mock_config.ocr_model.id = "mistral-ocr-latest"
    mock_config.translator_model.id = "gemini-pro"
    mock_get_config.return_value = mock_config
    mock_prompt.get_system_translation_prompt.return_value = "system-prompt"
    mock_prompt.get_user_translation_prompt.return_value = "user-prompt"
    # For missing markdown, return a JSON with empty markdown
    mock_ocr_response = MagicMock()
    mock_ocr_response.json.return_value = (
        '{"model": "mistral-ocr-latest", "pages": [{"index": 0, "markdown": ""}]}'
    )
    mock_mistral.return_value.process_image.return_value = mock_ocr_response
    mock_gemini_instance = MagicMock()
    mock_gemini_instance.generate = AsyncMock(
        return_value=MagicMock(contents=["TRANSLATED_TEXT"])
    )
    mock_gemini.return_value = mock_gemini_instance

    img = create_test_image()
    with pytest.raises(ValueError) as e:
        await translate_image(img, "de")
    assert "Failed to parse OCR response" in str(e.value)


@patch("pipeline.image_translator.MistralOCR")
@patch("pipeline.image_translator.Gemini")
@patch("pipeline.image_translator.get_config")
@patch("pipeline.image_translator.Prompt")
@pytest.mark.asyncio
async def test_translate_image_handles_empty_gemini_response(
    mock_prompt, mock_get_config, mock_gemini, mock_mistral
):
    """Test translation when Gemini returns an empty response."""
    mock_config = MagicMock()
    mock_config.ocr_model.id = "mistral-ocr-latest"
    mock_config.translator_model.id = "gemini-pro"
    mock_get_config.return_value = mock_config
    mock_prompt.get_system_translation_prompt.return_value = "system-prompt"
    mock_prompt.get_user_translation_prompt.return_value = "user-prompt"
    mock_ocr_response = MagicMock()
    mock_ocr_response.json.return_value = '{"model": "mistral-ocr-latest", "pages": [{"index": 0, "markdown": "OCR_MARKDOWN"}]}'
    mock_mistral.return_value.process_image.return_value = mock_ocr_response
    mock_gemini_instance = MagicMock()
    mock_gemini_instance.generate = AsyncMock(return_value=MagicMock(contents=[]))
    mock_gemini.return_value = mock_gemini_instance

    img = create_test_image()
    with pytest.raises(Exception) as e:
        await translate_image(img, "es")
    assert "Failed to parse LLM response for translation" in str(e.value)
