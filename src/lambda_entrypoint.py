import json
from utils.utils import setup_logger
from pipeline.image_translator import translate_images
from pipeline.image_processor import process_input_image
from typing import Dict, Any


logger = setup_logger("image-translator", json_format=True)


def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    AWS Lambda function entry point for image translation.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The runtime information of the Lambda function.

    Returns:
        dict: The response containing the translation result or an error message.
    """
    try:
        image_paths = event.get("image_paths", [])
        target_language = event.get("target_language", "en")

        logger.info(f"Received {len(image_paths)} image(s) for processing.")
        images = [process_input_image(image_path) for image_path in image_paths]

        translation_result = translate_images(images, target_language)

        logger.info("Image translation completed successfully.")
        return {"statusCode": 200, "body": json.dumps(translation_result)}

    except Exception as e:
        logger.error("Error occurred during image translation.", exc_info=True)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
