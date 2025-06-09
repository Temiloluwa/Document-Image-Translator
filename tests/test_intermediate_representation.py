"""
Unit tests for models and functions in intermediate_representation.py.
Covers: BoundingBox, ImageRegion, Metadata, PageDimensions, PageText, Page, OcrResponse,
parse_ocr_response, embed_base64_image_in_markdown, embed_images_in_markdown,
embed_base64_images_in_html, get_image_dimensions_list_from_ir.
"""

import pytest
from models.intermediate_representation import (
    BoundingBox,
    ImageRegion,
    Metadata,
    PageDimensions,
    PageText,
    Page,
    OcrResponse,
    parse_ocr_response,
    embed_base64_image_in_markdown,
    embed_images_in_markdown,
    embed_base64_images_in_html,
    get_image_dimensions_list_from_ir,
)


def test_bounding_box_model():
    """Test BoundingBox model fields."""
    bbox = BoundingBox(top_left_x=1, top_left_y=2, bottom_right_x=3, bottom_right_y=4)
    assert bbox.top_left_x == 1
    assert bbox.top_left_y == 2
    assert bbox.bottom_right_x == 3
    assert bbox.bottom_right_y == 4


def test_image_region_model():
    """Test ImageRegion model fields."""
    bbox = BoundingBox(top_left_x=0, top_left_y=0, bottom_right_x=10, bottom_right_y=10)
    img = ImageRegion(id="img-1", bounding_box=bbox, image_base64="abc123")
    assert img.id == "img-1"
    assert img.bounding_box == bbox
    assert img.image_base64 == "abc123"


def test_metadata_model():
    """Test Metadata model field."""
    meta = Metadata(model="ocr-model")
    assert meta.model == "ocr-model"


def test_page_dimensions_model():
    """Test PageDimensions model fields and optional dpi."""
    dims = PageDimensions(dpi=300, height=1000, width=800)
    assert dims.dpi == 300
    assert dims.height == 1000
    assert dims.width == 800
    dims2 = PageDimensions(height=500, width=400)
    assert dims2.dpi is None


def test_page_text_model_valid():
    """Test PageText model with valid markdown."""
    pt = PageText(markdown="abc", html="<b>abc</b>", plain="plain")
    assert pt.markdown == "abc"
    assert pt.html == "<b>abc</b>"
    assert pt.plain == "plain"


def test_page_text_model_empty_markdown():
    """Test PageText model raises on empty markdown."""
    with pytest.raises(ValueError):
        PageText(markdown="   ")


def test_page_model():
    """Test Page model fields."""
    pt = PageText(markdown="# Title")
    img = ImageRegion(
        id="img-1",
        bounding_box=BoundingBox(
            top_left_x=0, top_left_y=0, bottom_right_x=10, bottom_right_y=10
        ),
        image_base64="abc",
    )
    dims = PageDimensions(height=100, width=200)
    page = Page(index=0, page_text=pt, images=[img], dimensions=dims)
    assert page.index == 0
    assert page.page_text == pt
    assert page.images == [img]
    assert page.dimensions == dims


def test_ocr_response_model():
    """Test OcrResponse model fields."""
    pt = PageText(markdown="abc")
    page = Page(index=0, page_text=pt)
    meta = Metadata(model="m")
    ocr = OcrResponse(pages=[page], metadata=meta)
    assert ocr.pages == [page]
    assert ocr.metadata == meta


def test_parse_ocr_response_valid():
    """Test parse_ocr_response with valid input."""
    data = {
        "model": "ocr-model",
        "pages": [
            {
                "index": 0,
                "markdown": "# Title\n\n![img-1](img-1)",
                "html": "<h1>Title</h1><img id='img-1' src='abc' />",
                "plain": "plain text",
                "images": [
                    {
                        "id": "img-1",
                        "bounding_box": {
                            "top_left_x": 1,
                            "top_left_y": 2,
                            "bottom_right_x": 3,
                            "bottom_right_y": 4,
                        },
                        "image_base64": "abc",
                    }
                ],
                "dimensions": {"dpi": 300, "height": 100, "width": 200},
            }
        ],
    }
    ocr = parse_ocr_response(data)
    assert ocr.metadata.model == "ocr-model"
    assert len(ocr.pages) == 1
    page = ocr.pages[0]
    assert page.index == 0
    assert page.page_text.markdown.startswith("# Title")
    assert page.images[0].id == "img-1"
    assert page.images[0].bounding_box.top_left_x == 1
    assert page.dimensions.dpi == 300


def test_parse_ocr_response_missing_model():
    """Test parse_ocr_response raises if model missing."""
    data = {"pages": []}
    with pytest.raises(ValueError):
        parse_ocr_response(data)


def test_parse_ocr_response_empty_markdown():
    """Test parse_ocr_response raises if markdown is empty."""
    data = {"model": "m", "pages": [{"index": 0, "markdown": "   ", "images": []}]}
    with pytest.raises(ValueError):
        parse_ocr_response(data)


def test_embed_base64_image_in_markdown_replaces():
    """Test embed_base64_image_in_markdown replaces image ref with base64 URI."""
    md = "# Title\n\n![img-1](img-1)"
    result = embed_base64_image_in_markdown(md, "img-1", "abc123")
    assert "data:image/jpeg;base64,abc123" in result
    assert result.count("![img-1](data:image/jpeg;base64,abc123)") == 1


