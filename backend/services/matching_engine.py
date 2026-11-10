"""Matching Logic Algorithm for AI Resume & Document Screening.
Compares candidate vectors against job requirements using TF-IDF / Cosine Similarity,
exact and semantic skill matching, and experience scoring.
"""

import math
import logging
from typing import Dict, Any, List, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class MatchingEngine:
    """Computes similarity scores and fit evaluations between resumes and job postings."""

    def __init__(
        self,
        weight_skills: float = 0.45,
        weight_semantic: float = 0.40,
        weight_experience: float = 0.15,
    ):
        """Initialize weights for the composite scoring formula."""
        # Normalize weights if they do not sum to 1.0
        total = weight_skills + weight_semantic + weight_experience
        self.w_skills = weight_skills / total
        self.w_semantic = weight_semantic / total
        self.w_exp = weight_experience / total

    def evaluate_candidate(
        self,
        candidate_profile: Dict[str, Any],
        job_description: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Evaluates candidate against a job description.

        Args:
            candidate_profile: Dict with 'skills', 'experience_years', 'text_preview', etc.
            job_description: Dict with 'title', 'description', 'required_skills', 'min_experience_years'.

        Returns:
            Dict containing match_score (0-100), breakdown, matched/missing skills, status, and summary.
        """
        # 1. Skill Overlap Scoring
        candidate_skills = set([s.lower() for s in candidate_profile.get("skills", [])])
        job_required_skills = job_description.get("required_skills", [])
        job_preferred_skills = job_description.get("preferred_skills", [])

        matched_skills_list = []
        missing_skills_list = []

        # Check required skills
        req_count = len(job_required_skills)
        req_matched = 0
        for skill in job_required_skills:
            if skill.lower() in candidate_skills:
                req_matched += 1
                matched_skills_list.append(skill)
            else:
                missing_skills_list.append(skill)

        req_score = (req_matched / req_count) if req_count > 0 else 1.0

        # Check preferred skills
        pref_count = len(job_preferred_skills)
        pref_matched = 0
        for skill in job_preferred_skills:
            if skill.lower() in candidate_skills:
                pref_matched += 1
                if skill not in matched_skills_list:
                    matched_skills_list.append(skill)

        pref_score = (pref_matched / pref_count) if pref_count > 0 else 1.0

        # Skill score combines 75% required + 25% preferred
        skill_score = (req_score * 0.75) + (pref_score * 0.25)

        # 2. Semantic Vector Similarity (TF-IDF + Cosine Similarity)
        semantic_score = self._compute_semantic_similarity(
            candidate_text=candidate_profile.get("text_preview", "") + " " + " ".join(candidate_profile.get("skills", [])),
            job_text=job_description.get("description", "") + " " + job_description.get("title", "") + " " + " ".join(job_required_skills),
        )

        # 3. Experience Match Scoring
        candidate_exp = float(candidate_profile.get("experience_years", 1.0))
        required_exp = float(job_description.get("min_experience_years", 2.0))

        if required_exp <= 0:
            exp_score = 1.0
        elif candidate_exp >= required_exp:
            # Bonus for exceeding up to 1.15
            bonus = min(0.15, (candidate_exp - required_exp) * 0.03)
            exp_score = min(1.0 + bonus, 1.15)
        else:
            # Penalty proportional to missing years
            exp_score = max(0.2, candidate_exp / required_exp)

        # 4. Composite Final Score (0 - 100)
        raw_score = (
            (skill_score * self.w_skills)
            + (semantic_score * self.w_semantic)
            + (min(1.0, exp_score) * self.w_exp)
        ) * 100.0

        # Clamp between 0.0 and 100.0
        final_score = float(round(max(0.0, min(100.0, raw_score)), 1))

        # 5. Fit Classification
        if final_score >= 80.0:
            status = "Strong Match"
            badge_color = "green"
            verdict = "Recommended for Immediate Interview"
        elif final_score >= 60.0:
            status = "Moderate Match"
            badge_color = "yellow"
            verdict = "Under Review / Requires Technical Screening"
        else:
            status = "Low Match"
            badge_color = "red"
            verdict = "Does not meet core qualifications"

        summary = (
            f"Candidate scored {final_score}% overall. "
            f"Matched {len(matched_skills_list)}/{req_count + pref_count} target skills "
            f"with {candidate_exp} years of relevant experience "
            f"(target: {required_exp} years)."
        )

        return {
            "match_score": final_score,
            "status": status,
            "badge_color": badge_color,
            "verdict": verdict,
            "summary": summary,
            "breakdown": {
                "skill_score_pct": round(skill_score * 100, 1),
                "semantic_score_pct": round(semantic_score * 100, 1),
                "experience_score_pct": round(min(1.0, exp_score) * 100, 1),
                "candidate_experience_years": candidate_exp,
                "required_experience_years": required_exp,
            },
            "matched_skills": matched_skills_list,
            "missing_skills": missing_skills_list,
        }

    def _compute_semantic_similarity(self, candidate_text: str, job_text: str) -> float:
        """Compute cosine similarity of TF-IDF vectors between resume and job description."""
        if not candidate_text.strip() or not job_text.strip():
            return 0.40  # baseline neutral similarity

        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=5000,
            )
            tfidf_matrix = vectorizer.fit_transform([candidate_text, job_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # TF-IDF cosine similarities typically range between 0.1 to 0.7 for resumes;
            # scale gracefully with non-linear sigmoid-like adjustment for intuitive human score
            scaled = min(1.0, similarity * 1.6 + 0.15)
            return max(0.1, scaled)
        except Exception as e:
            logger.warning(f"Error computing TF-IDF similarity: {e}")
            return 0.5
