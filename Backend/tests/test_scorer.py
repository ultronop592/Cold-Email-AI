import unittest
import sys
import os

# Ensure Backend is on the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.scorer import (
    extract_skills,
    extract_keywords,
    calculate_ats_score,
    calculate_tone_score,
    calculate_overall_score,
    build_score_dashboard,
    SKILL_ALIASES,
    BOILERPLATE_JOB_WORDS
)
from services.reasoning_builder import build_reasoning_summary


class TestScorer(unittest.TestCase):

    def test_extract_skills_aliases(self):
        text = "Experienced in K8s, JS, TS, ReactJS, and Golang backend development."
        skills = extract_skills(text)
        self.assertIn("kubernetes", skills)
        self.assertIn("javascript", skills)
        self.assertIn("typescript", skills)
        self.assertIn("react", skills)
        self.assertIn("go", skills)

    def test_extract_skills_multiword(self):
        text = "Hands-on experience with Large Language Models, Retrieval Augmented Generation, and System Design."
        skills = extract_skills(text)
        self.assertIn("large language models", skills)
        self.assertIn("rag", skills)
        self.assertIn("system design", skills)

    def test_extract_skills_symbols(self):
        text = "Strong background in C++, C#, and .NET Core with CI/CD deployment pipelines."
        skills = extract_skills(text)
        self.assertIn("c++", skills)
        self.assertIn("c#", skills)
        self.assertIn(".net", skills)
        self.assertIn("ci/cd", skills)

    def test_boilerplate_exclusion(self):
        boilerplate_text = "Exciting career opportunity seeking a dynamic engineer to join our passionate team."
        keywords = extract_keywords(boilerplate_text)
        for bp in ["opportunity", "seeking", "dynamic", "engineer", "team", "passionate", "career"]:
            self.assertNotIn(bp, keywords)

    def test_domain_keywords_extracted(self):
        tech_text = "Proficient in telemetry, concurrency, cryptography, and microfrontends."
        keywords = extract_keywords(tech_text)
        self.assertIn("telemetry", keywords)
        self.assertIn("concurrency", keywords)
        self.assertIn("cryptography", keywords)

    def test_ats_score_synonym_matching(self):
        job = "Looking for an engineer with Kubernetes, Amazon Web Services, and PostgreSQL."
        resume = "Senior developer proficient in K8s, AWS, and Postgres."
        result = calculate_ats_score(resume_text=resume, job_text=job)

        self.assertGreaterEqual(result["score"], 90)
        self.assertEqual(len(result["missing_keywords"]), 0)
        self.assertIn("Kubernetes", result["matched_keywords"])
        self.assertIn("AWS", result["matched_keywords"])
        self.assertIn("PostgreSQL", result["matched_keywords"])

    def test_ats_score_partial_match(self):
        job = "Requires Python, FastAPI, Docker, Kubernetes, and Terraform."
        resume = "Python developer with experience in FastAPI and Docker."
        result = calculate_ats_score(resume_text=resume, job_text=job)

        # 3 out of 5 skills matched (60% skill score)
        self.assertGreaterEqual(result["score"], 50)
        self.assertLessEqual(result["score"], 70)
        self.assertIn("Kubernetes", result["missing_keywords"])
        self.assertIn("Terraform", result["missing_keywords"])
        self.assertIn("Python", result["matched_keywords"])
        self.assertIn("FastAPI", result["matched_keywords"])
        self.assertIn("Docker", result["matched_keywords"])

    def test_ats_score_llm_skill_integration(self):
        job = "Job requirements for backend role."
        resume = "Candidate resume profile."
        key_skills = ["FastAPI", "Docker", "ChromaDB"]
        candidate_skills = ["FastAPI", "Docker"]
        missing_skills = ["ChromaDB"]

        result = calculate_ats_score(
            resume_text=resume,
            job_text=job,
            key_skills=key_skills,
            candidate_skills=candidate_skills,
            missing_skills=missing_skills
        )

        self.assertIn("ChromaDB", result["missing_keywords"])
        self.assertIn("FastAPI", result["matched_keywords"])
        self.assertIn("Docker", result["matched_keywords"])
        self.assertGreaterEqual(result["score"], 60)

    def test_ats_score_empty_inputs(self):
        # Empty job
        res1 = calculate_ats_score(resume_text="Python developer", job_text="")
        self.assertEqual(res1["score"], 0)
        self.assertEqual(res1["matched_keywords"], [])

        # Empty resume
        res2 = calculate_ats_score(resume_text="", job_text="Requires Python and Docker")
        self.assertEqual(res2["score"], 0)
        self.assertEqual(res2["matched_keywords"], [])
        self.assertIn("Python", res2["missing_keywords"])
        self.assertIn("Docker", res2["missing_keywords"])

    def test_build_score_dashboard_integration(self):
        job = "Senior Python engineer with FastAPI, Docker, and AWS experience."
        resume = "Python engineer with FastAPI and Docker."
        dashboard = build_score_dashboard(
            resume_text=resume,
            job_text=job,
            tone_profile={"formality": "semi-formal", "vocabulary": "technical", "example_phrases": ["scalable pipelines"]},
            variants=[{"email": "Hi, I built scalable pipelines with FastAPI and Docker."}],
            match_score=85,
            resume_score=80
        )

        self.assertIn("overall_score", dashboard)
        self.assertIn("breakdown", dashboard)
        ats = dashboard["breakdown"]["ats_score"]
        self.assertGreaterEqual(ats["score"], 60)
        self.assertIn("Python", ats["matched_keywords"])
        self.assertIn("AWS", ats["missing_keywords"])

    def test_reasoning_builder_ats_why(self):
        analysis = {
            "analysis_reasoning": {"overall_assessment": "Good fit", "biggest_strength": "Python", "biggest_gap": "AWS"},
            "job_analysis": {},
            "resume_analysis": {},
            "tone_profile": {"formality": "semi-formal", "vocabulary": "technical", "personality": ["technical"]},
            "suggestions": []
        }
        variants = []
        score_dashboard = {
            "breakdown": {
                "match_score": {"score": 85},
                "resume_score": {"score": 80},
                "tone_score": {"score": 75},
                "ats_score": {
                    "score": 90,
                    "matched_keywords": ["Python", "FastAPI", "Docker"],
                    "missing_keywords": []
                }
            }
        }
        summary = build_reasoning_summary(analysis, variants, score_dashboard)
        ats_why = summary["score_explanations"]["ats_score"]["why"]
        self.assertIn("All target skills were found in your resume!", ats_why)

    def test_ats_score_full_match_100(self):
        job = "Looking for a full stack engineer skilled in React, Node.js, TypeScript, PostgreSQL, and Docker."
        resume = "Full stack engineer with React.js, Node, TS, Postgres, and Docker in production."
        result = calculate_ats_score(resume_text=resume, job_text=job)

        self.assertEqual(result["score"], 100)
        self.assertEqual(len(result["missing_keywords"]), 0)
        self.assertIn("React", result["matched_keywords"])
        self.assertIn("Node.js", result["matched_keywords"])
        self.assertIn("TypeScript", result["matched_keywords"])
        self.assertIn("PostgreSQL", result["matched_keywords"])
        self.assertIn("Docker", result["matched_keywords"])

    def test_build_score_dashboard_with_llm_skills(self):
        dashboard = build_score_dashboard(
            resume_text="Senior engineer profile",
            job_text="Backend posting",
            tone_profile={"formality": "semi-formal", "vocabulary": "technical", "example_phrases": []},
            variants=[],
            match_score=90,
            resume_score=85,
            key_skills=["FastAPI", "PostgreSQL", "Redis", "Kafka"],
            candidate_skills=["FastAPI", "PostgreSQL"],
            missing_skills=["Redis", "Kafka"]
        )

        ats = dashboard["breakdown"]["ats_score"]
        self.assertEqual(ats["score"], 50)  # 2 of 4 skills matched
        self.assertIn("FastAPI", ats["matched_keywords"])
        self.assertIn("PostgreSQL", ats["matched_keywords"])
        self.assertIn("Redis", ats["missing_keywords"])
        self.assertIn("Apache Kafka", ats["missing_keywords"])


if __name__ == "__main__":
    unittest.main()
