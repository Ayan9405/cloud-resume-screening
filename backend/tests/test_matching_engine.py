"""Tests for Matching Engine Scoring."""

import pytest
from backend.services.matching_engine import MatchingEngine


def test_matching_engine_high_match():
    engine = MatchingEngine()

    candidate = {
        "skills": ["AWS", "Terraform", "Docker", "Kubernetes", "Python", "CI/CD"],
        "experience_years": 5.0,
        "text_preview": "Experienced AWS Solutions Architect using Terraform, Kubernetes, and Python.",
    }

    job = {
        "title": "Cloud Architect",
        "min_experience_years": 4.0,
        "required_skills": ["AWS", "Terraform", "Docker", "Kubernetes", "Python"],
        "preferred_skills": ["CI/CD"],
        "description": "Looking for AWS and Terraform cloud architect with Kubernetes and Python background.",
    }

    result = engine.evaluate_candidate(candidate, job)

    assert result["match_score"] >= 80.0
    assert result["status"] == "Strong Match"
    assert "AWS" in result["matched_skills"]
    assert len(result["missing_skills"]) == 0


def test_matching_engine_low_match():
    engine = MatchingEngine()

    candidate = {
        "skills": ["HTML5", "CSS3", "Photoshop"],
        "experience_years": 1.0,
        "text_preview": "Graphic designer with HTML and CSS.",
    }

    job = {
        "title": "Principal Cloud Security Architect",
        "min_experience_years": 8.0,
        "required_skills": ["AWS", "Kubernetes", "Terraform", "Security"],
        "preferred_skills": ["Python"],
        "description": "Design secure AWS enterprise infrastructure.",
    }

    result = engine.evaluate_candidate(candidate, job)

    assert result["match_score"] < 50.0
    assert result["status"] == "Low Match"
    assert "AWS" in result["missing_skills"]
