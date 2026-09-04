import asyncio
import httpx
from services.job_scraper import (
    scrape_jobs_async,
    scrape_company_page_async,
    REQUEST_HEADERS
)
from services.resume_parser import get_relevant_resume_text
from services.scorer import build_score_dashboard
from services.memory_services import (
    retrieve_similar_jobs,
    build_few_shot_context,
    save_to_memory,
)
from llms.combined_analyzer import (
    analyze_job_and_resume_async,
    analyze_job_and_resume
)
from llms.variants_generator import (
    generate_variants_async,
    generate_variants
)


def truncate(text, max_chars=3000):
    """Prevent token overflow by trimming long texts"""
    return text[:max_chars] if len(text) > max_chars else text


async def run_pipeline(job_url, resume_file):

    # Step 1: Concurrently scrape job description and company tone page
    async with httpx.AsyncClient(headers=REQUEST_HEADERS, timeout=12.0, follow_redirects=True) as http_client:
        job_task = scrape_jobs_async(job_url, client=http_client)
        company_task = scrape_company_page_async(job_url, client=http_client)
        raw_job_description, company_text = await asyncio.gather(job_task, company_task)

    job_description = truncate(raw_job_description)

    # Step 2: Parse resume - LangChain TextSplitter
    resume_text = get_relevant_resume_text(resume_file=resume_file, job_text=job_description)

    # Step 3: Retrieve similar past applications from ChromaDB memory for few-shot guidance
    similar_jobs = retrieve_similar_jobs(job_description=job_description, resume_text=resume_text, n_results=2)
    few_shot_context = build_few_shot_context(similar_jobs)

    # Step 4: API 1 call - analysis + polished email
    analysis = await analyze_job_and_resume_async(
        job=job_description,
        resume=resume_text,
        company_text=company_text
    )

    # Step 5: API Call 2 - 2 strategy variants with reasoning + few-shot context
    variants = await generate_variants_async(
        job=job_description,
        resume=resume_text,
        tone_profile=analysis.get("tone_profile"),
        few_shot_context=few_shot_context
    )

    # Step 6: Pure Python score computation
    score_dashboard = build_score_dashboard(
        resume_text=resume_text,
        job_text=job_description,
        tone_profile=analysis.get("tone_profile"),
        variants=variants,
        match_score=analysis.get("match_score", 0),
        resume_score=analysis.get("resume_score", 0)
    )

    # Step 7: Persist current generation to ChromaDB memory
    memory_id = save_to_memory(
        job_description=job_description,
        resume_text=resume_text,
        variants=variants,
        analysis=analysis,
        score_dashboard=score_dashboard
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
        "missing_skills": analysis.get("missing_skills", []),

        # Memory metadata
        "memory_id": memory_id,
        "similar_past_applications": len(similar_jobs)
    }


def run_pipeline_sync(job_url, resume_file):
    """Synchronous wrapper for offline testing or scripts"""
    return asyncio.run(run_pipeline(job_url, resume_file))
