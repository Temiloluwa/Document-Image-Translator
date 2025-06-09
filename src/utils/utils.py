"""
Utility functions for image loading, S3/DynamoDB interactions, config loading, and error handling.
"""

import base64
import io
import json
import logging
import os
from typing import Any, Dict, Union

import aioboto3
import aiofiles
from omegaconf import DictConfig, ListConfig, OmegaConf
from PIL import Image, UnidentifiedImageError
from pathlib import Path
from pythonjsonlogger import jsonlogger
from logging import getLogger

logger = getLogger("image-translator")


def load_image(image_input: Union[str, bytes]) -> Image.Image:
    """
    Converts an image input (file path, base64 string, or bytes) to a PIL Image in RGB mode.

    Args:
        image_input: Union[str, bytes]
            - File path to the image
            - Base64 encoded string of the image (optionally with data URI prefix)
            - Bytes of the image

    Returns:
        PIL.Image.Image: The loaded image as a PIL Image object in RGB mode.

    Raises:
        FileNotFoundError: If the file path does not exist.
        ValueError: If the input is not a valid image or base64 string.
    """
    if isinstance(image_input, str):
        if os.path.isfile(image_input):
            img = Image.open(image_input)
        elif os.path.exists(image_input) and os.path.isdir(image_input):
            raise FileNotFoundError(f"Path exists but is not a file: {image_input}")
        else:
            base64_str = image_input
            if base64_str.startswith("data:image"):
                try:
                    base64_str = base64_str.split(",", 1)[1]
                except IndexError:
                    raise ValueError("Malformed data URI for image.")
            try:
                image_data = base64.b64decode(base64_str)
                img = Image.open(io.BytesIO(image_data))
            except (
                base64.binascii.Error,
                ValueError,
                UnidentifiedImageError,
                OSError,
            ) as e:
                if os.path.sep in image_input or image_input.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".bmp", ".gif")
                ):
                    raise FileNotFoundError(f"File not found: {image_input}")
                raise ValueError(
                    "String input is neither a valid file path nor a valid base64-encoded image string."
                ) from e
    elif isinstance(image_input, bytes):
        try:
            img = Image.open(io.BytesIO(image_input))
        except (UnidentifiedImageError, OSError) as e:
            raise ValueError("Bytes input is not a valid image.") from e
    else:
        raise ValueError(
            "Unsupported image input type. Must be file path, base64 string, or bytes."
        )
    return img.convert("RGB")


def read_json(file_path: str) -> Dict[str, Any]:
    """
    Reads a JSON file and returns its content as a dictionary.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Parsed content of the JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_config(config_path: str = "utils/config.yaml") -> DictConfig | ListConfig:
    """
    Loads the configuration from a YAML file.

    Args:
        config_path (str): Path to the configuration YAML file.

    Returns:
        DictConfig | ListConfig: The loaded configuration.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as file:
        return OmegaConf.load(file)


