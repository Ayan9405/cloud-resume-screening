"""Lambda Handler for Candidate Leaderboard and Screening Results.
Handles API Gateway HTTP requests for:
- GET /candidates (List/Leaderboard sorted by score)
- GET /candidates/{id} (Detailed candidate profile)
- DELETE /candidates/{id} (Remove candidate entry)
- POST /candidates/rescore (Batch recalculate scores against active job)
"""

import os
import json
import logging
from typing import Dict, Any

from backend.services.dynamodb_service import DynamoDBService
from backend.services.matching_engine import MatchingEngine

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

db_service = DynamoDBService()
matching_engine = MatchingEngine()

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Requested-With",
    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,DELETE",
}


def _response(status_code: int, body_data: Any) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body_data, default=str),
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """API Gateway HTTP router for /candidates endpoints."""
    http_method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "GET")

    # Handle CORS Preflight
    if http_method == "OPTIONS":
        return _response(200, {"message": "CORS preflight OK"})

    path = event.get("rawPath") or event.get("path") or "/candidates"
    path_parameters = event.get("pathParameters") or {}
    query_parameters = event.get("queryStringParameters") or {}

    try:
        # Route: POST /candidates/rescore
        if path.endswith("/rescore") and http_method == "POST":
            return handle_batch_rescore(query_parameters.get("job_id"))

        # Route: GET /candidates/{id}
        candidate_id = path_parameters.get("id") or path_parameters.get("candidate_id")
        if not candidate_id and "/" in path.strip("/"):
            parts = path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] == "candidates":
                candidate_id = parts[1]

        if candidate_id:
            if http_method == "GET":
                cand = db_service.get_candidate(candidate_id, query_parameters.get("job_id"))
                if not cand:
                    return _response(404, {"error": f"Candidate {candidate_id} not found"})
                return _response(200, cand)

            elif http_method == "DELETE":
                success = db_service.delete_candidate(candidate_id, query_parameters.get("job_id"))
                return _response(200, {"success": success, "deleted_id": candidate_id})

        # Route: GET /candidates (Leaderboard)
        if http_method == "GET":
            job_id = query_parameters.get("job_id")
            candidates = db_service.list_candidates(job_id=job_id)
            return _response(200, {
                "count": len(candidates),
                "job_id": job_id,
                "candidates": candidates,
            })

        return _response(405, {"error": f"Method {http_method} on {path} not supported"})

    except Exception as e:
        logger.error(f"Error handling candidates API: {e}", exc_info=True)
        return _response(500, {"error": "Internal server error in candidates API", "details": str(e)})


def handle_batch_rescore(job_id: str = None) -> Dict[str, Any]:
    """Batch re-evaluates all candidates against the current job requirements."""
    target_job = db_service.get_job(job_id) if job_id else db_service.get_active_job()
    if not target_job:
        return _response(400, {"error": "No active job found to score against"})

    candidates = db_service.list_candidates(job_id=job_id)
    rescored_count = 0

    for cand in candidates:
        evaluation = matching_engine.evaluate_candidate(cand, target_job)
        cand["match_score"] = evaluation["match_score"]
        cand["status"] = evaluation["status"]
        cand["badge_color"] = evaluation["badge_color"]
        cand["verdict"] = evaluation["verdict"]
        cand["summary"] = evaluation["summary"]
        cand["matched_skills"] = evaluation["matched_skills"]
        cand["missing_skills"] = evaluation["missing_skills"]
        cand["breakdown"] = evaluation["breakdown"]
        cand["job_id"] = target_job["job_id"]
        cand["job_title"] = target_job.get("title")

        db_service.save_candidate(cand)
        rescored_count += 1

    # Return freshly sorted list
    updated_list = db_service.list_candidates(job_id=target_job["job_id"])
    return _response(200, {
        "message": f"Successfully re-scored {rescored_count} candidates against '{target_job.get('title')}'",
        "job_id": target_job["job_id"],
        "candidates": updated_list,
    })
