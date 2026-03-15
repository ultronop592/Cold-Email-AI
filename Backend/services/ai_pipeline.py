from services.job_scraper import scrape_jobs
from services.resume_parser import parse_resume
from services.scorer import build_score_dashboard
from llms.combined_analyzer import analyze_job_and_resume


def truncate(text, max_chars=3000):
    """Prevent token overflow by trimming long texts"""
    return text[:max_chars] if len(text) > max_chars else text


def run_pipeline(job_url, resume_file):

    # Step 1: Scrape job description
    job_description = truncate(scrape_jobs(job_url))

    # Step 2: Parse resume
    resume_text = truncate(parse_resume(resume_file), max_chars=2000)

    # Single API call for analysis + best email
    analysis = analyze_job_and_resume(
        job=job_description,
        resume=resume_text,
        company_text=""
    )

    # Pure Python score computation
    score_dashboard = build_score_dashboard(
        resume_text=resume_text,
        job_text=job_description,
        tone_profile=analysis.get("tone_profile"),
        variants=[{"email": analysis.get("email", "")}],
        match_score=analysis["match_score"],
        resume_score=analysis["resume_score"]
    )

    return {
        "email": analysis.get("email", ""),
        "suggestion_text": analysis.get("suggestion_text", ""),
        "tips": analysis.get("tips", []),
        "score_dashboard": score_dashboard,
        "missing_skills": analysis.get("missing_skills", [])
    }
