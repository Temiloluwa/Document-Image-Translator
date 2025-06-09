# Document Image Translator

A serverless demonstration of deploying AI products in AWS: this project translates document images between languages using AWS Lambda, S3, DynamoDB, and advanced AI models (OCR and LLMs).

---

## Supporting Repositories

This project is supported by shared infrastructure and CI/CD pipeline repositories:

- **Infrastructure as Code:** [bildcraft/shared/infrastructure](https://gitlab.com/bildcraft/shared/infrastructure)
  - Contains Terraform for provisioning AWS resources (S3, Lambda, DynamoDB, API Gateway, etc.)
- **CI/CD Pipelines:** [bildcraft/shared/ci-cd-pipelines](https://gitlab.com/bildcraft/shared/ci-cd-pipelines)
  - Centralized GitLab CI/CD templates and automation for build, test, deployment, and environment management

> **Note:** The infrastructure and CI/CD repositories above deploy this project to production 
---

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Backend (AWS Lambda)](#backend-aws-lambda)
  - [API Endpoints](#api-endpoints)
  - [S3 Event Trigger](#s3-event-trigger)
  - [Example Workflow](#example-workflow)
- [Web Application (Frontend)](#web-application-frontend)
- [Installation & Development](#installation--development)
- [Configuration](#configuration)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [License](#license)

---

## Features
- Upload document images (via web app or API)
- Extract text using OCR (Mistral)
- Translate text to target language using LLMs (Gemini, etc.)
- Download/view translated results
- Status tracking via DynamoDB
- Modular, testable, and extensible pipeline

---

## Architecture
- **Frontend:** Next.js/TypeScript web app for uploads and status tracking
- **Backend:** AWS Lambda (Python) for processing, translation, and status
- **SQS:** Queues jobs for Lambda
- **Storage:** S3 for document images and results
- **Database:** DynamoDB for status tracking
- **AI:** Mistral (OCR), Gemini (translation)

---

## Backend (AWS Lambda)

This backend is exposed as a REST API powered by **AWS API Gateway** and AWS Lambda.

### API Endpoints (see `api/lambda_entrypoint.py`)
- `GET /presigned-url`: Get a presigned S3 URL for uploading a document image
- `POST /upload-image`: Record upload status in DynamoDB
- `GET /status`: Retrieve translation status for a file

### S3 Event Trigger
- Uploading a file to the configured S3 bucket triggers the translation pipeline automatically.

### Example Workflow
1. Client requests a presigned S3 URL from the API
2. Client uploads a document image to S3
3. Lambda is triggered, processes the image, runs OCR, translates, and uploads results
4. Status is tracked in DynamoDB and can be queried via API

---

## Web Application (Frontend)

- **Location:** `web/document-image-translator/`
- **Tech stack:** Next.js, TypeScript
- **Features:**
  - Upload document images (requests presigned S3 URL from backend)
  - Track translation status (polls backend for updates)
  - View/download translated results
- **Development:**
  1. `cd web/document-image-translator`
  2. Install dependencies: `npm install`
  3. Start dev server: `npm run dev`
- **Configuration:**
  - API endpoint URLs are set in the frontend code (see `src/app/`)
  - The frontend expects the backend Lambda/API to be deployed and accessible
- **See also:** `web/document-image-translator/README.md` for more details

---

## Installation & Development

### Backend
1. Clone the repository
2. Create a virtual environment and install dependencies:
   ```sh
   uv venv --python=3.12.4 .venv
   . .venv/bin/activate
   uv sync --all-groups
   ```
3. Run tests:
   ```sh
   make test
   ```
4. Lint and format code:
   ```sh
   make lint
   ```

### Frontend
1. `cd web/document-image-translator`
2. `npm install`
3. `npm run dev`

---

## Configuration
- `src/utils/config.yaml` – Model IDs, image size/quality, etc.
- Environment variables for AWS resources (S3 bucket, DynamoDB table)
- API endpoint URLs in frontend (see `web/document-image-translator/src/app/`)

---

## Testing
- Run all tests: `make test`
- Integration and unit tests are in `tests/`
- Uses `pytest`, `pytest-asyncio`, and `pytest-cov`

---

## Project Structure
- `api/lambda_entrypoint.py` – REST API handlers for presigned URLs, status, etc.
- `src/lambda_entrypoint.py` – Main Lambda entrypoint for S3 event processing
- `src/models/` – Data models (status, intermediate representation, etc.)
- `src/pipeline/` – Image processing and translation pipeline
- `src/utils/` – Utilities, config, LLM/OCR wrappers, prompts
- `tests/` – Unit and integration tests
- `data/` – Sample images (if present)
- `web/document-image-translator/` – Next.js frontend app

---

## Dependencies
- aioboto3, aiofiles, beautifulsoup4, datauri, google-genai, mistralai, omegaconf, pillow, python-json-logger, requests, python-ulid, etc.
- Dev: mypy, pre-commit, ruff, pytest, pytest-cov, numpy, pytest-asyncio, pytest-dotenv

---

## License
MIT

---

*Last updated: June 9, 2025*
