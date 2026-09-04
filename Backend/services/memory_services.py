import json
import uuid
from datetime import datetime
from db.chroma_client import collection


def save_to_memory(
    job_description,
    resume_text,
    variants,
    analysis,
    score_dashboard
):
    """
    Save a completed generation to ChromaDB.
    Called after every successful pipeline run.
    """
    try:
        job_analysis = (analysis.get('job_analysis') or {}) if isinstance(analysis, dict) else {}
        resume_analysis = (analysis.get('resume_analysis') or {}) if isinstance(analysis, dict) else {}

        # Build a searchable document from job + resume
        document = f"""
        Role: {job_analysis.get('role', '')}
        Company: {job_analysis.get('company', '')}
        Skills Required: {', '.join(job_analysis.get('key_skills_required', []))}
        Experience Level: {job_analysis.get('experience_level', '')}
        Candidate Skills: {', '.join(resume_analysis.get('strongest_skills', []))}
        Match Score: {analysis.get('match_score', 0) if isinstance(analysis, dict) else 0}
        """

        best_email = ""
        best_style = ""
        if variants and isinstance(variants, list) and len(variants) > 0:
            first_variant = variants[0]
            if isinstance(first_variant, dict):
                best_email = first_variant.get('email', '')
                best_style = first_variant.get('style', '')

        suggestions = []
        if isinstance(analysis, dict):
            suggestions = analysis.get('tips') or analysis.get('suggestions') or []

        # Store full generation data as metadata
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "role": str(job_analysis.get('role', 'Unknown')),
            "company": str(job_analysis.get('company', 'Unknown')),
            "experience_level": str(job_analysis.get('experience_level', 'Unknown')),
            "match_score": str(analysis.get('match_score', 0) if isinstance(analysis, dict) else 0),
            "overall_score": str(score_dashboard.get('overall_score', 0) if isinstance(score_dashboard, dict) else 0),
            # Store best variant (first one) as reference email
            "best_email": best_email,
            "best_style": best_style,
            # Store suggestions as JSON string
            "suggestions": json.dumps(suggestions)
        }

        # Generate unique ID for this record
        record_id = str(uuid.uuid4())

        collection.add(
            documents=[document],
            metadatas=[metadata],
            ids=[record_id]
        )

        return record_id

    except Exception as e:
        # Memory save should never crash the pipeline
        print(f"[Memory] Save failed silently: {e}")
        return None


def retrieve_similar_jobs(job_description, resume_text, n_results=2):
    """
    Find past generations similar to current job + resume.
    Returns examples to use as few-shot context.
    """
    try:
        # Check if collection has any records first
        if collection.count() == 0:
            return []

        # Build query from current job
        query = f"{job_description[:500]} {resume_text[:300]}"

        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, collection.count())
        )

        if not results or not results.get('metadatas') or not results['metadatas'][0]:
            return []

        similar = []
        for metadata in results['metadatas'][0]:
            raw_suggestions = metadata.get('suggestions')
            try:
                parsed_suggestions = json.loads(raw_suggestions) if raw_suggestions else []
            except Exception:
                parsed_suggestions = []

            similar.append({
                "role": metadata.get('role', 'Unknown'),
                "company": metadata.get('company', 'Unknown'),
                "match_score": metadata.get('match_score', '0'),
                "overall_score": metadata.get('overall_score', '0'),
                "best_email": metadata.get('best_email', ''),
                "best_style": metadata.get('best_style', ''),
                "suggestions": parsed_suggestions
            })

        return similar

    except Exception as e:
        print(f"[Memory] Retrieval failed silently: {e}")
        return []


def build_few_shot_context(similar_jobs):
    """
    Convert similar past jobs into few-shot prompt context.
    This is what gets passed to the variants generator.
    """
    if not similar_jobs:
        return ""

    context = "REFERENCE EMAILS FROM SIMILAR PAST APPLICATIONS (Use these successful patterns as style and structure inspiration, but adapt all facts/skills to the current candidate and job):\n\n"

    valid_count = 0
    for i, job in enumerate(similar_jobs, 1):
        if not job.get('best_email'):
            continue
        valid_count += 1
        context += f"""Example {valid_count}:
Role: {job.get('role', 'Unknown')} at {job.get('company', 'Unknown')}
Match Score: {job.get('match_score', '0')}/100
Overall Score: {job.get('overall_score', '0')}/100
Best Style: {job.get('best_style', 'achievement')}
Email That Worked:
{job.get('best_email', '')}
---
"""
    return context.strip() if valid_count > 0 else ""


def get_memory_stats():
    """
    Return stats about what's stored in memory.
    Useful for debugging and showing in API response.
    """
    try:
        count = collection.count()
        return {
            "total_stored": count,
            "status": "active" if count > 0 else "empty"
        }
    except Exception as e:
        return {
            "total_stored": 0,
            "status": f"error: {e}"
        }