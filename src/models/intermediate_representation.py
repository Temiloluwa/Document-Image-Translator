from pydantic import BaseModel, Field
from typing import List, Literal


class Style(BaseModel):
    font_family: str
    font_size: int
    color: str
    is_bold: bool
    is_italic: bool


class Element(BaseModel):
    type: Literal["text", "image", "table"]
    content: str
    bounding_box: List[float] = Field(..., min_items=4, max_items=4)  # type: ignore
    style: Style
    language: str


class Dimensions(BaseModel):
    width: int
    height: int


class Page(BaseModel):
    page_num: int
    dimensions: Dimensions
    elements: List[Element]


class Document(BaseModel):
    pages: List[Page]


class Metadata(BaseModel):
    source_format: Literal["pdf", "image", "docx"]
    source_lang: str
    target_lang: str
    dpi: int


class DocumentTranslation(BaseModel):
    metadata: Metadata
    source: Document
    target: Document
