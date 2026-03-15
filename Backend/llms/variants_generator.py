import json
from langchain_core.prompts import PromptTemplate
from llms.groq_client import llm

VARIANTS_TEMPLATE = """
You are an expert cold email strategist for job applications.

Generate exactly 3 different cold email variants for this candidate.
Each variant uses a completely different opening strategy.

IMPORTANT — TONE MATCHING:
The company has this communication style: {tone_profile}
Mirror this tone in all 3 emails.

{few_shot_context}

VARIANT STRATEGIES:
- achievement: Open with candidate's single biggest achievement relevant to this role
- problem_solver: Open by identifying a problem this company likely faces, position candidate as solution
- curiosity: Open with a sharp insight about the company showing deep research

Rules for each email:
- Under 120 words
- No subject line
- Sound human not robotic
- Mention company name and role specifically
- End with confident call to action
- Each variant must feel completely different from the others

Return ONLY a valid JSON object. No markdown. No extra text.

{{
    "variants": [
        {{
            "style": "achievement",
            "email": "<full email body>",
            "reasoning": {{
                "strategy_choice": "<why achievement strategy fits THIS specific job>",
                "resume_points_used": "<which specific resume points were highlighted and why>",
                "tone_decision": "<how company tone was reflected in this email>",
                "predicted_impact": "<why this opening would make THIS hiring manager keep reading>"
            }}
        }},
        {{
            "style": "problem_solver",
            "email": "<full email body>",
            "reasoning": {{
                "strategy_choice": "<why problem_solver strategy fits THIS specific job>",
                "resume_points_used": "<which specific resume points were highlighted and why>",
                "tone_decision": "<how company tone was reflected in this email>",
                "predicted_impact": "<why this opening would make THIS hiring manager keep reading>"
            }}
        }},
        {{
            "style": "curiosity",
            "email": "<full email body>",
            "reasoning": {{
                "strategy_choice": "<why curiosity strategy fits THIS specific job>",
                "resume_points_used": "<which specific resume points were highlighted and why>",
                "tone_decision": "<how company tone was reflected in this email>",
                "predicted_impact": "<why this opening would make THIS hiring manager keep reading>"
            }}
        }}
    ]
}}

JOB DESCRIPTION:
{job}

CANDIDATE RESUME:
{resume}
"""

prompt = PromptTemplate(
    input_variables=["job", "resume", "tone_profile", "few_shot_context"],
    template=VARIANTS_TEMPLATE
)

chain = prompt | llm

def generate_variants(job, resume, tone_profile=None, few_shot_context=""):
    if not tone_profile:
        tone_profile = {
            "formality": "semi-formal",
            "personality": ["professional", "friendly"],
            "vocabulary": "mixed",
            "example_phrases": []
        }

    response = chain.invoke({
        "job": job,
        "resume": resume,
        "tone_profile": json.dumps(tone_profile),
        "few_shot_context": few_shot_context
    })

    raw = response.content.strip()

    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)
    return result["variants"]