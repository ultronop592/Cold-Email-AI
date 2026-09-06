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
    # Validate inputs
    if not job_url or not job_url.strip():
        raise HTTPException(status_code=400, detail="Job URL or Job Description is required.")

    if not resume or not resume.filename:
        raise HTTPException(status_code=400, detail="Resume PDF file is required.")

    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF document.")

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