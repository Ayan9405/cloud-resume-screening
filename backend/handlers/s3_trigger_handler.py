"""S3 Event Trigger Lambda Handler for AI Resume & Document Screening.
Triggered automatically whenever a PDF/DOCX resume is uploaded to S3.
Orchestrates OCR Parsing -> NLP Entity Extraction -> Semantic Matching -> DynamoDB Storage.
"""

import os
import json
import uuid
import urllib.parse
import logging
from typing import Dict, Any

from backend.services.document_parser import DocumentParser
from backend.services.nlp_extractor import NLPExtractor
from backend.services.matching_engine import MatchingEngine
from backend.services.dynamodb_service import DynamoDBService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize service singletons for container reuse across warm Lambda invocations
doc_parser = DocumentParser()
nlp_extractor = NLPExtractor()
matching_engine = MatchingEngine()
db_service = DynamoDBService()


def process_resume_payload(
    file_bytes: bytes,
    filename: str,
    s3_bucket: str = "",
    s3_key: str = "",
    job_id: str = "job-cloud-architect",
) -> Dict[str, Any]:
    """Core resume processing pipeline.

    1. OCR / Text Extraction
    2. NLP Entity & Skill Extraction
    3. Job Description Lookup
    4. Scoring & Fit Evaluation
    5. DynamoDB Persistence
    """
    logger.info(f"Processing resume: {filename} (S3 Key: {s3_key}) for Job: {job_id}")

    # Step 1: Extract Text via DocumentParser (AWS Textract or local fallback)
    parse_result = doc_parser.extract_text(
        file_bytes=file_bytes,
        filename=filename,
        s3_bucket=s3_bucket,
        s3_key=s3_key,
    )
    raw_text = parse_result.get("text", "")
    page_count = parse_result.get("page_count", 1)
    parse_method = parse_result.get("method", "unknown")

    # Step 2: Extract Entities & Candidate Profile via NLPExtractor
    profile = nlp_extractor.extract_candidate_profile(raw_text, filename=filename)

    # Step 3: Fetch Target Job Description
    target_job = db_service.get_job(job_id)
    if not target_job:
        target_job = db_service.get_active_job()

    # Step 4: Evaluate Candidate against Job Requirements
    evaluation = matching_engine.evaluate_candidate(profile, target_job)

    # Step 5: Construct Candidate Record for DynamoDB
    candidate_id = f"cand-{uuid.uuid4().hex[:8]}"
    candidate_record = {
        "candidate_id": candidate_id,
        "job_id": target_job.get("job_id", job_id),
        "job_title": target_job.get("title", "Cloud Solutions Architect"),
        "name": profile.get("name", "Candidate"),
        "email": profile.get("email", "candidate@example.com"),
        "phone": profile.get("phone", "N/A"),
        "links": profile.get("links", {}),
        "filename": filename,
        "s3_bucket": s3_bucket,
        "s3_key": s3_key,
        "page_count": page_count,
        "parse_method": parse_method,
        "skills": profile.get("skills", []),
        "experience_years": profile.get("experience_years", 1.0),
        "education": profile.get("education", []),
        "match_score": evaluation.get("match_score", 0.0),
        "status": evaluation.get("status", "Review"),
        "badge_color": evaluation.get("badge_color", "yellow"),
        "verdict": evaluation.get("verdict", ""),
        "summary": evaluation.get("summary", ""),
        "matched_skills": evaluation.get("matched_skills", []),
        "missing_skills": evaluation.get("missing_skills", []),
        "breakdown": evaluation.get("breakdown", {}),
        "experience_snippets": profile.get("experience_snippets", []),
        "text_preview": profile.get("text_preview", ""),
    }

    # Step 6: Save into DynamoDB Table
    saved = db_service.save_candidate(candidate_record)
    logger.info(f"Successfully processed candidate {saved['name']} - Match Score: {saved['match_score']}%")
    return saved


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main AWS Lambda entry point triggered by S3 ObjectCreated events."""
    logger.info(f"Received event: {json.dumps(event, default=str)}")

    processed_records = []

    # Check for direct invocation / API Gateway call
    if "Records" not in event:
        # Handle direct testing call
        raw_body = event.get("body", "{}")
        if isinstance(raw_body, str):
            payload = json.loads(raw_body) if raw_body else {}
        else:
            payload = raw_body

        filename = payload.get("filename", "sample_resume.pdf")
        job_id = payload.get("job_id", "job-cloud-architect")
        text_content = payload.get("text", "")
        file_bytes = text_content.encode("utf-8")

        result = process_resume_payload(
            file_bytes=file_bytes,
            filename=filename,
            s3_bucket="direct-invoke",
            s3_key=f"resumes/{filename}",
            job_id=job_id,
        )
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "success", "candidate": result}),
        }

    # Process standard S3 Event records
    import boto3
    s3_client = boto3.client("s3")

    for record in event.get("Records", []):
        try:
            s3_info = record.get("s3", {})
            bucket_name = s3_info.get("bucket", {}).get("name")
            raw_key = s3_info.get("object", {}).get("key", "")
            s3_key = urllib.parse.unquote_plus(raw_key)

            if not bucket_name or not s3_key:
                continue

            filename = os.path.basename(s3_key)
            # Infer job_id from prefix if structured like resumes/<job_id>/<file>
            parts = s3_key.split("/")
            job_id = parts[1] if len(parts) >= 3 else "job-cloud-architect"

            logger.info(f"Fetching object s3://{bucket_name}/{s3_key}")
            response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
            file_bytes = response["Body"].read()

            candidate_record = process_resume_payload(
                file_bytes=file_bytes,
                filename=filename,
                s3_bucket=bucket_name,
                s3_key=s3_key,
                job_id=job_id,
            )
            processed_records.append(candidate_record)

        except Exception as e:
            logger.error(f"Error processing S3 record {record}: {e}", exc_info=True)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Processed {len(processed_records)} resumes successfully",
            "candidates": [c.get("candidate_id") for c in processed_records],
        }),
    }
