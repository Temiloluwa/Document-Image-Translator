"""
This module provides AWS Lambda handlers for the document image translation API.
It supports generating presigned S3 URLs for uploads, recording upload status in DynamoDB,
and retrieving the status of uploaded files.
"""

# Standard library imports
import os
import re
import json
import logging
import datetime
from decimal import Decimal
from typing import Optional, Tuple, Dict, Any

# Third-party imports
import boto3
import ulid
from boto3.dynamodb.conditions import Key


# --- Logging Setup ---
def get_logger(name: str = "lambda_logger") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


logger = get_logger()


# --- AWS Resources ---
def get_s3_client():
    return boto3.client("s3")


def get_dynamodb_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(os.getenv("STATUS_TABLE_NAME"))


def get_uploads_bucket():
    return os.getenv("UPLOADS_BUCKET")


def get_results_bucket():
    return os.getenv("RESULTS_BUCKET")


s3 = get_s3_client()
table = get_dynamodb_table()
uploads_bucket = get_uploads_bucket()
results_bucket = get_results_bucket()


# --- Helper for reconstructing sanitized filename from S3 key ---
def reconstruct_sanitized_filename(base_name: str) -> str:
    """
    Given a base_name like 'deutschlandeditionpg9_png', reconstructs 'deutschlandeditionpg9.png'.
    Only splits on the last underscore and always returns name.ext (never appends .md/.html).
    """
    if "_" in base_name:
        parts = base_name.rsplit("_", 1)
        if len(parts) == 2:
            return f"{parts[0]}.{parts[1]}"
    return base_name


def convert_decimals(obj: Any) -> Any:
    """Recursively convert Decimal objects to float or int for JSON serialization."""
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    else:
        return obj


def sanitize_filename(filename: Optional[str]) -> str:
    """
    Remove non-alphanumeric characters from the name part of the file, but keep the extension.
    E.g. 'foo-bar 2024.pdf' -> 'foobar2024.pdf'
    """
    if not filename:
        logger.warning("sanitize_filename called with empty filename")
        return ""
    name, ext = os.path.splitext(filename)
    cleaned = re.sub(r"[^A-Za-z0-9]", "", name)
    ext = ext.lower()
    sanitized = cleaned + ext
    logger.debug(f"Sanitized filename: input={filename}, output={sanitized}")
    return sanitized


