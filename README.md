# Cold Email Generator AI

An intelligent cold email generation platform that scrapes job postings, parses resumes, and uses LLM-powered pipelines to craft personalized, metric-backed outreach emails — complete with scoring, reasoning, and strategy selection.

> Built with **FastAPI**, **LangChain**, **Groq LLMs**, **ChromaDB**, and **Next.js**.

---

## How It Works

The application runs a **multi-stage AI pipeline** that takes a job posting URL and a resume PDF, then produces two strategically different cold emails with full transparency into why each approach was chosen.

```
┌─────────────┐     ┌──────────────┐     ┌────────────────────┐     ┌──────────────┐
│  Job URL +   │────▶│  Scrape Job   │────▶│  LLM Call 1:       │────▶│  Score       │
│  Resume PDF  │     │  + Company    │     │  Analyze + Email   │     │  Dashboard   │
└─────────────┘     └──────────────┘     └────────────────────┘     └──────────────┘
                           │                        │                       │
                           ▼                        ▼                       ▼
                    ┌──────────────┐     ┌────────────────────┐     ┌──────────────┐
                    │  Parse Resume │     │  LLM Call 2:       │     │  Frontend    │
                    │  (RAG chunks) │     │  2 Strategy Emails │     │  Display     │
                    └──────────────┘     └────────────────────┘     └──────────────┘
```

### Pipeline Steps

| Step | Module | What It Does |
|------|--------|-------------|
| **1. Scrape Job** | `job_scraper.py` | Fetches job description text from any URL using `requests` + `BeautifulSoup`. Also attempts to scrape company `/about` pages for tone analysis. |
| **2. Parse Resume** | `resume_parser.py` | Extracts text from PDF using `pdfplumber`, then splits it into chunks using LangChain's `RecursiveCharacterTextSplitter`. Only the top 3 most relevant chunks (scored by keyword overlap with the job) are sent to the LLM — this is **RAG applied to resume parsing**. |
| **3. Analyze & Write** | `combined_analyzer.py` | **LLM Call 1** — A single structured prompt asks the model to: analyze job-resume fit, score the match, identify missing skills, generate improvement tips, and write one polished cold email. Returns structured JSON via Pydantic schemas. |
| **4. Generate Variants** | `variants_generator.py` | **LLM Call 2** — Generates exactly 2 strategically different email variants: an **Achievement Lead** (opens with metrics) and a **Problem Solver** (opens with a company challenge). Each variant includes AI reasoning explaining the strategy choice. |
| **5. Score** | `scorer.py` | Pure Python scoring — no LLM call. Computes 4 scores: **Match Score** (from LLM), **ATS Score** (keyword overlap), **Resume Score** (from LLM), and **Tone Score** (checks if email matches company communication style). Produces a weighted overall score. |
| **6. Memory** | `memory_services.py` | Saves each generation to **ChromaDB** for semantic retrieval. Can find similar past jobs to use as few-shot examples (available for future pipeline enhancements). |

---

## Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| **Python 3.11+** | Core language |
| **FastAPI + Uvicorn** | Async web framework + ASGI server |
| **LangChain** | Prompt templates, output parsers, text splitters |
| **langchain-groq** | Groq LLM integration |
| **Groq API** | Ultra-fast LLM inference (`llama-3.3-70b-versatile`) |
| **Pydantic** | Structured JSON output schemas |
| **pdfplumber** | PDF resume text extraction |
| **BeautifulSoup4** | HTML scraping for job descriptions |
| **ChromaDB** | Vector database for generation memory |
| **python-dotenv** | Environment variable management |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **Next.js 16** (App Router) | React framework with SSR |
| **React** | UI components |
| **Tailwind CSS** | Utility-first styling |
| **Lucide React** | Icon library |

### Deployment
| Technology | Purpose |
|-----------|---------|
| **Docker** | Containerized backend |
| **Render** | Cloud deployment (render.yaml Blueprint) |

---

## Project Structure

```
Cold Email Product/
├── Backend/
│   ├── app/
│   │   └── main.py                  # FastAPI app setup, CORS, router
│   ├── routes/
│   │   └── generte_email.py         # POST /generate-email endpoint
│   ├── services/
│   │   ├── ai_pipeline.py           # Orchestrates the full pipeline
│   │   ├── job_scraper.py           # Scrapes job + company pages
│   │   ├── resume_parser.py         # PDF parsing + RAG chunking
│   │   ├── scorer.py                # ATS, tone, match, overall scoring
│   │   ├── memory_services.py       # ChromaDB save/retrieve
│   │   ├── reasoning_builder.py     # Explainability summaries
│   │   └── rate_limiter.py          # IP-based rate limiting
│   ├── llms/
│   │   ├── groq_client.py           # LLM client config + logging
│   │   ├── combined_analyzer.py     # LLM Call 1: analysis + email
│   │   ├── variants_generator.py    # LLM Call 2: 2 strategy variants
│   │   └── schemas.py              # Pydantic output models
│   ├── db/
│   │   └── chroma_client.py         # ChromaDB persistent client
│   ├── prompts/
│   │   └── email_client.txt         # Reference prompt template
│   ├── Dockerfile                   # Docker container config
│   ├── requirement.txt              # Python dependencies
│   ├── .env                         # API keys (not committed)
│   └── .env.example                 # Template for .env
├── frontend/
│   ├── src/app/
│   │   ├── page.js                  # Main UI — hero + email generator
│   │   ├── globals.css              # Global styles (light SaaS theme)
│   │   ├── layout.js                # Root layout + fonts
│   │   └── api/generate-email/
│   │       └── route.js             # API proxy to backend
│   ├── package.json
│   └── next.config.mjs
├── render.yaml                      # Render deployment blueprint
└── README.md
```

