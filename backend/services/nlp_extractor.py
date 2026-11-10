"""NLP & Entity Extraction Service for Resume Screening.
Extracts contact information, technical skills, years of experience,
and education qualifications from parsed resume text.
Integrates with Amazon Comprehend when enabled or uses custom regex/NER heuristics.
"""

import os
import re
import logging
from typing import Dict, Any, List, Set, Optional

logger = logging.getLogger(__name__)

try:
    import boto3
except ImportError:
    boto3 = None


# Comprehensive technical skill taxonomy across Cloud, DevOps, AI, and Software Engineering
DEFAULT_SKILL_TAXONOMY = {
    # Cloud & Infrastructure
    "AWS", "Amazon Web Services", "EC2", "S3", "Lambda", "DynamoDB", "CloudFront", "IAM",
    "API Gateway", "ECS", "EKS", "Fargate", "CloudWatch", "Terraform", "CloudFormation",
    "Azure", "Google Cloud", "GCP", "Kubernetes", "Docker", "Ansible", "CI/CD", "GitHub Actions",
    "Jenkins", "GitLab CI", "Serverless", "OpenShift", "Helm",

    # Programming & Frameworks
    "Python", "JavaScript", "TypeScript", "Java", "Go", "Golang", "Rust", "C++", "C#",
    ".NET", "React", "React.js", "Next.js", "Node.js", "Express", "FastAPI", "Flask",
    "Django", "Spring Boot", "Tailwind CSS", "HTML5", "CSS3", "GraphQL", "REST API",
    "Vue.js", "Angular",

    # Databases & Big Data
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "DynamoDB",
    "Snowflake", "BigQuery", "Apache Spark", "Kafka", "SQL", "NoSQL", "Redshift",

    # Machine Learning & AI
    "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing", "PyTorch",
    "TensorFlow", "Scikit-Learn", "HuggingFace", "LangChain", "OpenAI", "Bedrock",
    "Computer Vision", "LLM", "Data Science", "Pandas", "NumPy",

    # Methodologies & Tools
    "Git", "Agile", "Scrum", "Microservices", "System Design", "Linux", "Bash", "Jira",
    "TDD", "OAuth", "JWT", "Security", "Monitoring", "Distributed Systems"
}


