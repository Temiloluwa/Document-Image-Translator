"""
Unit tests for utility functions: image loading, S3/DynamoDB interactions, config loading, and error handling.
"""

import os
import tempfile
import base64
import json
import pytest
import aiofiles
import logging
from PIL import Image, UnidentifiedImageError
from utils import utils
import yaml
import uuid


logger = logging.getLogger("image-translator")


def test_load_image_from_file(monkeypatch):
    """
    Test loading an image from a file path. Should not attempt base64 decode if file exists.
    """
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img = Image.new("RGBA", (10, 10), color=(255, 0, 0, 128))
        img.save(tmp, format="PNG")
        tmp_path = tmp.name
    loaded_img = utils.load_image(tmp_path)
    assert isinstance(loaded_img, Image.Image)
    assert loaded_img.mode == "RGB"
    os.remove(tmp_path)


def test_load_image_from_base64(monkeypatch):
    """
    Test loading an image from a base64-encoded string.
    """
    # No external dependencies to mock here
    img = Image.new("RGBA", (10, 10), color=(0, 0, 255, 128))
    buf = tempfile.SpooledTemporaryFile()
    img.save(buf, format="PNG")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    loaded_img = utils.load_image(b64)
    assert isinstance(loaded_img, Image.Image)
    assert loaded_img.mode == "RGB"


def test_load_image_from_bytes(monkeypatch):
    """
    Test loading an image from bytes.
    """
    # No external dependencies to mock here
    img = Image.new("RGBA", (10, 10), color=(0, 255, 0, 128))
    buf = tempfile.SpooledTemporaryFile()
    img.save(buf, format="PNG")
    buf.seek(0)
    img_bytes = buf.read()
    loaded_img = utils.load_image(img_bytes)
    assert isinstance(loaded_img, Image.Image)
    assert loaded_img.mode == "RGB"


def test_load_image_invalid_type():
    with pytest.raises(ValueError):
        utils.load_image(123)


def test_read_json(tmp_path, monkeypatch):
    data = {"a": 1, "b": 2}
    file_path = tmp_path / "test.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data))
    result = utils.read_json(str(file_path))
    assert result == data


@pytest.mark.asyncio
async def test_download_file_from_s3(monkeypatch):
    # Mock aioboto3.Session
    class FakeS3:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def download_file(self, Bucket, Key, Filename):
            async with aiofiles.open(Filename, "w") as f:
                await f.write("dummy")

    class FakeSession:
        def client(self, service):
            return FakeS3()

    monkeypatch.setattr(utils.aioboto3, "Session", lambda: FakeSession())
    await utils.download_file_from_s3("bucket", "key", "path.txt")
    async with aiofiles.open("path.txt", "r") as f:
        content = await f.read()
    assert content == "dummy"
    os.remove("path.txt")


@pytest.mark.asyncio
async def test_upload_file_to_s3(monkeypatch, tmp_path):
    called = {}

    class FakeS3:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def upload_file(self, Filename, Bucket, Key):
            called["Filename"] = Filename
            called["Bucket"] = Bucket
            called["Key"] = Key

    class FakeSession:
        def client(self, service):
            return FakeS3()

    monkeypatch.setattr(utils.aioboto3, "Session", lambda: FakeSession())
    file_path = tmp_path / "file.txt"
    async with aiofiles.open(file_path, "w") as f:
        await f.write("data")
    await utils.upload_file_to_s3(str(file_path), "bucket", "key")
    assert called["Filename"] == str(file_path)
    assert called["Bucket"] == "bucket"
    assert called["Key"] == "key"


@pytest.mark.asyncio
async def test_extract_s3_info_and_download(monkeypatch, tmp_path):
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "bucket"},
                    "object": {
                        "key": "uploads/jan-01-24/1234abcd-en/target-lang/file.txt"
                    },
                }
            }
        ]
    }
    monkeypatch.setenv("UPLOADS_BUCKET", "bucket")

    async def fake_download_file_from_s3(bucket, key, path):
        async with aiofiles.open(path, "w") as f:
            await f.write("dummy")

    monkeypatch.setattr(utils, "download_file_from_s3", fake_download_file_from_s3)
    results = await utils.extract_s3_info_and_download(event)
    assert len(results) == 1
    download_path, date_prefix, uuid_str, target_language, file_name = results[0]
    assert date_prefix == "jan-01-24"
    assert uuid_str == "1234abcd-en"
    assert target_language == "target-lang"
    assert file_name == "file.txt"
    async with aiofiles.open(download_path, "r") as f:
        content = await f.read()
    assert content == "dummy"
    os.remove(download_path)


