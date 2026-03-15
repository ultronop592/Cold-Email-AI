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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*" 
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"]
)

from routes.generte_email import router
app.include_router(router)