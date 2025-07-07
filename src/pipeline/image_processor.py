"""
Image processing utilities: enhancement, compression, and input normalization for translation pipeline.
"""

import io
import base64
from logging import getLogger

from PIL import Image, ImageEnhance
from utils.utils import load_image, get_config

logger = getLogger("image-translator")


def process_input_image(image: str | bytes) -> str:
    """
    Processes an input image by enhancing and compressing it, then encodes it to a base64 data URL.

    Args:
        image (str | bytes): The input image, either as a file path (str) or raw bytes.

    Returns:
        str: The processed image encoded as a base64 data URL (data:image/jpeg;base64,...).
    """
    logger.info("Processing input image...")
    config = get_config().image

    pil_img = load_image(image)
    pil_img = enhance_image(pil_img)
    pil_img = compress_image(pil_img, config.max_size_kb, config.initial_quality)
    logger.info("Image processing complete.")

    return encode_image(pil_img)


def compress_image(
    image: Image.Image, max_size_kb: int = 400, initial_quality: int = 95
) -> Image.Image:
    """
    Compresses an image to ensure it is not larger than the specified size.

    Args:
        image (Image): The image to be compressed.
        max_size_kb (int, optional): The maximum allowed size of the image in kilobytes.
        initial_quality (int, optional): The starting quality for compression.

    Returns:
        Image: The compressed image.

    Raises:
        ValueError: If the image cannot be compressed below the specified size.
    """
    buffer = io.BytesIO()
    quality = initial_quality

    while True:
        buffer.seek(0)
        buffer.truncate()
        image.save(buffer, format="JPEG", quality=quality)
        size_kb = len(buffer.getvalue()) / 1024
        logger.info(f"Image size: {size_kb:.2f} KB, Quality: {quality}")

        if size_kb <= max_size_kb or quality <= 10:
            break

        quality -= 5

    if quality <= 10 and size_kb > max_size_kb:
        logger.error(
            f"Could not compress below {max_size_kb} KB (final: {size_kb:.2f} KB)"
        )
        raise ValueError("Image cannot be compressed below the specified size.")

    buffer.seek(0)
    return Image.open(buffer)


def enhance_image(image: Image.Image) -> Image.Image:
    """
    Enhances the image by adjusting contrast, brightness, sharpness, and color balance.

    Args:
        image (Image): The image to be enhanced.

    Returns:
        Image: The enhanced image.
    """
    # Apply only light contrast and brightness adjustments
    image = ImageEnhance.Contrast(image).enhance(1.05)
    image = ImageEnhance.Brightness(image).enhance(1.05)
    logger.info("Image enhanced: light contrast and brightness applied.")
    return image


def encode_image(image: str | Image.Image, format: str = "JPEG") -> str | None:
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
