# Document Image Translator API

This API provides endpoints for uploading document images, checking translation status, and retrieving translated results. It is designed to be used with AWS Lambda, S3, and DynamoDB.

## Endpoints


### 1. Generate Presigned Upload URL

- **Endpoint:** `GET /v1/presigned-url`
- **Description:** Generates a presigned S3 URL for uploading a document image for translation, and returns the S3 result locations for the translated output.
- **Query Parameters:**
  - `filename` (string, required): The name of the file to upload.
  - `target_language` (string, required): The target language code for translation.
- **Example cURL:**
  ```sh
  curl -G \
    --data-urlencode "filename=example.png" \
    --data-urlencode "target_language=fr" \
    https://<api-gateway-url>/v1/presigned-url
  ```
- **Responses:**
  - `200 OK`: Returns a JSON object with the presigned upload URL and S3 result locations for markdown and HTML output.
    ```json
    {
      "upload_url": "string",
      "markdown_results_location": "string",
      "html_results_location": "string"
    }
    ```
  - `400 Bad Request`: Missing required parameters.
    ```json
    { "error": "filename and target_language are required" }
    ```

---


### 2. Get Upload/Translation Status

- **Endpoint:** `GET /v1/status`
- **Description:** Retrieves the status of an uploaded file and its translation process.
- **Query Parameters:**
  - `html_results_location` (string, required) or `markdown_results_location` (string, required): The S3 key for the result file. The API extracts the UUID and filename from this value.
- **Example cURL:**
  ```sh
  curl -G \
    --data-urlencode "html_results_location=results/jan-05-24/01hzyq2q2q2q2q2q2q2q2q2q2q/example_result.html" \
    https://<api-gateway-url>/v1/status
  ```
- **Responses:**
  - `200 OK`: Returns the status item from DynamoDB, or the result locations if processing is complete.
    ```json
    {
      "markdown_results_location": "string",
      "html_results_location": "string"
    }
    ```
    or
    ```json
    { ...item }
    ```
  - `400 Bad Request`: Missing or invalid result location.
    ```json
    { "error": "A valid html_results_location or markdown_results_location is required" }
    ```
  - `404 Not Found`: Item not found.
    ```json
    { "error": "Item not found" }
    ```

---


### 3. Get Translation Result Locations

- **Endpoint:** `GET /v1/result`
- **Description:** Returns the S3 locations for the translated document in Markdown and HTML formats.
- **Query Parameters:**
  - `html_results_location` (string, required) or `markdown_results_location` (string, required): The S3 key for the result file. The API extracts the UUID and filename from this value.
- **Example cURL:**
  ```sh
  curl -G \
    --data-urlencode "markdown_results_location=results/jan-05-24/01hzyq2q2q2q2q2q2q2q2q2q2q/example_result.md" \
    https://<api-gateway-url>/v1/result
  ```
- **Responses:**
  - `200 OK`: Returns the S3 locations for both Markdown and HTML results.
    ```json
    {
      "markdown_results_location": "string",
      "html_results_location": "string"
    }
    ```
  - `400 Bad Request`: Missing or invalid result location.
    ```json
    { "error": "A valid html_results_location or markdown_results_location is required" }
    ```
  - `404 Not Found`: Item not found.
    ```json
    { "error": "Item not found" }
    ```

---

### 4. Fallback for Unknown Endpoints

- **Response:** `404 Not Found`
  ```json
  { "error": "Not Found" }
  ```

---

## Environment Variables
- `STATUS_TABLE_NAME`: DynamoDB table for status tracking
- `UPLOADS_BUCKET`: S3 bucket for uploads
- `RESULTS_BUCKET`: S3 bucket for results

## Requirements
- AWS Lambda
- S3
- DynamoDB
- Python 3.8+
- boto3
- ulid-py

---

For implementation details, see `lambda_entrypoint.py`.
