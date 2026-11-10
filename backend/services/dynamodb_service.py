"""Database CRUD Logic for NoSQL Storage (AWS DynamoDB with Local Fallback).
Handles candidate entries, job descriptions, leaderboard queries,
and score updates.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

try:
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
except ImportError:
    boto3 = None


def _convert_float_to_decimal(obj):
    """Recursively convert float to Decimal for DynamoDB serialization."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: _convert_float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_float_to_decimal(i) for i in obj]
    return obj


def _convert_decimal_to_float(obj):
    """Recursively convert Decimal to float for JSON/dict responses."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: _convert_decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_decimal_to_float(i) for i in obj]
    return obj


class DynamoDBService:
    """Manages NoSQL persistence for Candidates and Jobs."""

    def __init__(
        self,
        candidates_table_name: Optional[str] = None,
        jobs_table_name: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        self.region_name = region_name or os.environ.get("AWS_REGION", "us-east-1")
        self.candidates_table_name = candidates_table_name or os.environ.get("CANDIDATES_TABLE", "ResumeScreeningCandidates")
        self.jobs_table_name = jobs_table_name or os.environ.get("JOBS_TABLE", "ResumeScreeningJobs")

        self.dynamodb = None
        self.candidates_table = None
        self.jobs_table = None
        self.use_mock = True

        # Check if AWS credentials or Local DynamoDB endpoint is available
        if boto3 and os.environ.get("USE_AWS_SERVICES", "false").lower() == "true":
            try:
                self.dynamodb = boto3.resource("dynamodb", region_name=self.region_name)
                self.candidates_table = self.dynamodb.Table(self.candidates_table_name)
                self.jobs_table = self.dynamodb.Table(self.jobs_table_name)
                # Test connectivity
                self.candidates_table.load()
                self.use_mock = False
                logger.info(f"Connected to AWS DynamoDB tables: {self.candidates_table_name}, {self.jobs_table_name}")
            except Exception as e:
                logger.warning(f"DynamoDB not available ({e}). Defaulting to in-memory/local JSON store.")
                self.use_mock = True

        # In-Memory fallback store
        self._mock_candidates: Dict[str, Dict[str, Any]] = {}
        self._mock_jobs: Dict[str, Dict[str, Any]] = {}
        self._active_job_id: Optional[str] = None
        self._init_default_mock_data()

    def _init_default_mock_data(self):
        """Seed initial job and sample candidates for immediate local UI demonstration."""
        default_job = {
            "job_id": "job-cloud-architect",
            "title": "Senior Cloud Solutions Architect",
            "department": "Cloud & Platform Engineering",
            "min_experience_years": 4.0,
            "required_skills": ["AWS", "Terraform", "Docker", "Kubernetes", "Python", "CI/CD"],
            "preferred_skills": ["DynamoDB", "Lambda", "Microservices", "System Design", "FastAPI"],
            "description": (
                "We are seeking an experienced Cloud Solutions Architect to build, "
                "automate, and deploy resilient enterprise cloud pipelines on AWS. "
                "Must have strong proficiency with Terraform, AWS Serverless (Lambda, DynamoDB, S3), "
                "container orchestration with Docker/Kubernetes, and automated CI/CD workflows."
            ),
            "created_at": "2026-11-01T10:00:00Z",
            "is_active": True,
        }
        self._mock_jobs[default_job["job_id"]] = default_job
        self._active_job_id = default_job["job_id"]

        sample_candidates = [
            {
                "candidate_id": "cand-001",
                "job_id": "job-cloud-architect",
                "name": "Sarah Jenkins",
                "email": "sarah.jenkins@example.com",
                "phone": "+1 (555) 234-5678",
                "filename": "Sarah_Jenkins_Cloud_Architect.pdf",
                "skills": ["AWS", "Terraform", "Docker", "Kubernetes", "Python", "CI/CD", "Lambda", "DynamoDB"],
                "experience_years": 6.5,
                "match_score": 94.5,
                "status": "Strong Match",
                "badge_color": "green",
                "matched_skills": ["AWS", "Terraform", "Docker", "Kubernetes", "Python", "CI/CD", "Lambda", "DynamoDB"],
                "missing_skills": [],
                "summary": "Outstanding candidate. Matched 8/8 target cloud skills with 6.5 years experience.",
                "uploaded_at": "2026-11-02T14:22:00Z",
                "breakdown": {
                    "skill_score_pct": 100.0,
                    "semantic_score_pct": 92.0,
                    "experience_score_pct": 100.0,
                    "candidate_experience_years": 6.5,
                    "required_experience_years": 4.0,
                },
                "education": ["B.S. in Computer Science - University of Washington"],
            },
            {
                "candidate_id": "cand-002",
                "job_id": "job-cloud-architect",
                "name": "Michael Chen",
                "email": "mchen.dev@example.com",
                "phone": "+1 (555) 876-5432",
                "filename": "Michael_Chen_DevOps.docx",
                "skills": ["AWS", "Docker", "Python", "CI/CD", "Git", "Linux", "FastAPI"],
                "experience_years": 4.0,
                "match_score": 82.0,
                "status": "Strong Match",
                "badge_color": "green",
                "matched_skills": ["AWS", "Docker", "Python", "CI/CD", "FastAPI"],
                "missing_skills": ["Terraform", "Kubernetes"],
                "summary": "Solid candidate with core cloud and Python proficiency; needs Terraform onboarding.",
                "uploaded_at": "2026-11-02T15:10:00Z",
                "breakdown": {
                    "skill_score_pct": 75.0,
                    "semantic_score_pct": 84.0,
                    "experience_score_pct": 100.0,
                    "candidate_experience_years": 4.0,
                    "required_experience_years": 4.0,
                },
                "education": ["M.S. in Software Engineering - San Jose State University"],
            },
            {
                "candidate_id": "cand-003",
                "job_id": "job-cloud-architect",
                "name": "Alex Rodriguez",
                "email": "alex.r@example.com",
                "phone": "+1 (555) 345-9876",
                "filename": "Alex_Rodriguez_WebDev.pdf",
                "skills": ["JavaScript", "React", "Node.js", "HTML5", "CSS3", "Docker", "Git"],
                "experience_years": 2.5,
                "match_score": 58.5,
                "status": "Low Match",
                "badge_color": "red",
                "matched_skills": ["Docker"],
                "missing_skills": ["AWS", "Terraform", "Kubernetes", "Python", "CI/CD"],
                "summary": "Frontend-heavy profile with minimal AWS cloud infrastructure background.",
                "uploaded_at": "2026-11-03T09:30:00Z",
                "breakdown": {
                    "skill_score_pct": 25.0,
                    "semantic_score_pct": 52.0,
                    "experience_score_pct": 62.5,
                    "candidate_experience_years": 2.5,
                    "required_experience_years": 4.0,
                },
                "education": ["B.Tech in Information Technology"],
            },
        ]
        for c in sample_candidates:
            self._mock_candidates[c["candidate_id"]] = c

    # ------------------ Candidate Operations ------------------ #

    def save_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save or update candidate record."""
        if not candidate_data.get("uploaded_at"):
            candidate_data["uploaded_at"] = datetime.now(timezone.utc).isoformat()

        if self.use_mock:
            self._mock_candidates[candidate_data["candidate_id"]] = candidate_data
            return candidate_data

        try:
            item = _convert_float_to_decimal(candidate_data)
            self.candidates_table.put_item(Item=item)
            return candidate_data
        except Exception as e:
            logger.error(f"Error saving candidate to DynamoDB: {e}")
            # Fallback to local store
            self._mock_candidates[candidate_data["candidate_id"]] = candidate_data
            return candidate_data

    def get_candidate(self, candidate_id: str, job_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve single candidate by ID."""
        if self.use_mock:
            return self._mock_candidates.get(candidate_id)

        try:
            if job_id:
                resp = self.candidates_table.get_item(Key={"job_id": job_id, "candidate_id": candidate_id})
            else:
                # Scan or query by candidate_id
                resp = self.candidates_table.scan(FilterExpression=Attr("candidate_id").eq(candidate_id))
                items = resp.get("Items", [])
                return _convert_decimal_to_float(items[0]) if items else None

            item = resp.get("Item")
            return _convert_decimal_to_float(item) if item else None
        except Exception as e:
            logger.error(f"Error fetching candidate {candidate_id}: {e}")
            return self._mock_candidates.get(candidate_id)

    def list_candidates(self, job_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List candidates sorted by match_score descending (Leaderboard)."""
        if self.use_mock:
            candidates = list(self._mock_candidates.values())
            if job_id:
                candidates = [c for c in candidates if c.get("job_id") == job_id]
            candidates.sort(key=lambda x: x.get("match_score", 0), reverse=True)
            return candidates[:limit]

        try:
            if job_id:
                resp = self.candidates_table.query(
                    KeyConditionExpression=Key("job_id").eq(job_id),
                    Limit=limit,
                )
                items = resp.get("Items", [])
            else:
                resp = self.candidates_table.scan(Limit=limit)
                items = resp.get("Items", [])

            converted = [_convert_decimal_to_float(item) for item in items]
            converted.sort(key=lambda x: x.get("match_score", 0), reverse=True)
            return converted
        except Exception as e:
            logger.error(f"Error listing candidates from DynamoDB: {e}")
            candidates = list(self._mock_candidates.values())
            if job_id:
                candidates = [c for c in candidates if c.get("job_id") == job_id]
            candidates.sort(key=lambda x: x.get("match_score", 0), reverse=True)
            return candidates[:limit]

    def delete_candidate(self, candidate_id: str, job_id: Optional[str] = None) -> bool:
        """Delete candidate by ID."""
        if self.use_mock:
            if candidate_id in self._mock_candidates:
                del self._mock_candidates[candidate_id]
                return True
            return False

        try:
            if not job_id:
                # Find job_id first
                cand = self.get_candidate(candidate_id)
                job_id = cand.get("job_id") if cand else "job-cloud-architect"

            self.candidates_table.delete_item(Key={"job_id": job_id, "candidate_id": candidate_id})
            if candidate_id in self._mock_candidates:
                del self._mock_candidates[candidate_id]
            return True
        except Exception as e:
            logger.error(f"Error deleting candidate {candidate_id}: {e}")
            if candidate_id in self._mock_candidates:
                del self._mock_candidates[candidate_id]
                return True
            return False

    # ------------------ Job Operations ------------------ #

    def save_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save or update a job description."""
        if not job_data.get("created_at"):
            job_data["created_at"] = datetime.now(timezone.utc).isoformat()

        job_id = job_data["job_id"]
        if self.use_mock:
            self._mock_jobs[job_id] = job_data
            if job_data.get("is_active"):
                self._active_job_id = job_id
            return job_data

        try:
            item = _convert_float_to_decimal(job_data)
            self.jobs_table.put_item(Item=item)
            if job_data.get("is_active"):
                self._active_job_id = job_id
            return job_data
        except Exception as e:
            logger.error(f"Error saving job to DynamoDB: {e}")
            self._mock_jobs[job_id] = job_data
            return job_data

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve job by ID."""
        if self.use_mock:
            return self._mock_jobs.get(job_id)

        try:
            resp = self.jobs_table.get_item(Key={"job_id": job_id})
            item = resp.get("Item")
            return _convert_decimal_to_float(item) if item else self._mock_jobs.get(job_id)
        except Exception as e:
            logger.error(f"Error fetching job {job_id}: {e}")
            return self._mock_jobs.get(job_id)

    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all available jobs."""
        if self.use_mock:
            return list(self._mock_jobs.values())

        try:
            resp = self.jobs_table.scan()
            items = [_convert_decimal_to_float(i) for i in resp.get("Items", [])]
            return items if items else list(self._mock_jobs.values())
        except Exception as e:
            logger.error(f"Error listing jobs from DynamoDB: {e}")
            return list(self._mock_jobs.values())

    def get_active_job(self) -> Dict[str, Any]:
        """Return the currently active job description for screening."""
        if self._active_job_id and self._active_job_id in self._mock_jobs:
            return self._mock_jobs[self._active_job_id]

        # Scan for is_active == True
        all_jobs = self.list_jobs()
        for j in all_jobs:
            if j.get("is_active"):
                return j
        return all_jobs[0] if all_jobs else self._mock_jobs.get("job-cloud-architect")
