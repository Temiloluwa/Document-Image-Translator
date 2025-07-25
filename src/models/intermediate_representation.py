import re
import logging
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from bs4 import BeautifulSoup
from copy import deepcopy

logger = logging.getLogger("image-translator")


class BoundingBox(BaseModel):
    top_left_x: int
    top_left_y: int
    bottom_right_x: int
    bottom_right_y: int


class ImageRegion(BaseModel):
    id: str
    bounding_box: BoundingBox
    image_base64: str


class Metadata(BaseModel):
    model: str


class PageDimensions(BaseModel):
    dpi: Optional[int] = None
    height: int
    width: int


class PageText(BaseModel):
    markdown: str
    html: Optional[str] = None
    plain: Optional[str] = ""

    @field_validator("markdown")
    def markdown_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("PageText.markdown must not be empty.")
        return v


class Page(BaseModel):
    index: int
    page_text: PageText
    images: List[ImageRegion] = Field(default_factory=list)
    dimensions: Optional[PageDimensions] = None


class OcrResponse(BaseModel):
    pages: List[Page]
    metadata: Metadata = Field(default_factory=Metadata)


def parse_ocr_response(json_response: dict) -> OcrResponse:
    """
    Parses the OCR JSON response and returns an OcrResponse instance (using PageText for text).

    Args:
        json_response (dict): The OCR response as a dictionary.

    Returns:
        OcrResponse: Parsed OCR response object.
    """
    model = json_response.get("model")
    if not model or not str(model).strip():
        raise ValueError("Metadata.model is required and must not be empty.")
    metadata = Metadata(model=model)
    pages = []
    for page in json_response.get("pages", []):
        images = []
        for img in page.get("images", []):
            if "bounding_box" in img:
                bbox = img["bounding_box"]
                bounding_box = BoundingBox(**bbox)
            else:
                bounding_box = BoundingBox(
                    top_left_x=img.get("top_left_x"),
                    top_left_y=img.get("top_left_y"),
                    bottom_right_x=img.get("bottom_right_x"),
                    bottom_right_y=img.get("bottom_right_y"),
                )
            images.append(
                ImageRegion(
                    id=img["id"],
                    bounding_box=bounding_box,
                    image_base64=img["image_base64"],
                )
            )
        dimensions_dict = page.get("dimensions", {})
        dimensions = PageDimensions(**dimensions_dict) if dimensions_dict else None
        markdown_val = page.get("markdown") or page.get("value") or ""
        if not markdown_val or not str(markdown_val).strip():
            raise ValueError(
                f"PageText.markdown must not be empty for page index {page.get('index')}"
            )
        page_text = PageText(
            markdown=markdown_val,
            html=page.get("html", ""),
            plain=page.get("plain", ""),
        )
        pages.append(
            Page(
                index=page["index"],
                page_text=page_text,
                images=images,
                dimensions=dimensions,
            )
        )
    return OcrResponse(pages=pages, metadata=metadata)


def embed_base64_image_in_markdown(
    md_text: str, image_id: str, base64_data: str
) -> str:
    """
    Replace the image reference in markdown (e.g. ![img-0.jpeg](img-0.jpeg))
    with a markdown image embedding the base64 data URI.

    Args:
        md_text (str): Markdown text containing image references.
        image_id (str): The image identifier to replace.
        base64_data (str): The base64-encoded image data.

    Returns:
        str: Markdown text with embedded base64 image.
    """
    pattern = re.compile(r"!\[([^\]]*)\]\(" + re.escape(image_id) + r"\)")
    if not base64_data.startswith("data:"):
        base64_data = f"data:image/jpeg;base64,{base64_data}"
    replacement = f"![{image_id}]({base64_data})"
    return pattern.sub(replacement, md_text)


def embed_images_in_markdown(ocr_response: OcrResponse) -> None:
    """
    Accepts an OCR response (OcrResponse) and updates the markdown field of each page in place
    with embedded base64 images. Does not convert to dict or return a value.

    Args:
        ocr_response (OcrResponse): The OCR response to process.
    """
    for page in ocr_response.pages:
        md_text = page.page_text.markdown
        for img in page.images:
            img_id = img.id
            base64_data = img.image_base64
            if img_id and base64_data:
                # If the markdown contains a file extension, replace both with and without extension
                md_text = embed_base64_image_in_markdown(md_text, img_id, base64_data)
                # Also try replacing with .jpeg extension if not already present
                if not md_text.count(f"![{img_id}](data:image"):
                    md_text = embed_base64_image_in_markdown(
                        md_text, f"{img_id}.jpeg", base64_data
                    )
        page.page_text.markdown = md_text