def test_embed_base64_image_in_markdown_with_data_uri():
    """Test embed_base64_image_in_markdown does not double-wrap data URI."""
    md = "![img-1](img-1)"
    result = embed_base64_image_in_markdown(md, "img-1", "data:image/png;base64,zzz")
    assert result.count("![img-1](data:image/png;base64,zzz)") == 1


def test_embed_images_in_markdown_mutates(ocr_response):
    """Test embed_images_in_markdown mutates markdown in-place for base64 embedding."""
    orig = ocr_response.pages[0].page_text.markdown
    embed_images_in_markdown(ocr_response)
    assert "data:image/jpeg;base64," in ocr_response.pages[0].page_text.markdown
    assert orig != ocr_response.pages[0].page_text.markdown


def test_embed_images_in_markdown_no_images():
    """Test embed_images_in_markdown does nothing if no images."""
    pt = PageText(markdown="# Title")
    page = Page(index=0, page_text=pt, images=[])
    ocr = OcrResponse(pages=[page], metadata=Metadata(model="m"))
    embed_images_in_markdown(ocr)
    assert ocr.pages[0].page_text.markdown == "# Title"


def test_embed_base64_images_in_html_mutates(ocr_response):
    """Test embed_base64_images_in_html mutates html in-place for base64 embedding."""
    orig = ocr_response.pages[0].page_text.html
    embed_base64_images_in_html(ocr_response)
    assert "data:image/jpeg;base64," in ocr_response.pages[0].page_text.html
    assert orig != ocr_response.pages[0].page_text.html


def test_embed_base64_images_in_html_empty_html():
    """Test embed_base64_images_in_html raises if html is empty."""
    pt = PageText(markdown="# T", html="   ")
    page = Page(index=0, page_text=pt, images=[])
    ocr = OcrResponse(pages=[page], metadata=Metadata(model="m"))
    with pytest.raises(ValueError):
        embed_base64_images_in_html(ocr)


def test_embed_base64_images_in_html_no_images():
    """Test embed_base64_images_in_html does nothing if no images."""
    pt = PageText(markdown="# T", html="<h1>H</h1>")
    page = Page(index=0, page_text=pt, images=[])
    ocr = OcrResponse(pages=[page], metadata=Metadata(model="m"))
    embed_base64_images_in_html(ocr)
    assert ocr.pages[0].page_text.html == "<h1>H</h1>"


def test_get_image_dimensions_list_from_ir(ocr_response):
    """Test get_image_dimensions_list_from_ir returns correct string."""
    dims = get_image_dimensions_list_from_ir(ocr_response.pages[0])
    assert "img-0: 100x50 px" in dims


def test_get_image_dimensions_list_from_ir_no_images():
    """Test get_image_dimensions_list_from_ir returns empty string if no images."""
    pt = PageText(markdown="# T")
    page = Page(index=0, page_text=pt, images=[])
    assert get_image_dimensions_list_from_ir(page) == ""


def test_embed_base64_image_in_markdown_no_match():
    """Test embed_base64_image_in_markdown does nothing if image_id not present."""
    md = "# Title\n\n![img-2](img-2)"
    result = embed_base64_image_in_markdown(md, "img-1", "abc123")
    assert result == md


def test_embed_images_in_markdown_multiple_images():
    """Test embed_images_in_markdown with multiple images on a page."""
    pt = PageText(markdown="# Title\n\n![img-1](img-1)\n![img-2](img-2)")
    img1 = ImageRegion(
        id="img-1",
        bounding_box=BoundingBox(
            top_left_x=0, top_left_y=0, bottom_right_x=10, bottom_right_y=10
        ),
        image_base64="abc",
    )
    img2 = ImageRegion(
        id="img-2",
        bounding_box=BoundingBox(
            top_left_x=1, top_left_y=1, bottom_right_x=11, bottom_right_y=11
        ),
        image_base64="def",
    )
    page = Page(index=0, page_text=pt, images=[img1, img2])
    ocr = OcrResponse(pages=[page], metadata=Metadata(model="m"))
    embed_images_in_markdown(ocr)
    assert "data:image/jpeg;base64,abc" in ocr.pages[0].page_text.markdown
    assert "data:image/jpeg;base64,def" in ocr.pages[0].page_text.markdown


def test_embed_base64_images_in_html_multiple_images():
    """Test embed_base64_images_in_html with multiple images on a page."""
    pt = PageText(
        markdown="# T", html='<img id="img-1" src="foo" /><img id="img-2" src="bar" />'
    )
    img1 = ImageRegion(
        id="img-1",
        bounding_box=BoundingBox(
            top_left_x=0, top_left_y=0, bottom_right_x=10, bottom_right_y=10
        ),
        image_base64="abc",
    )
    img2 = ImageRegion(
        id="img-2",
        bounding_box=BoundingBox(
            top_left_x=1, top_left_y=1, bottom_right_x=11, bottom_right_y=11
        ),
        image_base64="def",
    )
    page = Page(index=0, page_text=pt, images=[img1, img2])
    ocr = OcrResponse(pages=[page], metadata=Metadata(model="m"))
    embed_base64_images_in_html(ocr)
    assert "data:image/jpeg;base64,abc" in ocr.pages[0].page_text.html
    assert "data:image/jpeg;base64,def" in ocr.pages[0].page_text.html
