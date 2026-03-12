from services.job_scraper import scrape_jobs
from services.resume_parser import parse_resume

from llms.job_analyzer import analyze_job
from llms.resume_analyzer import analyze_resume
from llms.email_generation import generate_email
from llms.suggestion_engine import generate_suggestions


def run_pipeline(job_url, resume_file):

    # Step 1: Scrape job description
    job_description = scrape_jobs(job_url)

    # Step 2: Parse resume
    resume_text = parse_resume(resume_file)

    # Step 3: Analyze job description
    job_info = analyze_job(job_description)

    # Step 4: Analyze resume
    resume_info = analyze_resume(resume_text)

    # Step 5: Generate email
    email_content = generate_email(job_description, resume_text)

    # Step 6: Generate suggestions
    suggestions = generate_suggestions(job_info, resume_info)

    return {
        "email": email_content,
        "suggestions": suggestions,
        "job_analysis": job_info,
        "resume_analysis": resume_info
    }
