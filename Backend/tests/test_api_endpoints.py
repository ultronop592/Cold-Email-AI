import unittest
import sys
import os
import io

# Ensure Backend is on the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure GROQ_API_KEY is present for app initialization
os.environ.setdefault("GROQ_API_KEY", "test_key_placeholder")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestApiEndpoints(unittest.TestCase):

    def test_health_check_endpoint(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("service"), "Cold Email AI Backend")

    def test_root_endpoint(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertIn("docs", data)

    def test_upload_missing_job_url(self):
        file_content = b"%PDF-1.4 test content"
        response = client.post(
            "/generate-email",
            data={"job_url": "   "},
            files={"resume": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Job URL or Job Description is required", response.json().get("detail", ""))

    def test_upload_non_pdf_file(self):
        file_content = b"Plain text file"
        response = client.post(
            "/generate-email",
            data={"job_url": "https://linkedin.com/jobs/view/123"},
            files={"resume": ("resume.docx", io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("must be a PDF document", response.json().get("detail", ""))

    def test_upload_empty_pdf_file(self):
        response = client.post(
            "/generate-email",
            data={"job_url": "https://linkedin.com/jobs/view/123"},
            files={"resume": ("empty.pdf", io.BytesIO(b""), "application/pdf")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("empty", response.json().get("detail", "").lower())

    def test_upload_oversized_pdf_file(self):
        # 5 MB + 1 byte
        oversized = b"a" * (5 * 1024 * 1024 + 1)
        response = client.post(
            "/generate-email",
            data={"job_url": "https://linkedin.com/jobs/view/123"},
            files={"resume": ("large.pdf", io.BytesIO(oversized), "application/pdf")}
        )
        self.assertEqual(response.status_code, 413)
        self.assertIn("exceeds maximum allowed size", response.json().get("detail", ""))


if __name__ == "__main__":
    unittest.main()
