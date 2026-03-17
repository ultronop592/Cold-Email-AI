import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from llms.groq_client import llm_large
from llms.schemas import VariantsOutput

parser = JsonOutputParser(pydantic_object=VariantsOutput)

VARIANTS_TEMPLATE = """
You are an elite cold email copywriter. You write emails that hiring managers actually read and reply to.

Your task: Write exactly 2 cold email variants for a candidate applying to a specific role.

IMPORTANT — STYLE FIELD:
- Variant 1 "style" field MUST be exactly: "achievement"
- Variant 2 "style" field MUST be exactly: "problem_solver"
- Do NOT put tone or formality in the style field.

COMPANY TONE TO MATCH: {tone_profile}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VARIANT 1 — style: "achievement"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STRATEGY: Lead with the candidate's most impressive, measurable achievement that's directly relevant to the role.

EXACT EMAIL FORMAT TO FOLLOW:
---
Subject: [Role Title] Application — [Candidate's Strongest Relevant Achievement in 5-8 words]

Dear [Hiring Manager / Sir/Madam],

[Hook: Specific observation about the company's product, tech stack, or recent news that shows you did research — 1 sentence.]

[Value Bridge: Connect your biggest achievement with numbers to what the role needs. "At [Previous Company], I [specific achievement with metrics] — which maps directly to what your [Role Title] position requires." — 2-3 sentences.]

[Curiosity Gap: Tease something specific you've built or an insight you have that would help them — 1 sentence.]

[Call to Action: One clear, low-friction ask — 1 sentence. E.g., "Would love to share more over a quick 15-minute call this week."]

Regards,
[Candidate Full Name]
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VARIANT 2 — style: "problem_solver"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STRATEGY: Identify a real challenge the company likely faces based on the role description, and position the candidate as someone who already solved it.

EXACT EMAIL FORMAT TO FOLLOW:
---
Subject: Solving [Company's Key Challenge] — [Candidate Name] for [Role Title]

Dear [Hiring Manager / Sir/Madam],

[Hook: Name a specific, realistic challenge this company faces based on the job description — 1 sentence.]

[Value Bridge: Show you've already solved this problem. "When [Previous Company] faced a similar challenge, I [specific solution with measurable outcome]." — 2-3 sentences.]

[Curiosity Gap: Mention a specific approach or framework you'd bring — 1 sentence.]

[Call to Action: E.g., "I'd be happy to walk you through my approach over a 15-minute call. Would [this week] work?"]

Best regards,
[Candidate Full Name]
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROFESSIONAL EMAIL FORMAT RULES (CRITICAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MANDATORY FORMAT — every email MUST have ALL of these in this exact order:
1. SUBJECT LINE: Start with "Subject: ..." on the first line. Short, specific, compelling.
2. BLANK LINE after subject
3. SALUTATION: "Dear Hiring Manager," or "Dear Sir/Madam," on its own line
4. BLANK LINE after salutation
5. BODY: 3-4 short paragraphs (Hook → Value Bridge → Curiosity Gap → CTA), each separated by blank lines
6. BLANK LINE before closing
7. CLOSING: "Regards," or "Best regards," or "Warm regards," on its own line
8. FULL NAME: Candidate's FULL NAME from resume on the next line

CONTENT REQUIREMENTS:
- 120-170 words for the body (not counting subject, greeting, sign-off)
- Mention the EXACT company name at least once
- Mention the EXACT role title at least once
- Include at least ONE specific metric/number from the resume
- Each paragraph: 1-3 sentences MAX
- Sound like a confident professional, not a desperate job seeker

ABSOLUTE ANTI-PATTERNS (NEVER do these):
✗ "I am writing to express my interest in..."
✗ "I hope this email finds you well"
✗ "I came across your job posting"
✗ Generic flattery ("your company is amazing")
✗ Buzzwords: "synergy", "leverage", "passionate", "excited to apply"
✗ Missing subject line
✗ Missing "Dear" salutation
✗ Signing off as just "Best, FirstName" — MUST use full name with proper closing
✗ Wall of text without paragraph breaks

FOR EACH VARIANT, include "reasoning":
- strategy: MUST be "achievement" for variant 1, "problem_solver" for variant 2
- why_this_opening: 1-2 sentences explaining why you chose this specific hook
- key_strength_used: the specific skill or achievement from the resume that powers this email

{format_instructions}

JOB DESCRIPTION:
{job}

CANDIDATE RESUME:
{resume}
"""

prompt = PromptTemplate(
    template=VARIANTS_TEMPLATE,
    input_variables=["job", "resume", "tone_profile"],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
    }
)

chain = prompt | llm_large | parser


def generate_variants(job, resume, tone_profile=None):
    if not tone_profile:
        tone_profile = {
            "formality": "semi-formal",
            "personality": ["professional", "friendly"],
            "vocabulary": "mixed"
        }

    try:
        result = chain.invoke({
            "job": job,
            "resume": resume,
            "tone_profile": json.dumps(tone_profile)
        })
        return result.get("variants", [])

    except Exception as e:
        print(f"[Variants] Error: {e}")
        return []