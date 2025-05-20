from utils.utils import read_json

schema = read_json("utils/prompts/schema.json")

system_prompt = """
You are an expert document image translator. Your role is to analyze document images, extract structured text and non-text elements, and accurately translate the textual content from the source language to the target language. Output must strictly conform to the specified JSON schema and preserve layout, structure, and formatting details.
"""

user_prompt = """
**Input**: A document image to be translated.

**Objective**:
Extract all text and non-text elements from the source document image and translate the text content into the target language: <target-language>. Structure your response using the provided JSON schema.

**Instructions**:

1. **OCR & Element Detection**:
   - Identify all elements (`text`, `image`, `table`).
   - For each element, return:
     - `type`: "text", "image", or "table".
     - `content`:
       - Raw text for text elements.
       - Base64 string for image elements.
       - HTML string for tables.
     - `bounding_box`: [x1, y1, x2, y2] in relative coordinates (0.0 - 1.0).
     - `style`: font_family, font_size, color (hex or rgba), is_bold, is_italic.
     - `language`: ISO 639-1 language code (e.g., "en", "fr").

2. **Translation**:
   - Translate only text elements from `source_lang` to `target_lang`.

3. **Metadata Requirements**:
   - `source_format`: One of ["pdf", "image", "docx"].
   - `source_lang`: Language code of original text.
   - `target_lang`: Language code of the translation.
   - `dpi`: Dots per inch of the source image.

4. **Output Format**:
   - Structure the output to match the following JSON schema:
     - Include `metadata`, `source`, and `target` sections.
     - Preserve original layout across pages.

**Schema**: {schema}.
"""