class NLPExtractor:
    """Extracts structured entities, skills, and qualifications from resume text."""

    def __init__(self, region_name: Optional[str] = None):
        self.region_name = region_name or os.environ.get("AWS_REGION", "us-east-1")
        self.skill_set = set(DEFAULT_SKILL_TAXONOMY)
        self.comprehend_client = None

        if boto3 and os.environ.get("USE_AWS_SERVICES", "false").lower() == "true":
            try:
                self.comprehend_client = boto3.client("comprehend", region_name=self.region_name)
            except Exception as e:
                logger.warning(f"Could not connect to AWS Comprehend: {e}. Using local regex/NER.")

    def extract_candidate_profile(self, text: str, filename: str = "") -> Dict[str, Any]:
        """Orchestrates extraction of all candidate attributes from resume text.

        Args:
            text: Raw extracted resume text.
            filename: Name of the uploaded file (used for fallback name inference).

        Returns:
            Dictionary with candidate details, skills, experience, and contact info.
        """
        email = self.extract_email(text)
        phone = self.extract_phone(text)
        name = self.extract_name(text, email, filename)
        links = self.extract_links(text)
        skills = self.extract_skills(text)
        experience_years, experience_snippets = self.extract_experience(text)
        education = self.extract_education(text)

        # Amazon Comprehend augmentation if available
        comprehend_entities = []
        if self.comprehend_client and text.strip():
            try:
                comprehend_entities = self._extract_comprehend_entities(text[:4500])
            except Exception as e:
                logger.warning(f"Comprehend extraction skipped: {e}")

        return {
            "name": name,
            "email": email or "not_found@example.com",
            "phone": phone or "N/A",
            "links": links,
            "skills": sorted(list(skills)),
            "experience_years": experience_years,
            "experience_snippets": experience_snippets[:4],
            "education": education,
            "comprehend_entities": comprehend_entities[:10],
            "text_preview": text[:500] if text else "",
        }

    def extract_email(self, text: str) -> Optional[str]:
        """Extract primary email address."""
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None

    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number formatted internationally or locally."""
        phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        matches = re.findall(phone_pattern, text)
        if matches:
            return matches[0].strip()
        return None

    def extract_links(self, text: str) -> Dict[str, str]:
        """Extract LinkedIn, GitHub, or portfolio website URLs."""
        links = {}
        linkedin = re.search(r"https?://(?:www\.)?linkedin\.com/in/[\w-]+", text, re.IGNORECASE)
        if linkedin:
            links["linkedin"] = linkedin.group(0)

        github = re.search(r"https?://(?:www\.)?github\.com/[\w-]+", text, re.IGNORECASE)
        if github:
            links["github"] = github.group(0)

        return links

    def extract_name(self, text: str, email: Optional[str] = None, filename: str = "") -> str:
        """Infer candidate's full name from text header or email."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Common stop-words that appear at the top of a resume that are not names
        blacklist = {
            "resume", "curriculum", "vitae", "cv", "page", "contact",
            "profile", "summary", "experience", "education", "skills",
            "objective", "email", "phone", "address"
        }

        # Strategy 1: Check the first 4 non-empty lines for a 2-3 word capitalized name
        for line in lines[:5]:
            clean_line = re.sub(r"[^A-Za-z\s]", "", line).strip()
            words = clean_line.split()
            if 2 <= len(words) <= 3:
                if not any(w.lower() in blacklist for w in words):
                    # Check if each word starts with a capital letter
                    if all(w[0].isupper() for w in words if w):
                        return clean_line

        # Strategy 2: Infer from filename (e.g. John_Doe_Resume.pdf -> John Doe)
        if filename:
            base = os.path.splitext(filename)[0]
            clean_base = re.sub(r"(?i)(resume|cv|latest|updated|final|doc|pdf|_|-|\d)", " ", base).strip()
            parts = clean_base.split()
            if 1 <= len(parts) <= 3 and all(p.isalpha() for p in parts):
                return " ".join([p.capitalize() for p in parts])

        # Strategy 3: Infer from email username
        if email:
            user_part = email.split("@")[0]
            clean_parts = re.split(r"[._-]", user_part)
            clean_parts = [p.capitalize() for p in clean_parts if p.isalpha() and len(p) > 1]
            if len(clean_parts) >= 2:
                return " ".join(clean_parts[:2])

        return "Candidate"

    def extract_skills(self, text: str, additional_skills: Optional[List[str]] = None) -> Set[str]:
        """Extract technical skills using case-insensitive token and boundary matching."""
        combined_skills = set(self.skill_set)
        if additional_skills:
            for s in additional_skills:
                combined_skills.add(s.strip())

        found_skills = set()
        text_lower = text.lower()

        for skill in combined_skills:
            # Word boundary matching to avoid partial substring hits (e.g., 'Go' vs 'Google')
            pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"
            if re.search(pattern, text_lower):
                found_skills.add(skill)

        return found_skills

    def extract_experience(self, text: str) -> (float, List[str]):
        """Calculate total years of experience and extract key role snippets."""
        # Detect explicit years statements like "5+ years of experience" or "7 years experience"
        explicit_matches = re.findall(
            r"(\d{1,2})\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience",
            text,
            re.IGNORECASE,
        )
        if explicit_matches:
            try:
                years = max([float(m) for m in explicit_matches])
                return years, self._extract_experience_snippets(text)
            except ValueError:
                pass

        # Detect year ranges like "2018 - 2023", "2020 - Present", "2019 to Present"
        range_pattern = r"\b(20\d\d|19\d\d)\s*(?:-|–|to)\s*(20\d\d|present|current)\b"
        ranges = re.findall(range_pattern, text, re.IGNORECASE)

        total_years = 0.0
        current_year = 2026

        for start_str, end_str in ranges:
            start_year = int(start_str)
            if end_str.lower() in ["present", "current"]:
                end_year = current_year
            else:
                end_year = int(end_str)

            diff = end_year - start_year
            if 0 <= diff <= 35:
                total_years += diff

        # Cap sensible maximum or default to estimated entry level
        calculated_years = min(round(total_years, 1), 30.0)
        if calculated_years == 0.0:
            calculated_years = 1.0  # sensible entry level baseline

        return calculated_years, self._extract_experience_snippets(text)

    def _extract_experience_snippets(self, text: str) -> List[str]:
        """Find bullet points or sentences that mention experience or accomplishments."""
        snippets = []
        for line in text.split("\n"):
            line_clean = line.strip()
            if len(line_clean) > 30 and any(
                kw in line_clean.lower()
                for kw in ["developed", "engineered", "built", "designed", "led", "managed", "implemented", "deployed"]
            ):
                snippets.append(line_clean)
        return snippets

    def extract_education(self, text: str) -> List[str]:
        """Extract degree qualifications and academic achievements."""
        degree_patterns = [
            r"\b(?:Ph\.?D|Doctor of Philosophy)\b.*",
            r"\b(?:M\.?S|M\.?Tech|Master(?:'s)?\s+of\s+[\w\s]+)\b.*",
            r"\b(?:B\.?S|B\.?Tech|B\.?E|Bachelor(?:'s)?\s+of\s+[\w\s]+)\b.*",
            r"\b(?:Computer Science|Information Technology|Software Engineering|Data Science)\b",
        ]
        found = []
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                clean_m = m.strip()[:80]
                if clean_m and clean_m not in found:
                    found.append(clean_m)
        return found[:3]

    def _extract_comprehend_entities(self, text_chunk: str) -> List[Dict[str, str]]:
        """Call AWS Comprehend batch_detect_entities for deeper semantic metadata."""
        if not self.comprehend_client:
            return []
        response = self.comprehend_client.detect_entities(
            Text=text_chunk,
            LanguageCode="en",
        )
        return [
            {"text": ent.get("Text"), "type": ent.get("Type")}
            for ent in response.get("Entities", [])
            if ent.get("Type") in ["ORGANIZATION", "PERSON", "LOCATION", "TITLE"]
        ]
