"""
Pytest fixtures for consistent test configuration and patching get_config.
"""

import pytest
from omegaconf import OmegaConf
from utils import utils
from pipeline import image_processor
from models.intermediate_representation import (
    OcrResponse,
    Page,
    PageText,
    ImageRegion,
    BoundingBox,
    Metadata,
    PageDimensions,
)


@pytest.fixture(autouse=True)
def patch_get_config(monkeypatch, request):
    """
    Automatically patch get_config for all tests except those starting with 'test_get_config'.
    """
    if request.node.name.startswith("test_get_config"):
        yield
        return
    config = OmegaConf.create({"image": {"max_size_kb": 400, "initial_quality": 95}})
    monkeypatch.setattr(utils, "get_config", lambda *args, **kwargs: config)
    monkeypatch.setattr(image_processor, "get_config", lambda *args, **kwargs: config)
    yield


@pytest.fixture(scope="module")
def real_sqs_event():
    return {
        "Records": [
            {
                "messageId": "650f65af-09d0-4211-8863-a048e2b14789",
                "receiptHandle": "AQEBqw9MA14cLOAojOtpParvdIsHuUoL0pYSoGR3TA6VLBiAi6X4pZhEviFecFJlXboAO6N5QKq4WmioXLhQgBTRFlrv0wRrQvN/YpS3Rrl9yIQ3sNEjPFJhba0bBpQ7RqJfFbaZWLlPCoSDKkVwfwGpMOQxgpsu5ZgrWrfBk/G4uulzaNPRoh5YmRFLUxsYLwR/VXmUlSR+nIXPrZ5VaiVQ2313JUA5Cfgd3gip+b9otHUKWQihRwvulW2oRdRa9FqDKj/VnWjeHj5F1H6+nwJlxzWYG9JQkSjZcp2qCEzbK0dTh0Ypecpsubp+Hr1PhYBcr1JsM0yrVt/ugSd5jrL4eyn3QkkRtDacMfjaLEvj41imhw/sV6gsZUa6NMTlcmNoY7sP/Dj9Ynly3sm5sfi76TXXQMgdnt5NnZ+UXDMgVGI=",
                "body": '{"Records":[{"eventVersion":"2.1","eventSource":"aws:s3","awsRegion":"us-east-1","eventTime":"2025-06-02T17:19:59.110Z","eventName":"ObjectCreated:Put","userIdentity":{"principalId":"AWS:AROATHQWQWN4YLAU3QZZG:temmie.adeoti"},"requestParameters":{"sourceIPAddress":"105.119.2.233"},"responseElements":{"x-amz-request-id":"Q2MS4QM2TZJWJBJW","x-amz-id-2":"o3oRY1+QqNdbuDXWLSLXyGsDPMxsozQMkxND4unSQCblAT1QvyOY881yB2is7BG5rkfm+9ocMnqFl38phn6UtlZ6FBL2YKAU"},"s3":{"s3SchemaVersion":"1.0","configurationId":"tf-s3-queue-20250531014704599200000001","bucket":{"name":"blc-image-translation-uploads","ownerIdentity":{"principalId":"A2V6RV36M4D3DG"},"arn":"arn:aws:s3:::blc-image-translation-uploads"},"object":{"key":"uploads/QuickScan_56467301_195971bd-684d-41ba-8e1e-a1234_20250308_180326_1_processed.jpg","size":120062,"eTag":"2763451ef0cc199d676acdd8cda23435","sequencer":"00683DDD3F0410D2E3"}}}]} ',
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1748884799609",
                    "SenderId": "AROA4R74ZO52XAB5OD7T4:S3-PROD-END",
                    "ApproximateFirstReceiveTimestamp": "1748884799626",
                },
                "messageAttributes": {},
                "md5OfBody": "bea17007ddde95def8bcb9dc5c34a299",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:222311789433:blc-image-translation-uploads-queue",
                "awsRegion": "us-east-1",
            }
        ]
    }


@pytest.fixture(scope="module")
def ocr_response():
    """
    Fixture to provide a mock OCR response object.
    """
    return OcrResponse(
        pages=[
            Page(
                index=0,
                page_text=PageText(
                    markdown="""# Sample OCR Document\n\nThis is a sample OCR markdown text with an embedded image below.\n\n![img-0](img-0.jpeg)\n\nSome more text after the image.""",
                    html="""<h1>Sample OCR Document</h1>\n<p>This is a sample OCR markdown text with an embedded image below.</p>\n<img id=\"img-0\" src=\"/9j/4AAQSkZJRgABAQEASABIAAD...\" width=\"100\" height=\"50\" />\n<p>Some more text after the image.</p>""",
                    plain="Sample OCR Document\n\nThis is a sample OCR markdown text with an embedded image below.\n[IMAGE: img-0]\nSome more text after the image.",
                ),
                images=[
                    ImageRegion(
                        id="img-0",
                        bounding_box=BoundingBox(
                            top_left_x=10,
                            top_left_y=20,
                            bottom_right_x=110,
                            bottom_right_y=70,
                        ),
                        image_base64="/9j/4AAQSkZJRgABAQEASABIAAD...",
                    )
                ],
                dimensions=PageDimensions(dpi=300, height=1000, width=800),
            )
        ],
        metadata=Metadata(model="test-ocr-model"),
    )
