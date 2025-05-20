from dataclasses import dataclass
from typing import Optional, List
from PIL import Image
from google.genai.types import GenerateContentResponse


@dataclass
class Message:
    role: str
    contents: Optional[List[str | Image.Image] | List[GenerateContentResponse]]


class GeminiUserMessage(Message):
    def __init__(self, prompt: str, images: List[Image.Image]):
        super().__init__(role="user", contents=images + [prompt])


class GeminiAssistantMessage(Message):
    def __init__(self, response: GenerateContentResponse):
        super().__init__(role="assistant", contents=[response])
