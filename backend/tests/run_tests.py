"""Self-contained test runner using Python's standard unittest library."""

import os
import sys
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.services.document_parser import DocumentParser
from backend.services.nlp_extractor import NLPExtractor
from backend.services.matching_engine import MatchingEngine
from backend.services.dynamodb_service import DynamoDBService
from backend.handlers.presigned_url_handler import generate_presigned_url
from backend.handlers.s3_trigger_handler import process_resume_payload


class TestDocumentParser(unittest.TestCase):
    def setUp(self):
        self.parser = DocumentParser()

    def test_plain_text_extraction(self):
        sample = "John Doe\nSoftware Engineer\nPython, AWS, Docker"
        res = self.parser.extract_text(sample.encode("utf-8"), "resume.txt")
        self.assertEqual(res["status"], "success")
        self.assertIn("John Doe", res["text"])
        self.assertIn("Python", res["text"])

    def test_empty_content(self):
        res = self.parser.extract_text(b"", "empty.txt")
        self.assertEqual(res["text"], "")


class TestNLPExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = NLPExtractor()

    def test_contact_extraction(self):
        sample = "Alice Smith\nEmail: alice.smith@example.com\nPhone: +1 555-123-4567\n"
        email = self.extractor.extract_email(sample)
        phone = self.extractor.extract_phone(sample)
        self.assertEqual(email, "alice.smith@example.com")
        self.assertIn("555", phone)

    def test_skills_extraction(self):
        sample = "Proficient in Python, AWS, Terraform, Docker, and Kubernetes."
        skills = self.extractor.extract_skills(sample)
        self.assertTrue({"Python", "AWS", "Terraform", "Docker", "Kubernetes"}.issubset(skills))

    def test_experience_extraction(self):
        sample = "Lead Architect with 6+ years of experience in cloud computing."
        years, _ = self.extractor.extract_experience(sample)
        self.assertEqual(years, 6.0)


class TestMatchingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MatchingEngine()

    def test_high_match_scoring(self):
        cand = {
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
        res = self.engine.evaluate_candidate(cand, job)
        self.assertGreaterEqual(res["match_score"], 80.0)
        self.assertEqual(res["status"], "Strong Match")
        self.assertIn("AWS", res["matched_skills"])

    def test_low_match_scoring(self):
        cand = {
            "skills": ["HTML5", "CSS3"],
            "experience_years": 1.0,
            "text_preview": "Junior designer with basic HTML and CSS.",
        }
        job = {
            "title": "Principal AWS Cloud Security Architect",
            "min_experience_years": 8.0,
            "required_skills": ["AWS", "Kubernetes", "Terraform", "Security"],
            "preferred_skills": ["Python"],
            "description": "Design secure AWS enterprise infrastructure.",
        }
        res = self.engine.evaluate_candidate(cand, job)
        self.assertLess(res["match_score"], 60.0)
        self.assertEqual(res["status"], "Low Match")


class TestDynamoDBService(unittest.TestCase):
    def setUp(self):
        self.db = DynamoDBService()

    def test_crud_and_sorting(self):
        candidates = self.db.list_candidates()
        self.assertGreaterEqual(len(candidates), 1)
        scores = [c["match_score"] for c in candidates]
        self.assertEqual(scores, sorted(scores, reverse=True))

        # Save & Fetch
        cand_id = "test-cand-abc"
        self.db.save_candidate({
            "candidate_id": cand_id,
            "job_id": "job-cloud-architect",
            "name": "Integration Tester",
            "email": "tester@example.com",
            "match_score": 91.5,
            "skills": ["Python", "AWS"],
        })
        cand = self.db.get_candidate(cand_id)
        self.assertIsNotNone(cand)
        self.assertEqual(cand["name"], "Integration Tester")

        # Delete
        self.assertTrue(self.db.delete_candidate(cand_id))
        self.assertIsNone(self.db.get_candidate(cand_id))


class TestPipelineIntegration(unittest.TestCase):
    def test_full_pipeline_run(self):
        raw_resume = (
            "Alex Morgan\n"
            "alex.morgan@example.com | +1 555-890-1234\n"
            "Senior Cloud Solutions Architect with 5+ years of experience in AWS, Terraform, Docker, Kubernetes, Python, and CI/CD.\n"
            "Built automated serverless pipelines using AWS Lambda and DynamoDB. Deployed microservices on EKS.\n"
        )
        saved = process_resume_payload(
            file_bytes=raw_resume.encode("utf-8"),
            filename="Alex_Morgan_Resume.txt",
            s3_bucket="unit-test-bucket",
            s3_key="resumes/Alex_Morgan_Resume.txt",
            job_id="job-cloud-architect",
        )
        self.assertEqual(saved["name"], "Alex Morgan")
        self.assertEqual(saved["email"], "alex.morgan@example.com")
        self.assertGreaterEqual(saved["match_score"], 70.0)
        self.assertIn("AWS", saved["skills"])


if __name__ == "__main__":
    unittest.main()
