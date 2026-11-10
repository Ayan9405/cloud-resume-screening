"""Lambda Handler for Generating S3 Presigned Upload URLs.
Enables direct browser-to-S3 document uploads without routing large
file payloads through backend servers or API Gateway limits.
"""

import os
import json
import uuid
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.config import Config
except ImportError:
    boto3 = None

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}


def generate_presigned_url(filename: str, content_type: str, job_id: str = "job-cloud-architect") -> Dict[str, Any]:
    """Generates an S3 presigned PUT URL for secure, direct file upload."""
    bucket_name = os.environ.get("RESUMES_BUCKET", "resume-screening-documents-bucket")
    region = os.environ.get("AWS_REGION", "us-east-1")
    use_aws = os.environ.get("USE_AWS_SERVICES", "false").lower() == "true"

    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {ext}. Allowed: {ALLOWED_EXTENSIONS}")

    unique_id = str(uuid.uuid4())[:8]
    clean_filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
    s3_key = f"resumes/{job_id}/{unique_id}_{clean_filename}"

    if boto3 and use_aws:
        try:
            s3_client = boto3.client(
                "s3",
                region_name=region,
                config=Config(signature_version="s3v4"),
            )
            presigned_url = s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": bucket_name,
                    "Key": s3_key,
                    "ContentType": content_type or "application/pdf",
                    "Metadata": {
                        "job_id": job_id,
                        "original_filename": clean_filename,
                    },
                },
                ExpiresIn=900,  # 15 minutes
            )
            return {
                "upload_url": presigned_url,
                "s3_bucket": bucket_name,
                "s3_key": s3_key,
                "job_id": job_id,
                "filename": clean_filename,
                "expires_in_seconds": 900,
                "is_mock": False,
            }
        except Exception as e:
            logger.warning(f"Error creating real S3 presigned URL: {e}. Falling back to mock URL.")

    # Local / Mock Dev Mode URL
    mock_url = f"/api/upload-direct?key={s3_key}&filename={clean_filename}&job_id={job_id}"
    return {
        "upload_url": mock_url,
        "s3_bucket": bucket_name,
        "s3_key": s3_key,
        "job_id": job_id,
        "filename": clean_filename,
        "expires_in_seconds": 900,
        "is_mock": True,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda entry point for API Gateway HTTP POST /upload-url."""
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "OPTIONS,POST",
    }

    # Handle CORS preflight
    http_method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")
    if http_method == "OPTIONS":
        return {"statusCode": 200, "headers": headers, "body": ""}

    try:
        body_raw = event.get("body", "{}")
        if isinstance(body_raw, str):
            body = json.loads(body_raw) if body_raw else {}
        else:
            body = body_raw or {}

        filename = body.get("filename")
        if not filename:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Missing 'filename' parameter in request body"}),
            }

        content_type = body.get("content_type", "application/pdf")
        job_id = body.get("job_id", "job-cloud-architect")

        result = generate_presigned_url(filename, content_type, job_id)
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(result),
        }
    except ValueError as ve:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": str(ve)}),
        }
    except Exception as e:
        logger.error(f"Internal error generating presigned URL: {e}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": "Internal server error generating upload URL", "details": str(e)}),
        }
