# Cold Email AI

Cold Email AI generates a tailored cold outreach email from:
- A job posting URL
- A candidate resume PDF

It provides:
- A FastAPI backend for scraping, parsing, generation, and scoring
- A Next.js frontend test console for end-to-end validation

## Current Behavior (Important)

The backend currently runs in a simplified, low-latency mode:
1. Scrape job text from URL
2. Parse resume PDF text
3. Make one LLM call for combined analysis + email generation
4. Compute score dashboard in Python
5. Return only email, improvements text, tips, scores, and missing skills

The active API response keys are:
- `email`
- `suggestion_text`
- `tips`
- `score_dashboard`
- `missing_skills`

## Project Structure

```text
Cold Email Product/
  Backend/
    app/
      main.py
    routes/
      generte_email.py
    services/
      ai_pipeline.py
      job_scraper.py
      resume_parser.py
      scorer.py
      memory_services.py
      reasoning_builder.py
    llms/
      groq_client.py
      combined_analyzer.py
      variants_generator.py
    db/
      chroma_client.py
    prompts/
    requirement.txt
  frontend/
    src/app/
    package.json
```

## Tech Stack

### Backend
- Python
- FastAPI + Uvicorn
- LangChain Core + langchain-groq
- Groq LLM API (`GROQ_MODEL`, default: `llama-3.3-70b-versatile`)
- requests + BeautifulSoup4 (job scraping)
- pdfplumber (resume PDF parsing)
- python-dotenv
- python-multipart
- ChromaDB + sentence-transformers (memory/semantic modules present)

### Frontend
- Next.js (App Router)
- React

## Backend Concepts

### Active request path
- `Backend/routes/generte_email.py`
  - Exposes `POST /generate-email`
  - Accepts `job_url` as `Form(...)` and `resume` as `File(...)`
- `Backend/services/ai_pipeline.py`
  - Orchestrates scrape -> parse -> analyze -> score
  - Uses a single LLM call for speed
- `Backend/llms/combined_analyzer.py`
  - Prompts the model for structured JSON output
  - Produces polished cold email format (greeting, opening, body, CTA, signoff)
  - Returns plain-text improvement block and quick tips
  - Sanitizes control characters before JSON parse
- `Backend/services/scorer.py`
  - Builds score dashboard with breakdown (match, ATS, resume, tone, overall)

### Supporting modules present in repository
- `Backend/services/memory_services.py`
  - Save/retrieve similar historical runs using ChromaDB
- `Backend/services/reasoning_builder.py`
  - Builds explainability/reasoning summaries from analysis outputs
- `Backend/llms/variants_generator.py`
  - Generates multi-style email variants with strategy reasoning
- `Backend/db/chroma_client.py`
  - Persistent ChromaDB collection setup

Note: these advanced modules exist and are useful for expanded workflows, but they are not in the current active low-latency response path.

## High-Level Architecture

1. Frontend form sends multipart data to `frontend/src/app/api/generate-email/route.js`.
2. Frontend proxy forwards to backend `POST /generate-email`.
3. Backend route calls `run_pipeline()`.
4. Pipeline returns minimal payload for fast UI rendering.
5. Frontend displays cold email, plain-text improvements, and score cards.

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

### 1. Create virtual environment

From project root:

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### 2. Install backend dependencies

```bash
pip install -r Backend/requirement.txt
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

## Run

Open two terminals from project root.

### Terminal A (Backend)

```bash
python -m uvicorn app.main:app --app-dir Backend --host 127.0.0.1 --port 8000
```

Backend URLs:
- Docs: `http://127.0.0.1:8000/docs`
- Endpoint: `POST /generate-email`

### Terminal B (Frontend)

```bash
cd frontend
npm run dev
```

Frontend URL:
- `http://127.0.0.1:3000`

## API Contract

### `POST /generate-email`

Request: `multipart/form-data`
- `job_url` (string, required)
- `resume` (PDF file, required)

Response: `application/json`

```json
{
  "email": "Hi Hiring Team,\n\n...\n\nBest regards,\nCandidate",
  "suggestion_text": "Improvements:\n- ...\n- ...\n\nQuick Tips:\n- ...\n- ...",
  "tips": ["...", "...", "..."],
  "score_dashboard": {
    "overall_score": 78,
    "overall_label": "Good",
    "breakdown": {
      "match_score": { "score": 80 },
      "ats_score": { "score": 75 },
      "resume_score": { "score": 79 },
      "tone_score": { "score": 76 }
    }
  },
  "missing_skills": ["skill_a", "skill_b"]
}
```

## Troubleshooting

- `422 Unprocessable Content`
  - Ensure request is multipart and includes both `job_url` and `resume`.
- Groq model/deprecation errors
  - Set `GROQ_MODEL` in `Backend/.env` to a currently supported model.
- Scraping failures on some job links
  - Some sites block bots or require auth; test with publicly accessible job pages.
- SSL verification issues during scrape
  - The scraper includes a fallback path for local/dev robustness.

## Notes

- The route file name is `generte_email.py` (current repository naming).
- The backend is optimized for response speed by reducing LLM calls to one per request.
