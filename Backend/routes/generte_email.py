from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from services.ai_pipeline import run_pipeline

router = APIRouter()

@router.post("/generate-email")

async def generate(
    job_url: str = Form(...),
    resume: UploadFile = File(...),
):
    try:
        result = run_pipeline(
            job_url,
            resume.file
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {exc}") from exc