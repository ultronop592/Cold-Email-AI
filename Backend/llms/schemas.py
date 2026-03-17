from pydantic import BaseModel, Field
from typing import List, Optional


class JobAnalysis(BaseModel):
    role: str = ""
    company: str = ""
    key_skills_required: List[str] = []
    experience_level: str = "mid"


class ResumeAnalysis(BaseModel):
    candidate_name: str = "Candidate"
    strongest_skills: List[str] = []
    experience_years: str = "0"


class ToneProfile(BaseModel):
    formality: str = "semi-formal"
    personality: List[str] = []
    vocabulary: str = "mixed"
    example_phrases: List[str] = []


class EmailFormat(BaseModel):
    greeting: str = ""
    opening: str = ""
    body: str = ""
    cta: str = ""
    signoff: str = ""


class CombinedAnalysis(BaseModel):
    email: str = ""
    email_format: EmailFormat = EmailFormat()
    job_analysis: JobAnalysis = JobAnalysis()
    resume_analysis: ResumeAnalysis = ResumeAnalysis()
    tone_profile: ToneProfile = ToneProfile()
    match_score: int = 0
    resume_score: int = 0
    missing_skills: List[str] = []
    suggestion_text: str = ""
    tips: List[str] = []


class VariantReasoning(BaseModel):
    strategy: str = ""
    why_this_opening: str = ""
    key_strength_used: str = ""


class Variant(BaseModel):
    style: str = ""
    email: str = ""
    reasoning: VariantReasoning = VariantReasoning()


class VariantsOutput(BaseModel):
    variants: List[Variant] = []
