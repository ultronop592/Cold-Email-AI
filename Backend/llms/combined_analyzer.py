import json
from langchain_core.prompts import PromptTemplate
from llms.groq_client import llm

COMBINED_TEMPLATE = """
You are an elite outreach strategist and cold-email copywriter. Your emails
have an average 45 % open rate and 12 % reply rate because you follow these
principles religiously.

═══════════════════════════════════════════════
 YOUR TASK
═══════════════════════════════════════════════
Given the JOB DESCRIPTION and CANDIDATE RESUME below, do TWO things:
1. Analyze the fit between the candidate and the role.
2. Write a single, outstanding cold email the candidate can send to the
   hiring manager. The email must feel like a real person wrote it, not AI.

═══════════════════════════════════════════════
 COLD EMAIL WRITING RULES (follow every single one)
═══════════════════════════════════════════════

STRUCTURE (4 parts, strict order):
  1. HOOK (1 sentence)  — Open with something specific about the company,
     their product, a recent news item, or a genuine observation.  NEVER
     open with "I am writing to…", "I came across…", "I hope this email
     finds you well", or any generic filler.
  2. VALUE BRIDGE (2-3 sentences) — Connect exactly 2-3 of the candidate's
     strongest skills, projects, or measurable achievements DIRECTLY to
     what the job description asks for.  Use concrete numbers or outcomes
     when available (e.g., "reduced build time by 40 %", "shipped a feature
     used by 10 k+ users").
  3. CURIOSITY GAP (1 sentence) — Tease a specific idea, insight, or
     relevant project that would make the reader want to learn more.
  4. CALL TO ACTION (1 sentence) — End with a single, low-friction ask:
     a 15-min call, a quick coffee chat, or "happy to share more details".

STYLE RULES:
  • Total email length: 80-130 words.  Shorter is better.
  • Tone: confident but not arrogant, friendly but not casual, concise
    but not robotic.
  • Use the hiring manager's first name if it can be inferred; otherwise
    use the company name or "Hi there".
  • Use the candidate's REAL name from the resume for the sign-off.
  • NO subject line — only the body.
  • NO bullet lists in the email — flowing sentences only.
  • NO buzzwords like "synergy", "leverage", "passionate".  Use plain,
    vivid English.
  • DO mention the company name and exact role title at least once.
  • Each paragraph should be 1-2 sentences MAX. White-space is your friend.

ANTI-PATTERNS TO AVOID:
  ✗ Starting with "Dear Hiring Manager"
  ✗ Repeating the entire job description back
  ✗ Generic flattery like "your company is amazing"
  ✗ Listing skills without context or proof
  ✗ Long paragraphs or wall-of-text
  ✗ Overly formal or stiff language

═══════════════════════════════════════════════
 OUTPUT FORMAT
═══════════════════════════════════════════════
Return ONLY a valid JSON object.  No markdown fences. No commentary.

{{
    "email": "<the full cold email body exactly as the candidate should send it — with paragraph breaks as newlines>",
    "email_format": {{
        "greeting": "<greeting line, e.g. Hi Sarah,>",
        "opening": "<the hook sentence tied to company/role>",
        "body": "<the value bridge: 2-3 sentences connecting resume highlights to job needs, with numbers>",
        "cta": "<one clear, low-friction call-to-action>",
        "signoff": "<sign-off with candidate's real name>"
    }},
    "job_analysis": {{
        "role": "<exact job title from the posting>",
        "company": "<company name if found, else Unknown>",
        "key_skills_required": ["skill1", "skill2", "skill3"],
        "experience_level": "<junior or mid or senior>"
    }},
    "resume_analysis": {{
        "candidate_name": "<full name from resume, else Candidate>",
        "strongest_skills": ["skill1", "skill2", "skill3"],
        "experience_years": "<estimated total years as a number>"
    }},
    "tone_profile": {{
        "formality": "<casual or semi-formal or formal>",
        "personality": ["<trait1>", "<trait2>"],
        "vocabulary": "<simple or technical or mixed>"
    }},
    "match_score": <0-100 integer — how well the resume matches the job requirements>,
    "resume_score": <0-100 integer — overall strength of the resume for this specific role>,
    "missing_skills": ["<important skill in job desc but absent from resume>"],
    "suggestion_text": "<plain text only. Start with 'Improvements:' then 3-5 bullet points on how the candidate can strengthen their application. End with 'Quick Tips:' and 3 actionable tips.>",
    "tips": ["<tip1>", "<tip2>", "<tip3>"]
}}

═══════════════════════════════════════════════
 INPUTS
═══════════════════════════════════════════════

JOB DESCRIPTION:
{job}

RESUME:
{resume}

COMPANY PAGE TEXT (may be empty if unavailable):
{company_text}
"""

prompt = PromptTemplate(
    input_variables=["job", "resume", "company_text"],
    template=COMBINED_TEMPLATE
)

chain = prompt | llm


def _escape_control_chars_in_strings(text):
    """Escape literal newlines/tabs inside JSON string values."""
    result = []
    in_string = False
    escape = False

    for ch in text:
        if in_string:
            if escape:
                result.append(ch)
                escape = False
                continue

            if ch == "\\":
                result.append(ch)
                escape = True
                continue

            if ch == '"':
                result.append(ch)
                in_string = False
                continue

            if ch == "\n":
                result.append("\\n")
                continue

            if ch == "\r":
                result.append("\\r")
                continue

            if ch == "\t":
                result.append("\\t")
                continue

            result.append(ch)
            continue

        result.append(ch)
        if ch == '"':
            in_string = True

    return "".join(result)


def analyze_job_and_resume(job, resume, company_text=""):
    response = chain.invoke({
        "job": job,
        "resume": resume,
        "company_text": company_text if company_text else "Not available"
    })

    raw = response.content.strip()

    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    raw = _escape_control_chars_in_strings(raw)

    parsed = json.loads(raw)

    # Compose a polished email when segmented format is provided.
    email_format = parsed.get("email_format") or {}
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
        formatted_email = "\n".join(
            [line for line in lines if line is not None]
        ).strip()
        if formatted_email:
            parsed["email"] = formatted_email

    return parsed