def query_status_items(
    filename: str, uuid: Optional[str] = None, require_complete: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Query DynamoDB for items by filename (partition key), optionally filter by uuid and state.
    If require_complete is True, only return items with status.state == 'complete'.
    Returns the first matching item or None.
    """
    filename = sanitize_filename(filename)
    logger.info(
        f"Querying DynamoDB for filename={filename}, uuid={uuid}, require_complete={require_complete}"
    )
    try:
        resp = table.query(
            KeyConditionExpression=Key("filename").eq(filename),
            ScanIndexForward=False,  # Most recent first
        )
        items = resp.get("Items", [])
        logger.debug(
            f"DynamoDB query returned {len(items)} items for filename={filename}"
        )
        item = None
        if uuid:
            for i in items:
                status = i.get("status", {})
                if status.get("uuid") == uuid:
                    if require_complete and status.get("state") != "complete":
                        continue
                    item = i
                    break
        else:
            item = items[0] if items else None
        logger.info(f"Query result: found item={item is not None}")
        return item
    except Exception as e:
        logger.error(f"DynamoDB exception: {e}")
        return None


def get_date_prefix() -> str:
    """Returns a date prefix like 'jan-04-24' using the current datetime."""
    now = datetime.datetime.now()
    return now.strftime("%b-%d-%y").lower()


def generate_result_locations(
    uuid_: str, filename: str, date_prefix: str
) -> Dict[str, str]:
    """Return S3 result locations for markdown and html for a given uuid and cleaned filename, with date prefix."""
    base_name = sanitize_filename(filename)
    name, ext = os.path.splitext(base_name)
    if not ext:
        raise Exception(
            f"generate_result_locations: filename must have an extension. Got: {filename}"
        )
    base_name_clean = f"{name}_{ext[1:]}"
    if not uuid_ or not base_name_clean or not date_prefix:
        raise Exception(
            f"generate_result_locations called with invalid uuid or filename: uuid={uuid_}, filename={filename}, date_prefix={date_prefix}"
        )

    key_md = f"results/{date_prefix}/{uuid_}/{base_name_clean}_result.md"
    key_html = f"results/{date_prefix}/{uuid_}/{base_name_clean}_result.html"
    logger.info(f"Result S3 keys: md={key_md}, html={key_html}")
    return {
        "markdown_results_location": key_md,
        "html_results_location": key_html,
    }


def extract_result_key_parts(
    location: str,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extract date_prefix, uuid, and base_name from a result S3 key location.
    location: results/{date-prefix}/{uuid}/{base_name}_result.(md|html)
    Returns (date_prefix, uuid, base_name)
    """
    try:
        parts = location.split("/")
        if len(parts) < 4:
            return None, None, None
        date_prefix = parts[1]
        uuid_ = parts[2]
        filename_with_ext = parts[3]
        if not (
            filename_with_ext.endswith(".md") or filename_with_ext.endswith(".html")
        ):
            return None, None, None
        base_name = filename_with_ext.rsplit("_result", 1)[0]
        return date_prefix, uuid_, base_name
    except Exception as e:
        logger.warning(f"Failed to extract key parts from location: {e}")
        return None, None, None


def generate_results_urls(location: str) -> Dict[str, str]:
    """
    Given a result S3 key location, return a presigned GET url valid for 10 minutes.
    Returns a dict with the url under the appropriate key.
    """
    if not location:
        return {}
    if location.endswith(".md"):
        url_key = "markdown_results_url"
    elif location.endswith(".html"):
        url_key = "html_results_url"
    else:
        url_key = "results_url"
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": results_bucket,
                "Key": location,
            },
            ExpiresIn=600,
        )
        return {url_key: url}
    except Exception as e:
        logger.error(f"Failed to generate presigned GET url for {location}: {e}")
        return {url_key: None}


def handle_presigned_url(query: Dict[str, str]) -> Dict[str, Any]:
    """
    Handle the /v1/presigned-url endpoint.

    Args:
        query (Dict[str, str]): Query parameters. Required keys:
            - filename (str): The name of the file to upload.
            - target_language (str): The target language for translation.

    Returns:
        Dict[str, Any]: API response with statusCode and body (JSON string). On success:
            {
                "upload_url": str,  # Presigned S3 upload URL
                "markdown_results_location": str,  # S3 key for markdown result
                "html_results_location": str      # S3 key for HTML result
            }
            On error, returns statusCode 400 or 500 and an error message.
    """
    filename = query.get("filename")
    target_lang = query.get("target_language")
    if not filename or not target_lang:
        logger.warning("Missing filename or target_language in presigned-url request")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "filename and target_language are required"}),
        }
    sanitized = sanitize_filename(filename)
    if not sanitized:
        logger.warning(
            f"Filename sanitization resulted in empty string: input={filename}"
        )
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid filename after sanitization"}),
        }
    file_uuid = str(ulid.ULID())
    # Generate presigned upload URL
    date_prefix = get_date_prefix()
    key = f"uploads/{date_prefix}/{file_uuid}/{target_lang}/{sanitized}"
    try:
        url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": uploads_bucket,
                "Key": key,
                "ContentType": "application/octet-stream",
            },
            ExpiresIn=600,
        )
    except Exception as e:
        logger.error(f"Error generating presigned upload URL: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"error": "Failed to generate presigned upload URL", "details": str(e)}
            ),
        }

    result_locations = generate_result_locations(file_uuid, sanitized, date_prefix)
    logger.info(
        f"Returning presigned upload URL and result locations for uuid={file_uuid}, filename={sanitized}"
    )
    return {
        "statusCode": 200,
        "body": json.dumps({"upload_url": url, **result_locations}),
    }


