from logging import getLogger
from PIL import Image
from typing import List, Dict, Any

from utils.llm.gemini import Gemini
from utils.prompts import Prompt
from utils.utils import get_config
from models.intermediate_representation import DocumentTranslation


logger = getLogger("image-translator")


def translate_images(images: List[Image.Image], target_language: str) -> Dict[str, Any]:
    """
    Translates images using the Gemini LLM by first converting them to an IR.

    Args:
        images (List[Image]): List of images to process.
        custom_prompt (str, optional): Custom prompt to guide the translation. Defaults to None.

    Returns:
        Dict: The response from the Gemini LLM.
    """

    config = get_config().model
    logger.info("Initializing Gemini LLM...")
    gemini = Gemini(
        system_instruction=Prompt.get_system_prompt(),
        response_schema=DocumentTranslation,  # type: ignore[arg-type]
        **config,
    )
    logger.info("Starting image translation with Gemini...")
    response = gemini.generate(
        prompt=Prompt.get_user_prompt(target_language), images=images
    )

    logger.info("Image translation complete.")
    return response  # type: ignore[return-value]
