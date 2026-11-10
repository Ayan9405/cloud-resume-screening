"""Tests for API Endpoints and DynamoDB Service."""

import pytest
from backend.services.dynamodb_service import DynamoDBService
from backend.handlers.presigned_url_handler import generate_presigned_url


def test_dynamodb_crud_operations():
    db = DynamoDBService()

    # Test candidate listing
    candidates = db.list_candidates()
    assert len(candidates) >= 1
    # Check sorted descending
    scores = [c["match_score"] for c in candidates]
    assert scores == sorted(scores, reverse=True)

    # Test save candidate
    new_candidate = {
        "candidate_id": "test-cand-999",
        "job_id": "job-cloud-architect",
        "name": "Test Candidate",
        "email": "test@example.com",
        "match_score": 88.0,
        "skills": ["AWS", "Python"],
    }
    saved = db.save_candidate(new_candidate)
    assert saved["candidate_id"] == "test-cand-999"

    # Test get candidate
    fetched = db.get_candidate("test-cand-999")
    assert fetched is not None
    assert fetched["name"] == "Test Candidate"

    # Test delete candidate
    deleted = db.delete_candidate("test-cand-999")
    assert deleted is True
    assert db.get_candidate("test-cand-999") is None


def test_presigned_url_generation():
    res = generate_presigned_url("test_resume.pdf", "application/pdf")
    assert "upload_url" in res
    assert "s3_key" in res
    assert res["s3_key"].endswith("test_resume.pdf")


def test_invalid_file_extension():
    with pytest.raises(ValueError):
        generate_presigned_url("malicious_executable.exe", "application/octet-stream")
