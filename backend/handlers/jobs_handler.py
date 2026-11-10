"""Lambda Handler for Job Description Management.
Handles API Gateway HTTP requests for:
- GET /jobs (List all jobs)
- POST /jobs (Create/update job requirements)
- GET /jobs/active (Retrieve current screening target job)
- POST /jobs/active (Set active screening job)
"""

import os
import json
import uuid
import logging
from typing import Dict, Any

from backend.services.dynamodb_service import DynamoDBService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

db_service = DynamoDBService()

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Requested-With",
    "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
}


def _response(status_code: int, body_data: Any) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body_data, default=str),
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """API Gateway HTTP router for /jobs endpoints."""
    http_method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "GET")

    if http_method == "OPTIONS":
        return _response(200, {"message": "CORS preflight OK"})

    path = event.get("rawPath") or event.get("path") or "/jobs"

    try:
        # Route: GET /jobs/active
        if path.endswith("/active") and http_method == "GET":
            active_job = db_service.get_active_job()
            return _response(200, active_job)

        # Route: POST /jobs/active
        if path.endswith("/active") and http_method == "POST":
            body = json.loads(event.get("body", "{}") or "{}")
            job_id = body.get("job_id")
            if not job_id:
                return _response(400, {"error": "Missing 'job_id' parameter in body"})
            job = db_service.get_job(job_id)
            if not job:
                return _response(404, {"error": f"Job {job_id} not found"})
            job["is_active"] = True
            db_service.save_job(job)
            return _response(200, {"message": f"Active job set to {job_id}", "job": job})

        # Route: GET /jobs
        if http_method == "GET":
            jobs = db_service.list_jobs()
            return _response(200, {"jobs": jobs})

        # Route: POST /jobs
        if http_method == "POST":
            body = json.loads(event.get("body", "{}") or "{}")
            if not body.get("title") or not body.get("description"):
                return _response(400, {"error": "Both 'title' and 'description' are required"})

            job_id = body.get("job_id") or f"job-{uuid.uuid4().hex[:6]}"
            job_record = {
                "job_id": job_id,
                "title": body.get("title"),
                "department": body.get("department", "Engineering"),
                "min_experience_years": float(body.get("min_experience_years", 2.0)),
                "required_skills": body.get("required_skills", []),
                "preferred_skills": body.get("preferred_skills", []),
                "description": body.get("description"),
                "is_active": body.get("is_active", True),
            }
            saved = db_service.save_job(job_record)
            return _response(201, {"message": "Job created/updated successfully", "job": saved})

        return _response(405, {"error": f"Method {http_method} not supported on {path}"})

    except Exception as e:
        logger.error(f"Error handling jobs API: {e}", exc_info=True)
        return _response(500, {"error": "Internal server error in jobs API", "details": str(e)})
