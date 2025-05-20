import base64
import io
import logging
import json
from omegaconf import DictConfig, ListConfig, OmegaConf
from PIL import Image
from pythonjsonlogger import jsonlogger
from typing import Dict, Any


def load_image(image_input: str | bytes) -> Image.Image:
    """
    Converts an image input (file path, base64 string, or bytes) to a PIL Image.

    Args:
        image_input: Union[str, bytes]
            - File path to the image
            - Base64 encoded string of the image
            - Bytes of the image

    Returns:
        PIL.Image.Image: The loaded image as a PIL Image object.
    """
    if isinstance(image_input, str):
        try:
            image_data = base64.b64decode(image_input)
            return Image.open(io.BytesIO(image_data))
        except (base64.binascii.Error, ValueError):  # type: ignore
            return Image.open(image_input)
    elif isinstance(image_input, bytes):
        return Image.open(io.BytesIO(image_input))
    else:
        raise ValueError(
            "Unsupported image input type. Must be file path, base64 string, or bytes."
        )


def read_json(file_path: str) -> Dict[str, Any]:
    """
    Reads a JSON file and returns its content as a dictionary.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Parsed content of the JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)  # type: ignore[no-any-return]


def get_config(config_path: str = "utils/config.yaml") -> DictConfig | ListConfig:
    """Reads a YAML file and returns its content as an OmegaConf object"""
    with open(config_path, "r", encoding="utf-8") as file:
        return OmegaConf.load(file)


class JSONFormatter(jsonlogger.JsonFormatter):  # type: ignore
    """
    Custom logging formatter to output logs in JSON format using python-json-logger.
    """

    def __init__(self) -> None:
        super().__init__(fmt="%(asctime)s %(name)s %(levelname)s %(message)s")


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

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # type: ignore
        )
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger
