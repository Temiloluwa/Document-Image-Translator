from .template import (
    system_translation_prompt,
    user_translation_prompt,
    system_markdown_to_html_prompt,
    user_markdown_to_html_prompt,
)


class Prompt:
    """
    Provides static methods to retrieve system and user prompts for translation and markdown-to-HTML tasks.
    """

    @staticmethod
    def get_system_translation_prompt() -> str:
        """
        Return the system prompt for the translation LLM.
        """
        return system_translation_prompt

    @staticmethod
    def get_user_translation_prompt(ocr_response: str, target_language: str) -> str:
        """
        Return the user prompt, formatted with OCR response and target language.
        """
        return user_translation_prompt.replace(
            "<target-language>", target_language
        ).replace("<ocr-response>", ocr_response)

    @staticmethod
    def get_system_markdown_to_html_prompt(image_dimensions_list: str = "") -> str:
        """
        Return the system prompt for markdown-to-HTML conversion, formatted with image dimensions list.
        """
        return system_markdown_to_html_prompt.replace(
            "<image-dimensions-list>", image_dimensions_list
        )

    @staticmethod
    def get_user_markdown_to_html_prompt(markdown_content: str) -> str:
        """
        Return the user prompt for markdown-to-HTML conversion, formatted with markdown content.
        """
        return user_markdown_to_html_prompt.replace(
            "<markdown-content>", markdown_content
        )
