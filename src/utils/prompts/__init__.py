from .template import system_translate_and_html_prompt, user_translate_and_html_prompt


class Prompt:
    """
    Provides static methods to retrieve system and user prompts for translation and markdown-to-HTML tasks.
    """

    @staticmethod
    def get_system_translate_and_html_prompt(image_dimensions_list: str = "") -> str:
        """
        Return the system prompt for markdown-to-HTML conversion, formatted with image dimensions list.
        """
        return system_translate_and_html_prompt.replace(
            "<image-dimensions-list>", image_dimensions_list
        )

    @staticmethod
    def get_user_translate_and_html_prompt(
        markdown_content: str, target_language: str
    ) -> str:
        """
        Return the user prompt for PDF translation and HTML generation in one step, formatted with markdown content and target language.
        """
        return user_translate_and_html_prompt.replace(
            "<target-language>", target_language
        ).replace("<markdown-content>", markdown_content)
