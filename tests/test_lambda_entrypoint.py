"""
Integration tests for the Lambda entrypoint, using sample S3 events and mocking S3/DynamoDB interactions.
"""

import os
import json
import pytest
from logging import getLogger
from lambda_entrypoint import lambda_handler
from resources.responses.mock_ocr_response import mock_ocr_response
from resources.responses.mock_translation_response import mock_translation_response
from resources.responses.mock_html_response import mock_html_response

logger = getLogger("image-translator")


@pytest.mark.integration
@pytest.mark.parametrize(
    "event_file,expected_count",
    [
        ("sample_s3_event_single.json", 1),
        ("sample_s3_event_two.json", 2),
        ("sample_s3_event_multiple.json", 4),
        ("sample_s3_event_all.json", 4),
    ],
)
def test_lambda_entrypoint_with_sample_events(
    monkeypatch, tmp_path, event_file, expected_count
):
    """
    End-to-end test for the lambda entrypoint using sample S3 event JSON files.
    S3 download/upload is patched to use local files. DynamoDB status posting is mocked.
    """
    resources_dir = os.path.join(os.path.dirname(__file__), "resources")
    event_path = os.path.join(resources_dir, event_file)
    with open(event_path, "r") as f:
        s3_event = json.load(f)

    sqs_event = {
        "Records": [
            {"body": json.dumps({"Records": [record]})}
            for record in s3_event["Records"]
        ]
    }
    monkeypatch.setenv("UPLOADS_BUCKET", "uploads-bucket")

    async def fake_extract_s3_info_and_download(event):
        logger.info(f"Mock extract_s3_info_and_download: event={event}")
        records = event.get("Records", [])
        results = []
        for record in records:
            s3_info = record["s3"]
            key = s3_info["object"]["key"]
            parts = key.split("/")
            file_uuid = parts[1]
            target_language = parts[2]
            file_name = parts[3]
            download_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "data",
                "uploads",
                file_uuid,
                target_language,
                file_name,
            )
            results.append((download_path, file_uuid, target_language, file_name))
        return results

    async def fake_upload_translation_result_to_s3(
        result, file_uuid, original_file_name
    ):
        logger.info(
            f"Mock upload_translation_result_to_s3: result={result}, file_uuid={file_uuid}, original_file_name={original_file_name}"
        )
        base_name = os.path.splitext(original_file_name)[0]
        dest_dir = os.path.join(
            os.path.dirname(__file__), "..", "data", "results", file_uuid
        )
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, f"{base_name}_result.json")
        with open(dest_path, "w") as f:
            json.dump(result, f)

    async def fake_post_status_to_dynamodb(file_name, uuid, status):
        logger.info(
            f"Mock post_status_to_dynamodb: file_name={file_name}, uuid={uuid}, status={status}"
        )

    monkeypatch.setattr(
        "lambda_entrypoint.extract_s3_info_and_download",
        fake_extract_s3_info_and_download,
    )
    monkeypatch.setattr(
        "lambda_entrypoint.upload_translation_result_to_s3",
        fake_upload_translation_result_to_s3,
    )
    monkeypatch.setattr(
        "utils.utils.post_status_to_dynamodb", fake_post_status_to_dynamodb
    )

    monkeypatch.setattr(
        "pipeline.image_translator.MistralOCR.process_image",
        lambda self, base64_image, model: mock_ocr_response,
    )

    class MockModels:
        def generate_content(self, *args, **kwargs):
            prompt = None
            if args:
                prompt = args[0]
            elif "prompt" in kwargs:
                prompt = kwargs["prompt"]

            if prompt and (
                isinstance(prompt, str)
                and ("<html" in prompt or "html" in prompt.lower())
            ):
                return mock_html_response
            return mock_translation_response

    class MockClient:
        def __init__(self, *args, **kwargs):
            self.models = MockModels()

    monkeypatch.setattr("google.genai.Client", MockClient)
    monkeypatch.setattr(
        "pipeline.image_translator.post_status_to_dynamodb",
        fake_post_status_to_dynamodb,
    )

    logger.info(f"Testing event file: {event_file}")
    response = lambda_handler(sqs_event, {})
    logger.info(f"Lambda response: {response}")
    assert response["statusCode"] == 200
    assert "All files processed successfully" in response["body"]
    assert len(sqs_event["Records"]) == expected_count
