import unittest
import sys
import os

# Ensure Backend is on the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.resume_parser import (
    extract_contact_info,
    get_relevant_resume_text,
    parse_resume
)
from services.exceptions import ResumeParsingError


class TestResumeParser(unittest.TestCase):

    def setUp(self):
        self.sample_standard_resume = (
            "Jane Doe\n"
            "San Francisco, CA | (415) 555-0142 | jane.doe@example.com\n"
            "https://linkedin.com/in/janedoe | https://github.com/janedoe | https://janedoe.tech\n\n"
            "PROFESSIONAL SUMMARY\n"
            "Full stack software engineer with 5 years building scalable web systems.\n\n"
            "TECHNICAL SKILLS\n"
            "Languages: Python, TypeScript, JavaScript, SQL, Go\n"
            "Frameworks: FastAPI, React, Next.js, Node.js, Django\n"
            "DevOps & Cloud: Docker, Kubernetes, AWS, PostgreSQL, Redis\n\n"
            "EXPERIENCE\n"
            "Senior Software Engineer - Acme Corp (2022 - Present)\n"
            "- Architected microservices with FastAPI and Docker reducing latency by 42%.\n"
            "- Mentored 4 junior engineers and led migration to Kubernetes on AWS.\n\n"
            "Software Engineer - Beta Inc (2019 - 2022)\n"
            "- Designed React/Next.js frontend dashboards for 30,000 daily active users.\n"
            "- Optimized PostgreSQL database queries reducing CPU utilization by 28%.\n\n"
            "EDUCATION\n"
            "B.S. in Computer Science - University of California, Berkeley"
        )

    def test_extract_contact_info_all_fields(self):
        info = extract_contact_info(self.sample_standard_resume)
        self.assertEqual(info["name"], "Jane Doe")
        self.assertIn("jane.doe@example.com", info["emails"])
        self.assertTrue(any("415" in p for p in info["phones"]))
        self.assertTrue(any("linkedin.com/in/janedoe" in li for li in info["linkedin"]))
        self.assertTrue(any("github.com/janedoe" in gh for gh in info["github"]))
        self.assertTrue(any("janedoe.tech" in pf for pf in info["portfolios"]))

    def test_extract_contact_info_empty(self):
        info = extract_contact_info("")
        self.assertEqual(info["name"], "")
        self.assertEqual(info["emails"], [])
        self.assertEqual(info["phones"], [])
        self.assertEqual(info["linkedin"], [])
        self.assertEqual(info["github"], [])

    def test_standard_resume_retained_in_full(self):
        # A standard resume (< 3,500 chars) must be 100% preserved
        result = get_relevant_resume_text(self.sample_standard_resume, "Looking for Python FastAPI React developer")
        self.assertEqual(result, self.sample_standard_resume)
        self.assertIn("jane.doe@example.com", result)
        self.assertIn("janedoe.tech", result)
        self.assertIn("University of California, Berkeley", result)
        self.assertIn("latency by 42%", result)

    def test_long_resume_preserves_contact_and_skills(self):
        # Construct an extra-long resume (> 5,000 characters)
        long_sections = [
            (
                "Carlos Hernandez\n"
                "Austin, TX | 512-555-9012 | carlos.h@example.com\n"
                "https://linkedin.com/in/carlos-h | https://github.com/carlos-dev\n\n"
                "EXECUTIVE SUMMARY\n"
                "Principal Cloud Solutions Architect with 12+ years of enterprise architecture experience."
            ),
            (
                "CORE TECHNICAL SKILLS\n"
                "Cloud: AWS, Google Cloud (GCP), Microsoft Azure\n"
                "Containers & Orchestration: Docker, Kubernetes, Helm, Terraform\n"
                "Backend: Python, FastAPI, Go, Rust, Java, Spring Boot\n"
                "Data & Storage: PostgreSQL, Redis, Apache Kafka, Snowflake"
            )
        ]

        # Add filler career history chunks to exceed 5,000 characters
        for i in range(1, 15):
            long_sections.append(
                f"Role {i} - Enterprise Corp {i} (201{i} - 201{i+1})\n"
                f"Detailed job responsibilities for project {i}. Managed a team of engineers implementing "
                f"internal business processes and legacy database systems with custom tooling. "
                f"Maintained extensive internal documentation and compliance procedures across teams." * 3
            )

        long_resume_text = "\n\n".join(long_sections)
        self.assertGreater(len(long_resume_text), 5000)

        job_posting = "Looking for a Cloud Architect with AWS, Kubernetes, Terraform, Python, and Kafka."
        result = get_relevant_resume_text(long_resume_text, job_posting, max_chars=3500)

        # 1. Length within budget
        self.assertLessEqual(len(result), 3500)

        # 2. Contact details guaranteed
        self.assertIn("carlos.h@example.com", result)
        self.assertIn("linkedin.com/in/carlos-h", result)
        self.assertIn("github.com/carlos-dev", result)

        # 3. Core skills section prioritized
        self.assertIn("CORE TECHNICAL SKILLS", result)
        self.assertIn("Kubernetes", result)
        self.assertIn("Terraform", result)

    def test_chronological_ordering_preserved(self):
        # Ensure retained chunks are ordered sequentially as they appeared in original document
        header = "Alice Wong\nSenior Developer | alice@example.com\n"
        skills = "TECHNICAL SKILLS\nPython, Docker, AWS, Redis\n"
        early_role = "2023 - Recent Senior Engineer Role with FastAPI and Docker in production."
        mid_role = "2020 - Mid Engineer Role working with Python and PostgreSQL systems."
        old_role = "2018 - Junior Developer working with basic HTML and CSS."

        # Pad with filler so total exceeds max_chars
        filler = "Filler section describing miscellaneous administrative duties and attendance.\n" * 40
        long_resume = f"{header}\n\n{skills}\n\n{early_role}\n\n{filler}\n\n{mid_role}\n\n{filler}\n\n{old_role}"

        result = get_relevant_resume_text(long_resume, "Seeking Senior Engineer with FastAPI and Docker", max_chars=3000)

        # Check relative order: header -> skills -> early_role
        idx_header = result.find("Alice Wong")
        idx_skills = result.find("TECHNICAL SKILLS")
        idx_early = result.find("Recent Senior Engineer Role")

        self.assertNotEqual(idx_header, -1)
        self.assertNotEqual(idx_skills, -1)
        self.assertNotEqual(idx_early, -1)
        self.assertLess(idx_header, idx_skills)
        self.assertLess(idx_skills, idx_early)

    def test_parse_resume_empty_error(self):
        from io import BytesIO
        # Empty stream should raise ResumeParsingError
        with self.assertRaises(ResumeParsingError):
            parse_resume(BytesIO(b""))


if __name__ == "__main__":
    unittest.main()
