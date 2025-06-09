import os
from mistralai import Mistral


class MistralOCR:
    """
    Wrapper for the Mistral OCR API client.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize the MistralOCR client with an API key.
        """
        self.api_key = api_key or os.getenv("OCR_MODEL_API_KEY")
        self.client = Mistral(api_key=self.api_key)

    def process_image(self, base64_image: str, model: str = "mistral-ocr-latest"):
        """
        Run OCR on a base64-encoded image using the specified model.

        Args:
            base64_image (str): The image encoded as base64.
            model (str): The OCR model to use.

        Returns:
            The OCR response from the Mistral API.
        """
        ocr_response = self.client.ocr.process(
            model=model,
            document={"type": "image_url", "image_url": base64_image},
            include_image_base64=True,
        )
        return ocr_response
