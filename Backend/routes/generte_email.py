from fastapi import APIRouter, UploadFile
from services.ai_pipeline import run_pipeline

router = APIRouter()

@router.post("/generate-email")

async def generate(job_url: str, resume: UploadFile):

    result = run_pipeline(
        job_url,
        resume.file
    )

    return result