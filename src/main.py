import json
from lambda_entrypoint import lambda_handler


def build_sqs_event(bucket: str, key: str) -> dict:
    """
    Build a single SQS-wrapped S3 event record for a given bucket and key.
    """
    s3_event = {
        "Records": [
            {
                "eventSource": "aws:s3",
                "s3": {
                    "bucket": {"name": bucket},
                    "object": {"key": key},
                },
            }
        ]
    }

    return {"Records": [{"body": json.dumps(s3_event), "eventSource": "aws:sqs"}]}


def main():
    bucket = "blc-image-translation-uploads"
    base_path = "uploads/jul-24-25/01K0YGNKCBJ2YZZ55KK66W9KHR/german"

    # files = ["deutschland-edition-pg-9.png", "Wired_2020-11-us.pdf"]
    files = ["Wired_2020-11-us.pdf"]

    sqs_records = []
    for filename in files:
        full_key = f"{base_path}/{filename}"
        sqs_event = build_sqs_event(bucket, full_key)
        sqs_records.append(sqs_event["Records"][0])

    full_event = {"Records": sqs_records}
    result = lambda_handler(full_event, context=None)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
