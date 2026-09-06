from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables first
load_dotenv()

# Validate API key on startup — fails loud instead of silently
if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("GROQ_API_KEY is not set. Check your Backend/.env file.")

app = FastAPI(
    title="Cold Email AI",
    description="Multi-agent cold email generator with tone matching and scoring",
    version="2.0.0"
)

# CORS — controls which frontends can call this backend
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
allowed_origins = (
    [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
    if allowed_origins_env
    else [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"]
)

from routes.generate_email import router
app.include_router(router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Cold Email AI Backend",
        "version": app.version
    }


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "healthy",
        "service": "Cold Email AI Backend",
        "version": app.version,
        "docs": "/docs"
    }