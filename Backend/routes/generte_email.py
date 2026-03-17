from fastapi import APIRouter, Form, File, UploadFile, Request
from fastapi.responses import JSONResponse
from services.rate_limiter import check_rate_limit
from services.ai_pipeline import run_pipeline
import traceback

router = APIRouter()

@router.post("/generate-email")
async def generate_email(
    request: Request,
    job_url: str = Form(...),
    resume: UploadFile = File(...)
):
    # Get real client IP — check X-Forwarded-For first (set by Next.js proxy),
    # then fall back to direct connection IP
    forwarded = request.headers.get("x-forwarded-for")
    client_ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
    check_rate_limit(client_ip)

    try:
        result = run_pipeline(job_url, resume.file)
        return result
    except Exception as e:
        tb = traceback.format_exc()
        print(f"\n[PIPELINE ERROR]\n{tb}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "traceback": tb}
        )