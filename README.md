# Document Image Translator Lambda

AWS Lambda function to translate document images between languages.

## Features
- Accepts document images as input
- Detects and extracts text from images
- Translates extracted text from a source language to a target language
- Returns translated text or a new image with translated content

## Usage
Deploy as an AWS Lambda function. Trigger with an event containing the document image and language parameters.

## Requirements
- AWS Lambda
- Python 3.12
- Dependencies as specified in `pyproject.toml`

## Project Structure
- `src/` - Lambda entrypoint and core logic
- `tests/` - Unit tests
- `data/` - Sample images
