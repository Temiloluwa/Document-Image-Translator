#!/bin/bash


# upload_to_s3.sh - Upload a file to a presigned S3 URL using curl
#
# Usage:
#   ./upload_to_s3.sh <filename> <presigned_url>
#
# Example:
#   ./upload_to_s3.sh myfile.pdf "https://example.com/upload?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=..."
#
# NOTE: Always wrap the presigned URL in quotes to avoid shell parse errors with '&' characters.


FILENAME="$1"
PRESIGNED_URL="$2"

if [ -z "$FILENAME" ] || [ -z "$PRESIGNED_URL" ]; then
  echo "Usage: $0 <filename> <presigned_url>"
  exit 1
fi

curl -X PUT \
  -H "Content-Type: application/octet-stream" \
  --upload-file "$FILENAME" \
  "$PRESIGNED_URL"