@pytest.mark.asyncio
async def test_extract_s3_info_and_download_multiple(monkeypatch, tmp_path):
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "bucket1"},
                    "object": {"key": "uploads/jan-01-24/uuid1/en/file1.txt"},
                }
            },
            {
                "s3": {
                    "bucket": {"name": "bucket2"},
                    "object": {"key": "uploads/jan-01-24/uuid2/fr/file2.txt"},
                }
            },
        ]
    }
    monkeypatch.setenv("UPLOADS_BUCKET", "bucket1")

    async def fake_download_file_from_s3(bucket, key, path):
        async with aiofiles.open(path, "w") as f:
            await f.write(bucket + key)

    monkeypatch.setattr(utils, "download_file_from_s3", fake_download_file_from_s3)
    results = await utils.extract_s3_info_and_download(event)
    assert len(results) == 1
    download_path, date_prefix, uuid_str, target_language, file_name = results[0]
    assert date_prefix == "jan-01-24"
    assert uuid_str == "uuid1"
    assert target_language == "en"
    assert file_name == "file1.txt"
    monkeypatch.setenv("UPLOADS_BUCKET", "bucket2")
    results = await utils.extract_s3_info_and_download(event)
    assert len(results) == 1
    download_path, date_prefix, uuid_str, target_language, file_name = results[0]
    assert date_prefix == "jan-01-24"
    assert uuid_str == "uuid2"
    assert target_language == "fr"
    assert file_name == "file2.txt"


@pytest.mark.asyncio
async def test_upload_translation_result_to_s3(monkeypatch, tmp_path):
    called = {}

    async def fake_upload_file_to_s3(file_path, bucket, key):
        called.setdefault("uploads", []).append((file_path, bucket, key))
        async with aiofiles.open(file_path, "r") as f:
            data = await f.read()
        if file_path.endswith(".md"):
            assert data == "test-markdown"
        elif file_path.endswith(".html"):
            assert data == "<html></html>"

    monkeypatch.setattr(utils, "upload_file_to_s3", fake_upload_file_to_s3)
    monkeypatch.setenv("RESULTS_BUCKET", "results-bucket")
    file_uuid = "testfile12"
    date_prefix = "jan-01-24"
    original_file_name = "myfile.png"
    mock_page_text = type(
        "PageText", (), {"markdown": "test-markdown", "html": "<html></html>"}
    )()
    mock_page = type("Page", (), {"page_text": mock_page_text})()
    mock_ocr_response = type("OcrResponse", (), {"pages": [mock_page]})()
    await utils.upload_translation_result_to_s3(
        mock_ocr_response, date_prefix, file_uuid, original_file_name
    )
    uploaded = called["uploads"]
    # The new format is myfile_png_result.md and myfile_png_result.html
    assert any(bucket == "results-bucket" for (_, bucket, _) in uploaded)
    assert any(key.endswith("myfile_png_result.md") for (_, _, key) in uploaded)
    assert any(key.endswith("myfile_png_result.html") for (_, _, key) in uploaded)


@pytest.mark.asyncio
async def test_post_status_to_dynamodb(monkeypatch):
    called = {}

    class FakeTable:
        async def put_item(self, Item):
            called["Item"] = Item

    class FakeDynamoDB:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def Table(self, table_name):
            return FakeTable()

    class FakeSession:
        def resource(self, service):
            return FakeDynamoDB()

    monkeypatch.setenv("STATUS_TABLE_NAME", "table")
    monkeypatch.setattr(utils.aioboto3, "Session", lambda: FakeSession())
    file_name = "file.png"
    uuid = "uuid123"
    status = {"progress": 50, "state": "processing", "uuid": uuid}
    await utils.post_status_to_dynamodb(file_name, status)
    assert called["Item"]["filename"] == file_name
    assert called["Item"]["status"]["uuid"] == uuid
    assert called["Item"]["status"]["progress"] == 50
    assert called["Item"]["status"]["state"] == "processing"


@pytest.mark.asyncio
async def test_post_status_to_dynamodb_env_missing(monkeypatch):
    monkeypatch.delenv("STATUS_TABLE_NAME", raising=False)
    with pytest.raises(RuntimeError):
        await utils.post_status_to_dynamodb(
            "file.png", {"progress": 0, "uuid": "uuid123"}
        )


