import os
import base64
from logging import getLogger
from pypdf import PdfReader, PdfWriter
from typing import Optional
from utils.utils import get_config
from io import BytesIO

logger = getLogger("image-translator")


def process_input_pdf(pdf: str) -> str:
    """
    Processes an input PDF by compressing it according to config limits and encoding it to a base64 data URL.

    Args:
        pdf (str): The input PDF file path.

    Returns:
        str | None: The processed PDF encoded as a base64 data URL (data:application/pdf;base64,...), or None if no pages fit or an error occurs.
    """
    logger.info("Processing input PDF...")

    config = get_config().pdf
    max_size_kb = config.get("max_size_kb", 20_480)
    max_chars = config.get("max_chars", 750_000)

    # Check file size on disk before processing
    try:
        file_size_kb = os.path.getsize(pdf) / 1024
    except Exception as e:
        logger.error(f"Error accessing file size for {pdf}: {e}")
        raise
    if file_size_kb > max_size_kb:
        error_msg = f"PDF exceeds max size on disk ({file_size_kb:.2f} KB > {max_size_kb} KB) and cannot be processed."
        logger.error(error_msg)
        raise ValueError(error_msg)

    pdf_bytes = compress_pdf_by_text_limit(pdf, max_chars)
    if pdf_bytes is None:
        logger.error("No pages fit within the character limit.")
        return None

    result = encode_pdf(pdf_bytes)
    logger.info("PDF processing complete.")
    return result


def encode_pdf(pdf: str | bytes) -> str | None:
    """
    Encode a PDF file path or bytes to base64 data URL.

    Args:
        pdf (str | bytes): The input PDF file path or PDF bytes.

    Returns:
        str | None: The base64 data URL, or None if the file is not found or an error occurs.
    """
    try:
        if isinstance(pdf, str):
            with open(pdf, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
        elif isinstance(pdf, bytes):
            pdf_bytes = pdf
        else:
            raise ValueError("Input must be a file path or bytes.")
        base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        return f"data:application/pdf;base64,{base64_pdf}"
    except FileNotFoundError:
        logger.error(f"Error: The file {pdf} was not found.")
        return None
    except Exception as e:
        logger.error(f"Error: {e}")
        return None


def compress_pdf_by_text_limit(
    input_path: str, max_chars: int = 700_000
) -> Optional[bytes]:
    """
    Compress a PDF by keeping only the first N pages such that the combined text length
    is under a specified character limit. Output is PDF bytes with the reduced page set.

    Args:
        input_path (str): Path to the original PDF.
        max_chars (int): Max number of characters allowed in total.

    Returns:
        Optional[bytes]: PDF bytes, or None if no pages fit.
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    total_chars = 0
    kept_pages = 0

    for page in reader.pages:
        text = page.extract_text() or ""
        if total_chars + len(text) > max_chars:
            break
        writer.add_page(page)
        total_chars += len(text)
        kept_pages += 1

    if kept_pages == 0:
        return None  # No pages fit within the limit

    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()