def encode_image(image, format="JPEG"):
    """Encode a file path or PIL Image to base64 and detect its format."""
    from mimetypes import guess_type
    import io

    if isinstance(image, str):
        try:
            mime_type, _ = guess_type(image)
            if mime_type is None or not mime_type.startswith("image/"):
                logger.error(f"Error: The file {image} is not a valid image.")
                return None
            with open(image, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                return f"data:{mime_type};base64,{base64_image}"
        except FileNotFoundError:
            logger.error(f"Error: The file {image} was not found.")
            return None
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
    elif isinstance(image, Image.Image):
        buf = io.BytesIO()
        image.save(buf, format=format)
        base64_image = base64.b64encode(buf.getvalue()).decode("utf-8")
        mime_type = f"image/{format.lower()}"
        return f"data:{mime_type};base64,{base64_image}"
    else:
        raise ValueError("Input must be a file path or PIL Image.")


class JSONFormatter(jsonlogger.JsonFormatter):  # type: ignore
    """
    Custom logging formatter to output logs in JSON format using python-json-logger.
    """

    def __init__(self, fmt=None):
        # Default to including filename and uuid if not provided
        if fmt is None:
            fmt = "%(asctime)s %(name)s %(levelname)s %(message)s %(filename)s %(uuid)s"
        super().__init__(fmt=fmt)


class JobStatusFilter(logging.Filter):
    """
    Logging filter to add job status information (filename, uuid) to log records.
    """

    def __init__(self):
        super().__init__()
        self.filename = None
        self.uuid = None

    def filter(self, record):
        logger = logging.getLogger(record.name)
        record.filename = getattr(logger, "filename", self.filename)
        record.uuid = getattr(logger, "uuid", self.uuid)
        return True


def setup_logger(
    name: str, level: int = logging.INFO, json_format: bool = False
) -> logging.Logger:
    """
    Sets up a logger that streams logs to the console.

    Args:
        name (str): Name of the logger.
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG).
        json_format (bool): Whether to format logs as JSON.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    has_filter = any(isinstance(f, JobStatusFilter) for f in logger.filters)
    if not has_filter:
        logger.addFilter(JobStatusFilter())

    handler = logging.StreamHandler()
    handler.setLevel(level)
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(uuid)s - %(message)s"
        )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


async def download_file_from_s3(bucket: str, key: str, download_path: str) -> None:
    """
    Downloads a file from S3 to a local path asynchronously.

    Args:
        bucket (str): S3 bucket name.
        key (str): S3 object key.
        download_path (str): Local file path to save the downloaded file.
    """
    session = aioboto3.Session()
    async with session.client("s3") as s3:
        try:
            await s3.download_file(Bucket=bucket, Key=key, Filename=download_path)
        except Exception as e:
            raise RuntimeError(f"Failed to download {key} from {bucket}: {e}")


async def upload_file_to_s3(file_path: str, bucket: str, key: str) -> None:
    """
    Uploads a local file to S3 asynchronously.

    Args:
        file_path (str): Local file path to upload.
        bucket (str): S3 bucket name.
        key (str): S3 object key to save as.
    """
    session = aioboto3.Session()
    async with session.client("s3") as s3:
        try:
            await s3.upload_file(Filename=file_path, Bucket=bucket, Key=key)
        except Exception as e:
            raise RuntimeError(f"Failed to upload {file_path} to {bucket}/{key}: {e}")


async def extract_s3_info_and_download(event: dict) -> list[tuple[str, str, str, str]]:
    """
    Extracts S3 bucket, uuid, target language, and file name from all records in the event,
    downloads each file to a structured path: /tmp/<uuid>/<target-language>/<filename>.

    Returns:
        list[tuple[str, str, str, str]]: List of (download_path, uuid, target_language, file_name)
    """
    results = []
    records = event.get("Records", [])

    for record in records:
        try:
            s3_info = record["s3"]
            logger.info(f"Processing S3 record: {s3_info}")
            bucket = s3_info["bucket"]["name"]
            key = s3_info["object"]["key"]

            if bucket != os.getenv("UPLOADS_BUCKET"):
                logger.error(
                    f"Bucket name mismatch: {bucket} != {os.getenv('UPLOADS_BUCKET')}"
                )
                raise ValueError(
                    "Bucket name does not match UPLOADS_BUCKET environment variable."
                )

            logger.info(f"Extracted S3 key: {key}")
            parts = key.strip("/").split("/")

            # Check if key has correct structure: uploads/<uuid>/<language>/<filename>
            if len(parts) < 4 or parts[0] != "uploads":
                logger.warning(f"Skipping non-matching key: {key}")
                continue

            uuid_str = parts[1]
            target_language = parts[2]
            file_name = parts[3]

            logger.info(
                f"Extracted UUID: {uuid_str}, Target Language: {target_language}, File Name: {file_name}"
            )

            if not file_name or file_name.endswith("/"):
                logger.warning(f"Skipping directory-like key: {key}")
                continue

            download_dir = Path("/tmp") / uuid_str / target_language
            download_dir.mkdir(parents=True, exist_ok=True)
            download_path = str(download_dir / file_name)

            await download_file_from_s3(bucket, key, download_path)
            logger.info("Record download successful")

            results.append((download_path, uuid_str, target_language, file_name))

        except Exception as e:
            logger.error(f"Failed to process record: {e}")
            continue

    return results


async def upload_translation_result_to_s3(
    ocr_response, file_uuid: str, original_file_name: str
) -> None:
    """
    Uploads the translation result (markdown and HTML) to the S3 bucket specified by the RESULTS_BUCKET environment variable asynchronously.
    The results are stored under the prefix /results/<uuid>/<original_file_name>_result.md and _result.html

    Args:
        ocr_response (OcrResponse): The OCR IR object to upload.
        file_uuid (str): The unique ID for the translation job.
        original_file_name (str): The original file name of the uploaded file.
    """
    bucket = os.environ.get("RESULTS_BUCKET")
    if not bucket:
        raise RuntimeError("RESULTS_BUCKET environment variable is not set.")
    base_name = os.path.splitext(original_file_name)[0]
    key_md = f"results/{file_uuid}/{base_name}_result.md"
    key_html = f"results/{file_uuid}/{base_name}_result.html"
    tmp_md = f"/tmp/{base_name}_result.md"
    tmp_html = f"/tmp/{base_name}_result.html"
    try:
        markdown = ocr_response.pages[0].page_text.markdown
        html = ocr_response.pages[0].page_text.html
        async with aiofiles.open(tmp_md, mode="w") as f_md:
            await f_md.write(markdown)
        async with aiofiles.open(tmp_html, mode="w") as f_html:
            await f_html.write(html)
    except (OSError, IOError, Exception) as e:
        raise RuntimeError(f"Failed to write result files: {e}")
    try:
        await upload_file_to_s3(tmp_md, bucket, key_md)
        await upload_file_to_s3(tmp_html, bucket, key_html)
    finally:
        if os.path.exists(tmp_md):
            os.remove(tmp_md)
        if os.path.exists(tmp_html):
            os.remove(tmp_html)


async def post_status_to_dynamodb(file_name: str, uuid: str, status: dict) -> None:
    """
    Posts the status of a file processing job to DynamoDB.

    Args:
        file_name (str): The file name to use as the key in DynamoDB.
        uuid (str): The unique ID for the translation job.
        status (dict): The status information to store.

    Raises:
        RuntimeError: If there is an error posting to DynamoDB.
    """
    table_name = os.environ.get("STATUS_TABLE_NAME")
    if not table_name:
        raise RuntimeError("STATUS_TABLE_NAME environment variable is not set.")

    session = aioboto3.Session()
    async with session.resource("dynamodb") as dynamodb:
        try:
            table = await dynamodb.Table(table_name)
            item = {
                "filename": file_name,
                "uuid": uuid,
                "status": status,
            }
            await table.put_item(Item=item)
        except Exception as e:
            raise RuntimeError(f"Failed to post status to DynamoDB: {e}")


def normalize_event_to_s3_records(event: dict) -> dict:
    """
    Normalize an incoming Lambda event to a dict with a 'Records' key containing S3 records only.
    Handles both SQS-wrapped S3 events and direct S3 events.

    Args:
        event (dict): Lambda event payload, expected to contain SQS or S3 event records.

    Returns:
        dict: Normalized event with 'Records' key containing S3 records.
    """
    records = event.get("Records", [])
    if records and isinstance(records[0], dict) and "body" in records[0]:
        s3_records = []
        for record in records:
            try:
                body = record["body"]
                if isinstance(body, str):
                    body_json = json.loads(body)
                elif isinstance(body, dict):
                    body_json = body
                else:
                    continue
                s3s = body_json.get("Records", [])
                for s3_record in s3s:
                    if (
                        "s3" in s3_record
                        and "bucket" in s3_record["s3"]
                        and "object" in s3_record["s3"]
                    ):
                        s3_records.append(s3_record)
            except Exception:
                continue
        return {"Records": s3_records}
    elif not isinstance(event.get("Records"), list):
        return {"Records": []}
    filtered_records = [
        r
        for r in records
        if isinstance(r, dict)
        and "s3" in r
        and "bucket" in r["s3"]
        and "object" in r["s3"]
    ]
    return {"Records": filtered_records}