---

## How the LLM Prompts Work

### LLM Call 1: Combined Analyzer
A single structured prompt performs **three tasks simultaneously**:
1. **Fit Analysis** — Extracts role details, candidate skills, tone profile, match score, resume score, missing skills
2. **Score Reasoning** — Explains why each score was given (biggest strength, biggest gap)
3. **Primary Email** — Writes a polished cold email following a strict structure: Hook → Value Bridge → Curiosity Gap → CTA

The prompt enforces **anti-patterns** (e.g., never say "I hope this finds you well") and requires the candidate's real name from the resume.

### LLM Call 2: Variants Generator
Generates exactly **2 email variants** with distinct strategies:
- **Variant 1 (Achievement Lead)** — Opens with the candidate's most impressive metric
- **Variant 2 (Problem Solver)** — Identifies a company challenge and positions the candidate as the solution

Each variant includes **AI reasoning**: `why_this_opening` and `key_strength_used`.

### LLM Configuration
Two separate `ChatGroq` clients are used:
- `llm` (temp=0.3, 800 tokens) — For analysis (needs precision)
- `llm_large` (temp=0.7, 1500 tokens) — For email variants (needs creativity)

Both include a `PipelineLogger` callback that tracks token usage, latency, and errors.

---

## Scoring System

| Score | Weight | How It's Calculated |
|-------|--------|-------------------|
| **Match Score** | 35% | LLM-assessed fit between resume and job requirements |
| **ATS Score** | 30% | Keyword overlap between job description and resume (Python regex) |
| **Resume Score** | 20% | LLM-assessed overall resume strength for this role |
| **Tone Score** | 15% | Checks if generated emails match company tone (formality, vocabulary, phrases) |

**Overall Score** = Weighted average → labeled as Excellent (85+), Good (70+), Fair (55+), or Needs Work.

---

## API Contract

### `POST /generate-email`

**Request:** `multipart/form-data`
- `job_url` (string, required) — URL of any job posting
- `resume` (PDF file, required) — Candidate resume

**Response:** `application/json`
```json
{
  "email": "Full polished email text...",
  "email_format": {
    "greeting": "Hi [Name],",
    "opening": "...",
    "body": "...",
    "cta": "...",
    "signoff": "Best regards, Candidate Name"
  },
  "variants": [
    {
      "style": "achievement",
      "email": "Subject: ... \n\nDear Hiring Manager,...",
      "reasoning": {
        "strategy": "achievement",
        "why_this_opening": "...",
        "key_strength_used": "..."
      }
    },
    {
      "style": "problem_solver",
      "email": "Subject: ... \n\nDear Sir/Madam,...",
      "reasoning": { "..." }
    }
  ],
  "score_dashboard": {
    "overall_score": 78,
    "overall_label": "Good",
    "breakdown": {
      "match_score": { "score": 80, "label": "Good" },
      "ats_score": { "score": 75, "matched_keywords": [], "missing_keywords": [] },
      "resume_score": { "score": 79 },
      "tone_score": { "score": 76 }
    }
  },
  "job_analysis": { "role": "...", "company": "...", "key_skills_required": [] },
  "resume_analysis": { "candidate_name": "...", "strongest_skills": [] },
  "suggestion_text": "- Improvement 1\n- Improvement 2",
  "tips": ["Tip 1", "Tip 2", "Tip 3"],
  "missing_skills": ["skill_a", "skill_b"]
}
```

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- A [Groq API key](https://console.groq.com)

### 1. Clone & Create Virtual Environment

```bash
git clone <repo-url>
cd "Cold Email Product"
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### 2. Install Backend Dependencies

```bash
pip install -r Backend/requirement.txt
```

### 3. Configure Environment Variables

Create `Backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
# Optional: override default model
# GROQ_MODEL=llama-3.3-70b-versatile
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Run Development Servers

**Terminal A — Backend:**
```bash
python -m uvicorn app.main:app --app-dir Backend --host 127.0.0.1 --port 8000
```

**Terminal B — Frontend:**
```bash
cd frontend
npm run dev
```

**URLs:**
- Frontend: `http://localhost:3000`
- Backend API Docs: `http://localhost:8000/docs`

---

## Deployment

### Deploy Backend to Render

The project includes a `Dockerfile` and `render.yaml` for one-step deployment:

1. Push code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com) → **New+ → Blueprint**
3. Connect your repository — Render reads `render.yaml` automatically
4. Set `GROQ_API_KEY` as an environment variable in the Render dashboard

### Deploy Frontend to Vercel

```bash
cd frontend
npx vercel
```

Set `BACKEND_API_URL` environment variable to your deployed backend URL.

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| `422 Unprocessable Content` | Ensure request is multipart with both `job_url` and `resume` |
| `GROQ_API_KEY is not set` | Create `Backend/.env` with your API key |
| Groq model errors | Set `GROQ_MODEL` in `.env` to a supported model |
| Scraping failures | Some sites block bots — test with publicly accessible job pages |
| ChromaDB sqlite errors | Ensure Python 3.11+ (ChromaDB needs sqlite 3.35+) |

---

## License

MIT
