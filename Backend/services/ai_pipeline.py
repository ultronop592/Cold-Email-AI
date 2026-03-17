from services.job_scraper import scrape_jobs, scrape_company_page
from services.resume_parser import get_relevant_resume_text
from services.scorer import build_score_dashboard
from llms.combined_analyzer import analyze_job_and_resume
from llms.variants_generator import generate_variants


def truncate(text, max_chars=3000):
    """Prevent token overflow by trimming long texts"""
    return text[:max_chars] if len(text) > max_chars else text


def run_pipeline(job_url, resume_file):

    # Step 1: Scrape job description
    job_description = truncate(scrape_jobs(job_url))
    comapny_text = scrape_company_page(job_url)

    # Step 2: Parse resume -Langchain text Spitter
    resume_text = get_relevant_resume_text(resume_file=resume_file, job_text=job_description)
    

    # API 1 call - analysis + polished email
    analysis = analyze_job_and_resume(
        job=job_description,
        resume=resume_text,
        company_text=comapny_text
    )

    # APi Call 2 -2 strategy variants with reasoning
    variants = generate_variants(
        job=job_description,
        resume=resume_text,
        tone_profile=analysis.get("tone_profile")
    )

    # Pure Python score computation
    score_dashboard = build_score_dashboard(
        resume_text=resume_text,
        job_text=job_description,
        tone_profile=analysis.get("tone_profile"),
        variants=variants,
        match_score=analysis.get("match_score", 0),
        resume_score=analysis.get("resume_score", 0)
    )

    return {
        # Primary polished email
        "email": analysis.get("email", ""),
        "email_format": analysis.get("email_format", {}),

        # 2 strategy variants
        "variants": variants,

        # Analysis
        "job_analysis": analysis.get("job_analysis", {}),
        "resume_analysis": analysis.get("resume_analysis", {}),
        "tone_profile": analysis.get("tone_profile", {}),

        # Scores
        "score_dashboard": score_dashboard,
        "match_score": analysis.get("match_score", 0),
        "resume_score": analysis.get("resume_score", 0),

        # Improvements
        "suggestion_text": analysis.get("suggestion_text", ""),
        "tips": analysis.get("tips", []),
        "missing_skills": analysis.get("missing_skills", [])
    }
