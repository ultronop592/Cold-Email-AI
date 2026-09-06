from fastapi import APIRouter, Form, File, UploadFile, Request, HTTPException
from fastapi.responses import JSONResponse
from services.rate_limiter import check_rate_limit
from services.ai_pipeline import run_pipeline
from services.exceptions import AppException
from app.logger import get_logger

logger = get_logger("routes.generate_email")

router = APIRouter()


@router.post("/generate-email")
async def generate_email(
    request: Request,
    job_url: str = Form(...),
    resume: UploadFile = File(...)
):
    clean_job_input = (job_url or "").strip()
    if not clean_job_input:
        raise HTTPException(status_code=400, detail="Job URL or Job Description is required.")

    is_url = clean_job_input.startswith("http://") or clean_job_input.startswith("https://")
    if not is_url and len(clean_job_input) < 30:
        raise HTTPException(
            status_code=400,
            detail="Provided job description is too short (minimum 30 characters required). If using a link, make sure it starts with http:// or https://."
        )

    if not resume or not resume.filename:
        raise HTTPException(status_code=400, detail="Resume PDF file is required.")

    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF document.")

    # Validate file size (max 5 MB)
    resume.file.seek(0, 2)
    file_size = resume.file.tell()
    resume.file.seek(0)

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded resume file is empty.")

    if file_size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Uploaded resume exceeds maximum allowed size of 5 MB."
        )

    # Get real client IP — check X-Forwarded-For first (set by Next.js proxy),
    # then fall back to direct connection IP
    forwarded = request.headers.get("x-forwarded-for")
    client_ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
    check_rate_limit(client_ip)

    try:
        result = await run_pipeline(job_url.strip(), resume.file)
        return result

    except HTTPException:
        # Re-raise FastAPI HTTP exceptions (such as rate limits) directly
        raise

    except AppException as exc:
        logger.warning("Application error during email generation: %s", exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    except Exception as exc:
        logger.error("Unhandled error processing email generation: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": f"An unexpected error occurred while generating your email: {str(exc)}"}
        )