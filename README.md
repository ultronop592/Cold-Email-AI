# Cold Email AI

Cold Email AI helps job seekers generate a tailored cold email from a job posting URL and a resume PDF.

It includes:
- A FastAPI backend for scraping, parsing, and AI generation.
- A Next.js frontend test console to upload a resume, submit a job URL, and view generated outputs.

## What This Project Does

Given a `job_url` and a resume PDF, the system:
1. Scrapes text from the job page.
2. Extracts text from the uploaded resume PDF.
3. Analyzes the job details.
4. Analyzes the resume profile.
5. Generates a cold outreach email.
6. Suggests profile improvements and missing skills.

The API response includes:
- `email`
- `suggestions`
- `job_analysis`
- `resume_analysis`

## Project Structure

```text
Cold Email Product/
  Backend/
    app/
    routes/
    services/
    llms/
    prompts/
    requirement.txt
  frontend/
    src/app/
    package.json
```

## Tech Stack

### Backend
- Python
- FastAPI
- Uvicorn
- LangChain + langchain-groq
- Groq LLM API
- ChromaDB
- sentence-transformers
- requests + BeautifulSoup4 (job page scraping)
- pdfplumber (resume PDF parsing)
- python-dotenv
- python-multipart

### Frontend
- Next.js (App Router)
- React
- ESLint

## Architecture (High-Level)

1. Frontend form sends multipart data to `frontend/src/app/api/generate-email/route.js`.
2. Frontend API route proxies request to backend `POST /generate-email`.
3. Backend route calls `run_pipeline()` in `Backend/services/ai_pipeline.py`.
4. Pipeline returns generated email + analyses + suggestions.
5. Frontend renders results in the test console UI.

## Environment Variables

### Backend (`Backend/.env`)
Create `Backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
# Optional override
# GROQ_MODEL=llama-3.3-70b-versatile
```

### Frontend (`frontend/.env.local`)
Optional (defaults to local backend):

```env
BACKEND_API_URL=http://127.0.0.1:8000
```

## Setup

### 1. Clone and open project

```bash
git clone https://github.com/ultronop592/Cold-Email-AI.git
cd Cold-Email-AI
```

### 2. Backend setup

From project root:

```bash
python -m venv .venv
```

Activate virtual environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r Backend/requirement.txt
```

### 3. Frontend setup

```bash
cd frontend
npm install
cd ..
```

## Run the Application

Open two terminals from project root.

### Terminal A: Run backend

```bash
# Ensure venv is active first
python -m uvicorn app.main:app --app-dir Backend --host 127.0.0.1 --port 8000
```

Backend endpoints:
- API docs: `http://127.0.0.1:8000/docs`
- Main generation endpoint: `POST /generate-email`

### Terminal B: Run frontend

```bash
cd frontend
npm run dev
```

Frontend URL:
- `http://127.0.0.1:3000`

## How to Use

1. Open `http://127.0.0.1:3000`.
2. Enter a job post URL.
3. Upload resume PDF.
4. Click `Test API`.
5. Review generated email, suggestions, and analyses.

## API Contract

### `POST /generate-email`

Request: `multipart/form-data`
- `job_url` (string, required)
- `resume` (file, required)

Response: `application/json`

```json
{
  "email": "...",
  "suggestions": "...",
  "job_analysis": "...",
  "resume_analysis": "..."
}
```

## Notes and Troubleshooting

- If you get `422 Unprocessable Content`, ensure request is multipart with both `job_url` and `resume`.
- If you get model errors from Groq, set `GROQ_MODEL` in `Backend/.env` to a currently supported model.
- Some job portals may block scraping or require authentication; try accessible job URLs.
- If SSL certificate verification fails while scraping, the backend includes a fallback path for local development.

## Future Improvements

- Structured JSON outputs for analysis fields.
- Better scraping adapters per job platform (LinkedIn, Indeed, etc.).
- Authentication and usage limits.
- Docker setup for one-command local startup.
