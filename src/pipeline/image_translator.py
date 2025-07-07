"""
Image translation pipeline: OCR, prompt construction, and LLM-based translation.
"""

import os
import json
from logging import getLogger
from models.status import Status
from utils.llm.gemini import Gemini
from utils.llm.mistral import MistralOCR
from utils.prompts import Prompt
from utils.utils import get_config, post_status_to_dynamodb
from models.intermediate_representation import (
    parse_ocr_response,
    embed_images_in_markdown,
    get_image_dimensions_list_from_ir,
    embed_base64_images_in_html,
    OcrResponse,
)

logger = getLogger("image-translator")


async def translate_image(
    image: str, target_language: str, file_name: str = None, uuid: str = None
) -> OcrResponse:
    """
        Perform OCR on the input image and translate the extracted text to the target language.
        Posts status updates to DynamoDB at key pipeline steps.

        Args:
            image (str): The input image (base64 or file path).
            target_language (str): The language to translate the text into.

        Returns:
    =     OcrResponse: The response containing translated text and images in markdown and HTML formats.
    """
    config = get_config(
        os.path.join(os.path.dirname(__file__), "..", "utils", "config.yaml")
    )

    logger.info(f"Translating image: {image}")

    if not file_name and not uuid:
        raise ValueError("File name and UUID must be provided to post status updates.")

    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid,
            state="started",
            progress=0,
            message="Starting translation pipeline",
        ).asdict(),
    )
    logger.info("Performing OCR...")
    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid, state="ocr_processing", progress=10, message="Performing OCR"
        ).asdict(),
    )
    ocr_response = MistralOCR().process_image(
        base64_image=image, model=config.ocr_model.id
    )
    try:
        response_ir = parse_ocr_response(json_response=json.loads(ocr_response.json()))
    except Exception as e:
        logger.error(f"Error parsing OCR response: {e}")
        await post_status_to_dynamodb(
            file_name,
            Status(
                uuid=uuid,
                state="error",
                progress=15,
                message=f"Error parsing OCR response: {e}",
            ).asdict(),
        )
        raise ValueError(
            "Failed to parse OCR response. Please check the input image or OCR model configuration."
        )
    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid, state="ocr_complete", progress=30, message="OCR complete"
        ).asdict(),
    )

    logger.info("Translating markdown with Gemini using template prompt...")
    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid, state="translating", progress=50, message="Translating markdown"
        ).asdict(),
    )
    translation_system_prompt = Prompt.get_system_translation_prompt()
    translation_user_prompt = Prompt.get_user_translation_prompt(
        response_ir.pages[0].page_text.markdown, target_language
    )
    translation_response = await Gemini(
        system_instruction=translation_system_prompt
    ).generate(
        prompt=translation_user_prompt,
        image=[],
        model=config.translator_model.id,
    )
    try:
        translated_markdown = translation_response.contents[0].strip()
    except Exception as e:
        logger.error(f"Error parsing translation LLM response: {e}")
        await post_status_to_dynamodb(
            file_name,
            Status(
                uuid=uuid,
                state="error",
                progress=60,
                message=f"Error parsing translation LLM response: {e}",
            ).asdict(),
        )
        raise ValueError("Failed to parse LLM response for translation.")
    response_ir.pages[0].page_text.markdown = translated_markdown
    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid,
            state="translation_complete",
            progress=70,
            message="Translation complete",
        ).asdict(),
    )

    logger.info("Generating HTML for translated markdown with Gemini...")
    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid, state="generating_html", progress=80, message="Generating HTML"
        ).asdict(),
    )
    image_dimensions_list = get_image_dimensions_list_from_ir(response_ir.pages[0])
    html_system_prompt = Prompt.get_system_markdown_to_html_prompt(
        image_dimensions_list
    )
    html_user_prompt = Prompt.get_user_markdown_to_html_prompt(translated_markdown)
    html_response = await Gemini(system_instruction=html_system_prompt).generate(
        prompt=html_user_prompt,
        image=[],
        model=config.translator_model.id,
    )
    try:
        translated_html = html_response.contents[0].strip("```html\n")
    except Exception as e:
        logger.error(f"Error parsing HTML LLM response: {e}")
        await post_status_to_dynamodb(
            file_name,
            Status(
                uuid=uuid,
                state="error",
                progress=90,
                message=f"Error parsing HTML LLM response: {e}",
            ).asdict(),
        )
        raise ValueError("Failed to parse LLM response for HTML conversion.")
    response_ir.pages[0].page_text.html = translated_html
    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid,
            state="html_complete",
            progress=95,
            message="HTML generation complete",
        ).asdict(),
    )

    logger.info("Embedding images in markdown and HTML...")
    embed_images_in_markdown(response_ir)
    embed_base64_images_in_html(response_ir)

    logger.info("Image translation complete.")
    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid, state="complete", progress=100, message="Pipeline complete"
        ).asdict(),
    )
    return response_ir