@pytest.mark.asyncio
async def test_post_status_to_dynamodb_error(monkeypatch):
    class FakeTable:
        async def put_item(self, Item):
            raise Exception("fail")

    class FakeDynamoDB:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def Table(self, table_name):
            return FakeTable()

    class FakeSession:
        def resource(self, service):
            return FakeDynamoDB()

    monkeypatch.setenv("STATUS_TABLE_NAME", "table")
    monkeypatch.setattr(utils.aioboto3, "Session", lambda: FakeSession())
    with pytest.raises(RuntimeError):
        await utils.post_status_to_dynamodb(
            "file.png", {"progress": 0, "uuid": "uuid123"}
        )


def test_get_config_valid(tmp_path):
    yaml_content = """
image:
  max_size_kb: 100
  initial_quality: 90
"""
    config_path = tmp_path / "config.yaml"
    with open(config_path, "w") as f:
        f.write(yaml_content)
    config = utils.get_config(str(config_path))
    image_cfg = config["image"] if "image" in config else config.image
    assert image_cfg["max_size_kb"] == 100 or image_cfg.max_size_kb == 100
    assert image_cfg["initial_quality"] == 90 or image_cfg.initial_quality == 90


def test_get_config_invalid(tmp_path):
    config_path = tmp_path / "bad.yaml"
    with open(config_path, "w") as f:
        f.write(": bad yaml")
    with pytest.raises((yaml.YAMLError, Exception)):
        utils.get_config(str(config_path))


def test_get_config_file_not_found():
    random_path = f"/tmp/does_not_exist_config_{uuid.uuid4().hex}.yaml"
    assert not os.path.exists(random_path)
    with pytest.raises((FileNotFoundError, Exception)):
        utils.get_config(random_path)


def test_setup_logger_plain_and_json():
    logger_plain = utils.setup_logger("plain", json_format=False)
    logger_json = utils.setup_logger("json", json_format=True)
    assert logger_plain.name == "plain"
    assert logger_json.name == "json"
    assert logger_plain.handlers
    assert logger_json.handlers


def test_json_formatter():
    formatter = utils.JSONFormatter()
    record = logging.LogRecord("test", logging.INFO, "file", 1, "msg", (), None)
    output = formatter.format(record)
    assert "asctime" in output
    assert "levelname" in output
    assert "message" in output


def test_load_image_file_not_found():
    with pytest.raises((FileNotFoundError, UnidentifiedImageError)):
        utils.load_image("/tmp/does_not_exist.png")


def test_load_image_invalid_base64():
    with pytest.raises(Exception):
        utils.load_image("not_base64!!")


def test_load_image_ambiguous_string():
    """
    Test that a string that is neither a file nor valid base64 raises ValueError.
    """
    with pytest.raises(ValueError):
        utils.load_image("this_is_not_a_file_and_not_base64")


@pytest.mark.asyncio
async def test_download_file_from_s3_error(monkeypatch):
    class FakeS3:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def download_file(self, Bucket, Key, Filename):
            raise Exception("fail")

    class FakeSession:
        def client(self, service):
            return FakeS3()

    monkeypatch.setattr(utils.aioboto3, "Session", lambda: FakeSession())
    with pytest.raises(RuntimeError):
        await utils.download_file_from_s3("bucket", "key", "fail.txt")


@pytest.mark.asyncio
async def test_upload_file_to_s3_error(monkeypatch, tmp_path):
    class FakeS3:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def upload_file(self, Filename, Bucket, Key):
            raise Exception("fail")

    class FakeSession:
        def client(self, service):
            return FakeS3()

    monkeypatch.setattr(utils.aioboto3, "Session", lambda: FakeSession())
    file_path = tmp_path / "fail.txt"
    async with aiofiles.open(file_path, "w") as f:
        await f.write("fail")
    with pytest.raises(RuntimeError):
        await utils.upload_file_to_s3(str(file_path), "bucket", "key")


@pytest.mark.asyncio
async def test_upload_translation_result_to_s3_cleanup(monkeypatch, tmp_path):
    called = {}

    async def fake_upload_file_to_s3(file_path, bucket, key):
        called["file_path"] = file_path
        called["bucket"] = bucket
        called["key"] = key

    monkeypatch.setattr(utils, "upload_file_to_s3", fake_upload_file_to_s3)
    monkeypatch.setenv("RESULTS_BUCKET", "results-bucket")
