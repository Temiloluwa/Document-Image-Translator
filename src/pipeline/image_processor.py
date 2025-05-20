import io
from logging import getLogger

from PIL import Image, ImageEnhance
from utils.utils import load_image, get_config

logger = getLogger("image-translator")


def process_input_image(image: str | bytes) -> Image.Image:
    """
    Processes an input image by enhancing and compressing it.

    Args:
        image (str | bytes): The input image, either as a file path (str) or raw bytes.

    Returns:
        Image: The processed image as a PIL Image.
    """
    logger.info("Processing input image...")
    config = get_config().image

    pil_img = load_image(image)
    pil_img = pil_img.convert("RGB")
    pil_img = enhance_image(pil_img)
    pil_img = compress_image(pil_img, config.max_size_kb, config.initial_quality)

    return pil_img


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
    Enhances an image to improve OCR accuracy by increasing its contrast.

    Args:
        image (Image): The input image to be enhanced.

    Returns:
        Image: The enhanced image.
    """
    enhancer = ImageEnhance.Contrast(image)
    enhanced = enhancer.enhance(2.0)
    logger.info("Image contrast enhanced.")
    return enhanced
