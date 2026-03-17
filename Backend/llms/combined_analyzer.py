import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from llms.groq_client import llm
from llms.schemas import CombinedAnalysis

parser = JsonOutputParser(pydantic_object=CombinedAnalysis)

COMBINED_TEMPLATE = """
You are an elite outreach strategist, cold-email copywriter, and hiring-fit analyst.

You will receive a JOB DESCRIPTION, CANDIDATE RESUME, and optional COMPANY PAGE TEXT.
Do THREE things:

━━━ TASK 1: ANALYZE FIT ━━━
Produce deep analysis of job requirements vs candidate qualifications:
- job_analysis: role title, company name, key_skills_required (list), experience_level
- resume_analysis: candidate_name (real name from resume), strongest_skills (list), experience_years
- tone_profile: formality (formal/semi-formal/casual), personality traits (list), vocabulary (technical/mixed/simple), example_phrases from company page
- match_score: 0-100 how well candidate fits this specific role
- resume_score: 0-100 overall resume strength for this role
- missing_skills: list of skills in job not found in resume
- suggestion_text: 2-3 bullet-point improvements the candidate should make
- tips: 3 quick actionable tips

━━━ TASK 2: REASON ABOUT SCORES ━━━
Provide analysis_reasoning with:
- overall_assessment: one sentence summary of candidate-job fit
- biggest_strength: the candidate's single strongest selling point for this role
- biggest_gap: the most important skill or experience the candidate lacks
- why_this_match_score: explain why you gave this match_score
- why_this_resume_score: explain why you gave this resume_score

━━━ TASK 3: WRITE PRIMARY EMAIL ━━━
Write one outstanding cold email the candidate can send.

EMAIL STRUCTURE (follow this exact order):
1. HOOK (1 sentence) — Open with something specific about the company, their product, a recent achievement, or the role itself. NEVER start with "I am writing to", "I hope this finds you well", or "I came across your posting".
2. VALUE BRIDGE (2-3 sentences) — Connect 2-3 candidate skills directly to job needs. Use real numbers from resume (e.g., "reduced latency by 35%", "shipped to 50k users").
3. CURIOSITY GAP (1 sentence) — Tease a relevant idea, project, or insight that makes the reader want to learn more.
4. CALL TO ACTION (1 sentence) — One low-friction ask: 15-min call, coffee chat, or "happy to share more details."

EMAIL STYLE RULES:
- 80-130 words total. Shorter is better.
- Confident but not arrogant; friendly but not casual.
- No bullet lists in the email body — flowing sentences only.
- No buzzwords: "synergy", "leverage", "passionate", "excited to apply".
- Use candidate's REAL NAME from resume for sign-off.
- Mention company name and exact role title at least once.
- Each paragraph: 1-2 sentences MAX.

EMAIL ANTI-PATTERNS (never do these):
✗ "Dear Hiring Manager" — find a better greeting
✗ Repeating the job description back word-for-word
✗ Generic flattery ("your company is amazing")
✗ Listing skills without proof, numbers, or context
✗ Wall-of-text paragraphs longer than 2 sentences

Return email_format with: greeting, opening, body, cta, signoff as separate fields.

{format_instructions}

JOB DESCRIPTION:
{job}

RESUME:
{resume}

COMPANY PAGE TEXT:
{company_text}
"""

prompt = PromptTemplate(
    template=COMBINED_TEMPLATE,
    input_variables=["job", "resume", "company_text"],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
    }
)

chain = prompt | llm | parser


def analyze_job_and_resume(job, resume, company_text=""):
    try:
        result = chain.invoke({
            "job": job,
            "resume": resume,
            "company_text": company_text if company_text else "Not available"
        })

        # Build polished email from email_format if available
        email_format = result.get("email_format", {})
        if email_format:
            lines = [
                email_format.get("greeting", "").strip(),
                "",
                email_format.get("opening", "").strip(),
                email_format.get("body", "").strip(),
                "",
                email_format.get("cta", "").strip(),
                "",
                email_format.get("signoff", "").strip(),
            ]
            formatted = "\n".join(
                l for l in lines if l is not None
            ).strip()
            if formatted:
                result["email"] = formatted

        return result

    except Exception as e:
        print(f"[Analyzer] Error: {e}")
        # Safe fallback — never crash pipeline
        return {
            "email": "",
            "email_format": {},
            "job_analysis": {
                "role": "Unknown", "company": "Unknown",
                "key_skills_required": [], "experience_level": "mid"
            },
            "resume_analysis": {
                "candidate_name": "Candidate",
                "strongest_skills": [], "experience_years": "0"
            },
            "tone_profile": {
                "formality": "semi-formal",
                "personality": [], "vocabulary": "mixed"
            },
            "match_score": 0,
            "resume_score": 0,
            "missing_skills": [],
            "suggestion_text": "",
            "tips": []
        }