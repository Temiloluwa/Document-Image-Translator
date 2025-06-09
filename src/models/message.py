from dataclasses import dataclass
from typing import Optional, List
from PIL import Image
from google.genai.types import GenerateContentResponse


@dataclass
class Message:
    """
    Represents a message exchanged with the LLM, including role and contents.
    """

    role: str
    contents: Optional[List[str | Image.Image] | List[GenerateContentResponse]]


class GeminiUserMessage(Message):
    """
    Message class for user input to Gemini, combining images and prompt.
    """

    def __init__(self, prompt: str, images: List[Image.Image]):
        """
        Initialize a user message with a prompt and images.
        """
        super().__init__(role="user", contents=images + [prompt])


class GeminiAssistantMessage(Message):
    """
    Message class for Gemini assistant responses.
    """

    def __init__(self, response: GenerateContentResponse):
        """
        Initialize an assistant message with a response object.
        """
        super().__init__(role="assistant", contents=[response])