def handle_status(query: Dict[str, str]) -> Dict[str, Any]:
    """
    Handle the /v1/status endpoint.

    Args:
        query (Dict[str, str]): Query parameters. Must include exactly one of:
            - html_results_location (str): S3 key for HTML result file, or
            - markdown_results_location (str): S3 key for Markdown result file.
        The uuid and filename are extracted from the provided result location string.

    Returns:
        Dict[str, Any]: API response with statusCode and body (JSON string).
            - If processing is complete:
                {
                    "markdown_results_location": str,
                    "html_results_location": str
                }
            - If not complete: returns the DynamoDB item (status and metadata).
            - On error, returns statusCode 400/404 and an error message.
    """
    location = query.get("html_results_location") or query.get(
        "markdown_results_location"
    )
    if not location:
        logger.warning("Missing or invalid result location in status request")
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "error": "A valid html_results_location or markdown_results_location is required"
                }
            ),
        }
    date_prefix, uuid_, base_name = extract_result_key_parts(location)
    if not uuid_ or not base_name or not date_prefix:
        logger.warning("Could not extract key parts from result location")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid result location format"}),
        }
    sanitized_filename = reconstruct_sanitized_filename(base_name)
    logger.info(
        f"Checking status for uuid={uuid_}, filename={sanitized_filename}, date_prefix={date_prefix}"
    )
    # Example output for your log:
    logger.info(
        f"[EXAMPLE] extract_result_key_parts: {date_prefix}, {uuid_}, {base_name}"
    )
    logger.info(f"[EXAMPLE] reconstruct_sanitized_filename: {sanitized_filename}")
    item = query_status_items(sanitized_filename, uuid_)
    if not item:
        logger.info(
            f"No status item found for uuid={uuid_}, filename={sanitized_filename}"
        )
        return {"statusCode": 404, "body": json.dumps({"error": "Item not found"})}
    status = item.get("status", {})
    if status.get("state") == "complete":
        logger.info(
            f"Processing complete for uuid={uuid_}, filename={sanitized_filename}"
        )
        return {
            "statusCode": 200,
            "body": json.dumps(generate_results_urls(location)),
        }
    else:
        logger.info(
            f"Processing not complete for uuid={uuid_}, filename={sanitized_filename}, state={status.get('state')}"
        )
        return {"statusCode": 200, "body": json.dumps(convert_decimals(item))}


def handle_result(query: Dict[str, str]) -> Dict[str, Any]:
    """
    Handle the /v1/result endpoint.

    Args:
        query (Dict[str, str]): Query parameters. Must include exactly one of:
            - html_results_location (str): S3 key for HTML result file, or
            - markdown_results_location (str): S3 key for Markdown result file.
        The uuid and filename are extracted from the provided result location string.

    Returns:
        Dict[str, Any]: API response with statusCode and body (JSON string).
            - On success:
                {
                    "markdown_results_location": str,
                    "html_results_location": str
                }
            - On error, returns statusCode 400/404 and an error message.
    """
    location = query.get("html_results_location") or query.get(
        "markdown_results_location"
    )
    if not location:
        logger.warning("Missing or invalid result location in result request")
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "error": "A valid html_results_location or markdown_results_location is required"
                }
            ),
        }
    date_prefix, uuid_, base_name = extract_result_key_parts(location)
    if not uuid_ or not base_name or not date_prefix:
        logger.warning("Could not extract key parts from result location")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid result location format"}),
        }
    sanitized_filename = reconstruct_sanitized_filename(base_name)
    logger.info(
        f"Returning presigned result url for uuid={uuid_}, filename={sanitized_filename}, date_prefix={date_prefix}"
    )
    return {
        "statusCode": 200,
        "body": json.dumps(generate_results_urls(location)),
    }


def lambda_handler(event, context):
    """AWS Lambda handler for document image translation API."""
    path = event.get("path")
    method = event.get("httpMethod")
    query = event.get("queryStringParameters") or {}
    logger.info(f"Received request: path={path}, method={method}, query={query}")
    if path == "/v1/presigned-url" and method == "GET":
        return handle_presigned_url(query)
    elif path == "/v1/status" and method == "GET":
        return handle_status(query)
    elif path == "/v1/result" and method == "GET":
        return handle_result(query)
    logger.warning(f"Unknown path or method: path={path}, method={method}")
    return {"statusCode": 404, "body": json.dumps({"error": "Not Found"})}
