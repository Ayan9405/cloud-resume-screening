"""Tests for NLP Entity and Skill Extraction."""

import pytest
from backend.services.nlp_extractor import NLPExtractor


def test_email_and_phone_extraction():
    extractor = NLPExtractor()
    sample_text = (
        "Alice Smith\n"
        "Email: alice.smith@example.com\n"
        "Phone: +1 555-123-4567\n"
        "LinkedIn: https://linkedin.com/in/alicesmith\n"
    )

    email = extractor.extract_email(sample_text)
    phone = extractor.extract_phone(sample_text)
    links = extractor.extract_links(sample_text)

    assert email == "alice.smith@example.com"
    assert "555" in phone
    assert "alicesmith" in links.get("linkedin", "")


def test_skills_extraction():
    extractor = NLPExtractor()
    sample_text = "Proficient in Python, AWS (S3, Lambda, DynamoDB), Terraform, Docker, and Kubernetes."
    skills = extractor.extract_skills(sample_text)

    expected = {"Python", "AWS", "S3", "Lambda", "DynamoDB", "Terraform", "Docker", "Kubernetes"}
    for exp in expected:
        assert exp in skills


def test_name_inference():
    extractor = NLPExtractor()
    text = "David Miller\nSenior Cloud Engineer\ndavid.miller@example.com"
    name = extractor.extract_name(text, email="david.miller@example.com")
    assert name == "David Miller"


def test_experience_extraction():
    extractor = NLPExtractor()
    text = "Senior Cloud Architect with 6+ years of experience in distributed systems."
    years, snippets = extractor.extract_experience(text)
    assert years == 6.0
