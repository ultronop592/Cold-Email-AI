from fastapi import APIRouter, UploadFile
from services.job_scraper import scrape_job
from services.resume_parser import parse_resume
from llm.email_generator import generate_email

router = APIRouter()

@router.post("/generate-email")

async def generate(url:str, resume:UploadFile):

    job_text = scrape_job(url)

    resume_text = parse_resume(resume.file)

    email = generate_email(
        job_text,
        resume_text
    )

    return {
        "email": email
    }