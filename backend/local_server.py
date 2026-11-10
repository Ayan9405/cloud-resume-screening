"""Local Development Server & Testing Harness for AI Resume Screening Pipeline.
Runs a FastAPI server exposing identical endpoints to AWS API Gateway + S3 Uploads.
Allows the team to develop and test the entire frontend & backend locally
without needing live AWS credentials or incurring cloud costs.
"""

import os
import sys
import uuid
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.handlers.presigned_url_handler import generate_presigned_url
from backend.handlers.s3_trigger_handler import process_resume_payload
from backend.services.dynamodb_service import DynamoDBService
from backend.services.matching_engine import MatchingEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("local_server")

app = FastAPI(
    title="Automated AI Resume & Document Screening API",
    description="Local development backend simulating AWS Lambda, S3, Textract, and DynamoDB.",
    version="1.0.0",
)

# Enable CORS for React frontend (Vite defaults to 5173 or 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_service = DynamoDBService()
matching_engine = MatchingEngine()


class PresignedUrlRequest(BaseModel):
    filename: str
    content_type: Optional[str] = "application/pdf"
    job_id: Optional[str] = "job-cloud-architect"


class JobCreateRequest(BaseModel):
    job_id: Optional[str] = None
    title: str
    department: Optional[str] = "Engineering"
    min_experience_years: float = 2.0
    required_skills: List[str]
    preferred_skills: Optional[List[str]] = []
    description: str
    is_active: Optional[bool] = True


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "AI Resume Screening Pipeline - Local Development Server",
        "docs_url": "/docs",
        "active_job": db_service.get_active_job().get("title"),
    }


# ------------------ Presigned URL & S3 Simulation ------------------ #

@app.post("/api/upload-url")
def get_upload_url(payload: PresignedUrlRequest):
    """Generates presigned upload URL or local direct upload route."""
    try:
        return generate_presigned_url(payload.filename, payload.content_type, payload.job_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/upload-direct")
@app.post("/api/upload-direct")
async def upload_direct_file(
    file: UploadFile = File(...),
    job_id: Optional[str] = Form("job-cloud-architect"),
):
    """Direct upload endpoint simulating the S3 ObjectCreated trigger."""
    try:
        content = await file.read()
        filename = file.filename or "uploaded_resume.pdf"
        s3_key = f"resumes/{job_id}/{uuid.uuid4().hex[:6]}_{filename}"

        logger.info(f"Received direct upload: {filename} ({len(content)} bytes)")
        candidate_record = process_resume_payload(
            file_bytes=content,
            filename=filename,
            s3_bucket="local-mock-bucket",
            s3_key=s3_key,
            job_id=job_id,
        )
        return {
            "status": "success",
            "message": f"Resume '{filename}' parsed and candidate '{candidate_record['name']}' screened successfully.",
            "candidate": candidate_record,
        }
    except Exception as e:
        logger.error(f"Upload and screening failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ------------------ Candidates & Leaderboard Endpoints ------------------ #

@app.get("/api/candidates")
def list_candidates(job_id: Optional[str] = Query(None)):
    """Retrieve candidates sorted by match_score descending."""
    candidates = db_service.list_candidates(job_id=job_id)
    return {
        "count": len(candidates),
        "job_id": job_id,
        "candidates": candidates,
    }


@app.get("/api/candidates/{candidate_id}")
def get_candidate(candidate_id: str, job_id: Optional[str] = Query(None)):
    """Retrieve detailed candidate evaluation profile."""
    cand = db_service.get_candidate(candidate_id, job_id=job_id)
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return cand


@app.delete("/api/candidates/{candidate_id}")
def delete_candidate(candidate_id: str, job_id: Optional[str] = Query(None)):
    """Delete a candidate record."""
    success = db_service.delete_candidate(candidate_id, job_id=job_id)
    return {"success": success, "deleted_id": candidate_id}


@app.post("/api/candidates/rescore")
def rescore_candidates(job_id: Optional[str] = Query(None)):
    """Batch re-score candidates against current job requirements."""
    target_job = db_service.get_job(job_id) if job_id else db_service.get_active_job()
    candidates = db_service.list_candidates(job_id=job_id)
    rescored = []

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
        rescored.append(cand)

    rescored.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return {
        "message": f"Rescored {len(rescored)} candidates against '{target_job.get('title')}'",
        "job_id": target_job["job_id"],
        "candidates": rescored,
    }


# ------------------ Jobs Endpoints ------------------ #

@app.get("/api/jobs")
def list_jobs():
    """List available job descriptions."""
    return {"jobs": db_service.list_jobs()}


@app.get("/api/jobs/active")
def get_active_job():
    """Return active screening job description."""
    return db_service.get_active_job()


@app.post("/api/jobs")
def create_job(payload: JobCreateRequest):
    """Create or update job description."""
    job_id = payload.job_id or f"job-{uuid.uuid4().hex[:6]}"
    record = {
        "job_id": job_id,
        "title": payload.title,
        "department": payload.department,
        "min_experience_years": payload.min_experience_years,
        "required_skills": payload.required_skills,
        "preferred_skills": payload.preferred_skills,
        "description": payload.description,
        "is_active": payload.is_active,
    }
    saved = db_service.save_job(record)
    return {"message": "Job created/updated successfully", "job": saved}


@app.post("/api/jobs/active")
def set_active_job(job_id: str = Query(...)):
    """Set the active job for screening."""
    job = db_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    job["is_active"] = True
    db_service.save_job(job)
    return {"message": f"Job {job_id} set as active", "job": job}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting AI Resume Screening Local Server on http://localhost:{port}")
    print(f"📖 Swagger API Documentation available at http://localhost:{port}/docs")
    uvicorn.run("backend.local_server:app", host="0.0.0.0", port=port, reload=True)
