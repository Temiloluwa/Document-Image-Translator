"""
AWS Lambda entrypoint for document image translation pipeline.
Handles S3 event triggers, image processing, translation, and result upload.
"""

import json
import asyncio
from typing import Any, Dict, List, Tuple
from utils.utils import (
    setup_logger,
    extract_s3_info_and_download,
    upload_translation_result_to_s3,
    normalize_event_to_s3_records,
)
from pipeline.image_translator import translate_image
from pipeline.image_processor import process_input_image

logger = setup_logger("image-translator", json_format=True)


async def execute_image_translation(
    image: str,
    date_prefix: str,
    target_language: str,
    file_uuid: str,
    original_file_name: str,
) -> None:
    """
    Translate a processed image to the target language and upload the result to S3.
    Sets logger context for filename and uuid for traceability.

    Args:
        image: The processed image object.
        target_language (str): Target language for translation.
        file_uuid (str): Unique identifier for the file.
        original_file_name (str): Original file name from S3.
    """
    logger.filename = original_file_name
    logger.uuid = file_uuid
    logger.info(
        f"Translating image for file {original_file_name} (uuid={file_uuid}) to {target_language}"
    )
    translation_result = await translate_image(
        image, target_language, original_file_name, file_uuid
    )
    await upload_translation_result_to_s3(
        translation_result, date_prefix, file_uuid, original_file_name
    )
    logger.info(
        f"Translation and upload complete for file {original_file_name} (uuid={file_uuid})"
    )


async def lambda_handler_async(
    file_info_list: List[Tuple[str, str, str, str, str]], context: Any
) -> Dict[str, Any]:
    """
    Asynchronous Lambda handler for processing all files concurrently.
    Processes each file, translates, and uploads results. Logs context for each file.

    Args:
        file_info_list (list): List of (download_path, file_uuid, target_language, original_file_name) tuples.
        context: Lambda context object (unused).

    Returns:
        dict: Lambda response with statusCode and body (JSON-encoded results or error message).
    """
    try:
        processed = []
        for (
            download_path,
            date_prefix,
            file_uuid,
            target_language,
            original_file_name,
        ) in file_info_list:
            logger.filename = original_file_name
            logger.uuid = file_uuid
            logger.info(
                f"Processing file {original_file_name} (uuid={file_uuid}) for language {target_language}"
            )
            image = process_input_image(download_path)
            processed.append(
                (image, date_prefix, target_language, file_uuid, original_file_name)
            )
        tasks = [
            execute_image_translation(
                image, date_prefix, target_language, file_uuid, original_file_name
            )
            for image, date_prefix, target_language, file_uuid, original_file_name in processed
        ]
        await asyncio.gather(*tasks)
        logger.info("Image translation completed successfully for all files.")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "All files processed successfully."}),
        }
    except Exception as e:
        logger.error(f"Error occurred during image translation: {e}", exc_info=True)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entrypoint for document image translation.
    Handles both SQS-wrapped S3 events and direct S3 events.
    Extracts S3 file information from the event, downloads files, and invokes the async handler
    to process all files concurrently. This function is the synchronous entrypoint required by AWS Lambda.

    Args:
        event (dict): Lambda event payload, expected to contain SQS or S3 event records.
        context: Lambda context object.

    Returns:
        dict: Lambda response with statusCode and body (JSON-encoded results or error message).
    """
    logger.info(f"Lambda handler invoked with event: {event}")
    normalized_event = normalize_event_to_s3_records(event)
    file_info_list = asyncio.run(extract_s3_info_and_download(normalized_event))
    logger.info(f"Received event with {len(file_info_list)} files to process.")
    if not file_info_list:
        logger.error("No files available to process.")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "No files available to process."}),
        }
    return asyncio.run(lambda_handler_async(file_info_list, context))
