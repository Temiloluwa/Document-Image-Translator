from .template import system_prompt, user_prompt


class Prompt:
    @staticmethod
    def get_system_prompt() -> str:
        return system_prompt

    @staticmethod
    def get_user_prompt(target_language: str) -> str:
        return user_prompt.replace("<target-language>", target_language)
