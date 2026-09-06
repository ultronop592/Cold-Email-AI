import unittest
import sys
import os
import asyncio

# Ensure Backend is on the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.job_scraper import (
    extract_linkedin_job_id,
    detect_job_board,
    extract_company_base_url,
    extract_greenhouse_info,
    extract_lever_info,
    extract_json_ld_job_posting,
    scrape_jobs_async,
    clean_html_text,
    KNOWN_JOB_BOARDS
)
from services.exceptions import ScrapingError


class TestJobScraper(unittest.TestCase):

    def test_extract_linkedin_job_id_formats(self):
        urls = {
            "https://www.linkedin.com/jobs/view/4028456123/": "4028456123",
            "https://www.linkedin.com/jobs/view/senior-software-engineer-at-stripe-4028456123": "4028456123",
            "https://www.linkedin.com/jobs/search/?currentJobId=4028456123&keywords=python": "4028456123",
            "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4028456123": "4028456123",
            "https://linkedin.com/jobs/view/4028456123?refId=abc": "4028456123",
            "https://www.linkedin.com/feed/": None,
            "https://example.com/jobs/12345": None
        }
        for url, expected in urls.items():
            self.assertEqual(extract_linkedin_job_id(url), expected, f"Failed for {url}")

    def test_detect_job_board(self):
        self.assertEqual(detect_job_board("https://www.linkedin.com/jobs/view/123"), "linkedin")
        self.assertEqual(detect_job_board("https://boards.greenhouse.io/stripe/jobs/456"), "greenhouse")
        self.assertEqual(detect_job_board("https://jobs.lever.co/figma/789"), "lever")
        self.assertEqual(detect_job_board("https://jobs.ashbyhq.com/openai/101"), "ashby")
        self.assertEqual(detect_job_board("https://apply.workable.com/revolut/j/102"), "workable")
        self.assertEqual(detect_job_board("https://www.indeed.com/viewjob?jk=103"), "indeed")
        self.assertEqual(detect_job_board("https://stripe.com/careers"), "generic")

    def test_extract_company_base_url_skips_job_boards(self):
        # Job boards must NOT be used as company website for tone scraping
        self.assertEqual(extract_company_base_url("https://www.linkedin.com/jobs/view/123"), "")
        self.assertEqual(extract_company_base_url("https://boards.greenhouse.io/stripe/jobs/456"), "")
        self.assertEqual(extract_company_base_url("https://jobs.lever.co/figma/789"), "")
        self.assertEqual(extract_company_base_url("https://www.indeed.com/viewjob?jk=103"), "")

        # Real company career sites should be permitted
        self.assertEqual(extract_company_base_url("https://careers.airbnb.com/positions/123"), "https://careers.airbnb.com")
        self.assertEqual(extract_company_base_url("https://about.gitlab.com/jobs/123"), "https://about.gitlab.com")

    def test_greenhouse_and_lever_info_extraction(self):
        gh = extract_greenhouse_info("https://boards.greenhouse.io/stripe/jobs/8172487")
        self.assertEqual(gh, ("stripe", "8172487"))

        lever = extract_lever_info("https://jobs.lever.co/acme-corp/a1b2c3d4-e5f6")
        self.assertEqual(lever, ("acme-corp", "a1b2c3d4-e5f6"))

    def test_direct_text_bypass(self):
        sample_jd = (
            "Senior Backend Engineer - Distributed Systems\n"
            "We are looking for a Senior Backend Engineer proficient in Python, FastAPI, and Docker.\n"
            "Responsibilities: Build scalable microservices, manage PostgreSQL databases, deploy on AWS."
        )
        result = asyncio.run(scrape_jobs_async(sample_jd))
        self.assertEqual(result, sample_jd)

    def test_direct_text_too_short_raises(self):
        with self.assertRaises(ScrapingError):
            asyncio.run(scrape_jobs_async("Too short"))

    def test_json_ld_job_posting_extraction(self):
        sample_html = """
        <html>
        <head>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "JobPosting",
            "title": "Principal AI Engineer",
            "description": "<p>Build agentic AI workflows with Python and LangChain.</p>",
            "hiringOrganization": {
                "@type": "Organization",
                "name": "Anthropic",
                "sameAs": "https://anthropic.com"
            }
        }
        </script>
        </head>
        <body>Job page</body>
        </html>
        """
        data = extract_json_ld_job_posting(sample_html)
        self.assertIsNotNone(data)
        self.assertEqual(data.get("title"), "Principal AI Engineer")
        self.assertEqual(data.get("hiringOrganization", {}).get("name"), "Anthropic")


if __name__ == "__main__":
    unittest.main()