def embed_base64_images_in_html(ocr_response: OcrResponse) -> None:
    """
    For each page in the OCR response, update the page_text.html field in place by embedding base64 images
    into <img> tags whose id attribute or src filename matches the image id in the IR.
    Raise a ValueError if the html field is empty or None.
    Uses BeautifulSoup for HTML manipulation instead of regex.
    """
    for page in ocr_response.pages:
        html = page.page_text.html or ""
        if not html.strip():
            raise ValueError(f"No HTML content found for page index {page.index}.")
        soup = BeautifulSoup(html, "html.parser")
        for img in page.images:
            img_id = img.id
            base64_data = img.image_base64
            if not base64_data:
                continue
            if not base64_data.startswith("data:"):
                base64_data = f"data:image/jpeg;base64,{base64_data}"

            img_tag = soup.find("img", id=img_id)
            if not img_tag and img_id.endswith(".jpeg"):
                img_tag = soup.find("img", id=img_id.replace(".jpeg", ""))

            if not img_tag:
                for tag in soup.find_all("img"):
                    src = tag.get("src", "")
                    if src and (img_id in src or img_id.replace(".jpeg", "") in src):
                        img_tag = tag
                        break
            if img_tag:
                img_tag["src"] = base64_data
        page.page_text.html = str(soup)


def get_image_dimensions_list_from_ir(ir_page) -> str:
    """
    Generate a string listing image IDs and their dimensions from an IR page for prompt injection.

    Args:
        ir_page: The IR page object containing images with bounding boxes.

    Returns:
        str: A newline-separated list of image_id: widthxheight px
    """
    image_dimensions = []
    for img in ir_page.images:
        if img.bounding_box:
            width = img.bounding_box.bottom_right_x - img.bounding_box.top_left_x
            height = img.bounding_box.bottom_right_y - img.bounding_box.top_left_y
            image_dimensions.append(f"{img.id}: {width}x{height} px")
    return "\n".join(image_dimensions)


def combine_pages_within_token_limit(
    ocr_response: OcrResponse,
    token_counter_fn,
    max_tokens: int,
    max_tokens_per_page: int = None,
) -> OcrResponse:
    """
    Combine pages into single IR, enforcing a max token limit per page.
    Returns an OcrResponse whose pages can be iterated with async for.
    """
    combined_pages = []
    page_idx = 0
    buf_md, buf_html, buf_plain, buf_imgs, buf_dims = [], [], [], [], []
    buf_tokens = 0

    def add_page(md, html, plain, imgs, dims):
        nonlocal page_idx
        combined_pages.append(
            Page(
                index=page_idx,
                page_text=PageText(markdown=md, html=html, plain=plain),
                images=deepcopy(imgs),
                dimensions=dims,
            )
        )
        logger.info(f"🧩 Added page {page_idx} | tokens: {token_counter_fn(md)}")
        page_idx += 1

    for page in ocr_response.pages:
        pt = page.page_text
        md = pt.markdown.strip()
        html = pt.html
        plain = pt.plain
        imgs = page.images
        dims = page.dimensions
        tokens = token_counter_fn(md)
        logger.info(f"📄 Page {page.index} | tokens: {tokens}")
        # If page itself exceeds max_tokens_per_page, split it into chunks
        if max_tokens_per_page and tokens > max_tokens_per_page:
            logger.warning(
                f"✂️ Page {page.index} exceeds max_tokens_per_page ({tokens} > {max_tokens_per_page}), chunking."
            )
            start = 0
            while start < len(md):
                chunk = md[start : start + max_tokens_per_page]
                add_page(chunk, html, plain, imgs, dims)
                start += max_tokens_per_page
            continue
        # If adding this page would exceed max_tokens_per_page, flush buffer first
        if max_tokens_per_page and (buf_tokens + tokens > max_tokens_per_page):
            if buf_md:
                add_page(
                    "\n\n".join(buf_md),
                    "\n\n".join(buf_html) if buf_html else None,
                    "\n\n".join(buf_plain) if buf_plain else None,
                    buf_imgs,
                    buf_dims[0] if buf_dims else None,
                )
            buf_md, buf_html, buf_plain, buf_imgs, buf_dims = [], [], [], [], []
            buf_tokens = 0
        # Add this page to buffer
        buf_md.append(md)
        buf_html.append(html.strip() if html else "")
        buf_plain.append(plain.strip() if plain else "")
        buf_imgs.extend(imgs)
        buf_dims.append(dims)
        buf_tokens += tokens
    # Flush any remaining buffer
    if buf_md:
        add_page(
            "\n\n".join(buf_md),
            "\n\n".join(buf_html) if buf_html else None,
            "\n\n".join(buf_plain) if buf_plain else None,
            buf_imgs,
            buf_dims[0] if buf_dims else None,
        )
    ocr_response_sync = deepcopy(ocr_response)
    ocr_response_sync.pages = combined_pages
    logger.info(
        f"✅ combine_pages_within_token_limit complete. Total pages: {len(combined_pages)}"
    )
    return ocr_response_sync
