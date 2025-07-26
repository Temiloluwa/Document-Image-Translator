import os
import json
from bs4 import BeautifulSoup
from logging import getLogger
from models.status import Status
from utils.llm.mistral import MistralOCR
from utils.llm.gemini import Gemini
from utils.utils import get_config, post_status_to_dynamodb
from models.intermediate_representation import (
    parse_ocr_response,
    combine_pages_within_token_limit,
    embed_images_in_markdown,
    embed_base64_images_in_html,
    get_image_dimensions_list_from_ir,
    OcrResponse,
)
from utils.prompts import Prompt

logger = getLogger("image-translator")


async def translate_pdf(
    pdf_bytes: bytes,
    target_language: str,
    file_name: str = None,
    uuid: str = None,
) -> OcrResponse:
    """
    Perform OCR on the input PDF and translate the extracted text to the target language.
    Posts status updates to DynamoDB at key pipeline steps.

    Args:
        pdf_bytes (str): The input PDF bytes.
        target_language (str): The language to translate the text into.
        file_name (str): The original file name (for status updates).
        uuid (str): Unique identifier (for status updates).

    Returns:
        OcrResponse: The intermediate representation object containing translated text and images in markdown and HTML formats.
    """
    # Step 1: Load configuration
    config = get_config(
        os.path.join(os.path.dirname(__file__), "..", "utils", "config.yaml")
    )

    gemini = Gemini(Prompt.get_system_translate_and_html_prompt(""))

    def token_counter(text: str) -> int:
        """Estimate token count"""
        return gemini.estimate_tokens(text, config.translator_model.id)

    # Step 2: Validate required arguments
    if not file_name or not uuid:
        raise ValueError("File name and UUID must be provided to post status updates.")

    # Step 3: Post initial status
    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid,
            state="started",
            progress=0,
            message="Starting PDF translation pipeline",
        ).asdict(),
    )

    # Step 4: Perform OCR on PDF
    logger.info("Performing OCR...")
    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid, state="ocr_processing", progress=10, message="Performing OCR"
        ).asdict(),
    )
    try:
        ocr_response = MistralOCR().process_pdf(
            base64_pdf=pdf_bytes, model=config.ocr_model.id
        )
        response_ir = parse_ocr_response(json_response=json.loads(ocr_response.json()))
    except Exception as e:
        logger.error(f"Error parsing OCR response: {e}")
        await post_status_to_dynamodb(
            file_name,
            Status(
                uuid=uuid,
                state="error",
                progress=15,
                message=f"Error parsing OCR response: {e}",
            ).asdict(),
        )
        raise ValueError(
            "Failed to parse OCR response. Please check the input PDF or OCR model configuration."
        )

    # Step 5: Post OCR complete status
    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid, state="ocr_complete", progress=30, message="OCR complete"
        ).asdict(),
    )

    # Step 6: Combine pages within token limit
    logger.info("Combining pages within token limit...")
    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid, state="combining_pages", progress=40, message="Combining pages"
        ).asdict(),
    )

    try:
        combined_ir = combine_pages_within_token_limit(
            response_ir,
            token_counter,
            config.pdf.max_token_size,
            config.pdf.max_tokens_per_page,
        )
    except Exception as e:
        logger.error(f"Error combining pages: {e}")
        await post_status_to_dynamodb(
            file_name,
            Status(
                uuid=uuid,
                state="error",
                progress=45,
                message=f"Error combining pages: {e}",
            ).asdict(),
        )
        raise ValueError("Failed to combine pages within token limit.")

    # Step 7: Post pages combined status
    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid, state="pages_combined", progress=50, message="Pages combined"
        ).asdict(),
    )

    # Step 8: Translate and generate HTML for each page
    logger.info("Translating and generating HTML for each page asynchronously...")
    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid,
            state="translating_html",
            progress=60,
            message="Translating each page to HTML",
        ).asdict(),
    )
    for idx, page in enumerate(combined_ir.pages, start=1):
        image_dimensions_list = get_image_dimensions_list_from_ir(page)
        translation_system_prompt = Prompt.get_system_translate_and_html_prompt(
            image_dimensions_list
        )
        translation_user_prompt = Prompt.get_user_translate_and_html_prompt(
            page.page_text.markdown, target_language
        )
        try:
            gemini = Gemini(
                system_instruction=translation_system_prompt,
                http_options={"timeout": config.translator_model.timeout},
            )
            logger.info(
                f"Translating page {idx} of Combined IR has {gemini.estimate_tokens(translation_user_prompt, config.translator_model.id)} tokens"
            )
            translation_response = await gemini.generate(
                prompt=translation_user_prompt,
                image=[],
                model=config.translator_model.id,
            )
            translated_html = translation_response.contents[0].strip("```html\n")
            page.page_text.html = translated_html
        except Exception as e:
            logger.error(f"Error parsing translation LLM response for page {idx}: {e}")
            await post_status_to_dynamodb(
                file_name,
                Status(
                    uuid=uuid,
                    state="error",
                    progress=65,
                    message=f"Error parsing translation LLM response for page {idx}: {e}",
                ).asdict(),
            )
            raise ValueError(
                f"Failed to parse LLM response for translation on page {idx}."
            )
    # Step 9: Embed images in markdown and html
    embed_base64_images_in_html(combined_ir)
    embed_images_in_markdown(combined_ir)

    # Step 10: Combine all page HTML bodies into one and assign to page 1
    combined_html = combine_html(combined_ir)
    if combined_ir.pages:
        combined_ir.pages[0].page_text.html = combined_html

    # Step 11: Post pipeline complete status
    logger.info("PDF translation complete.")
    await post_status_to_dynamodb(
        file_name,
        Status(
            uuid=uuid, state="complete", progress=100, message="Pipeline complete"
        ).asdict(),
    )

    # Step 12: Return the intermediate representation (IR) object, just like image_translator
    return combined_ir


def combine_html(ir: OcrResponse) -> str:
    """
    Combine the HTML body contents of all pages in the IR into a single HTML document with one head, using BeautifulSoup.
    """
    if (
        not ir.pages
        or not hasattr(ir.pages[0].page_text, "html")
        or not ir.pages[0].page_text.html
    ):
        return ""  # No HTML found

    # Parse first page's HTML
    soup_first = BeautifulSoup(ir.pages[0].page_text.html, "html.parser")
    head_tag = soup_first.head
    head_content = str(head_tag) if head_tag else ""
    body_tag = soup_first.body
    body_content = body_tag.decode_contents() if body_tag else soup_first.decode()

    # Append body from page 2 onward
    for p in ir.pages[1:]:
        html = (
            p.page_text.html
            if hasattr(p.page_text, "html") and p.page_text.html
            else ""
        )
        if html:
            soup = BeautifulSoup(html, "html.parser")
            body_tag = soup.body
            if body_tag:
                body_content += "\n" + body_tag.decode_contents()
            else:
                body_content += "\n" + soup.decode()

    # Build the final HTML document
    return f'<!DOCTYPE html>\n<html lang="en">\n{head_content}\n<body>\n{body_content}\n</body>\n</html>'
