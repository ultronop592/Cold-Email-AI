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
        # Build a searchable document from job + resume
        document = f"""
        Role: {analysis['job_analysis'].get('role', '')}
        Company: {analysis['job_analysis'].get('company', '')}
        Skills Required: {', '.join(analysis['job_analysis'].get('key_skills_required', []))}
        Experience Level: {analysis['job_analysis'].get('experience_level', '')}
        Candidate Skills: {', '.join(analysis['resume_analysis'].get('strongest_skills', []))}
        Match Score: {analysis.get('match_score', 0)}
        """

        # Store full generation data as metadata
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "role": analysis['job_analysis'].get('role', 'Unknown'),
            "company": analysis['job_analysis'].get('company', 'Unknown'),
            "experience_level": analysis['job_analysis'].get('experience_level', 'Unknown'),
            "match_score": str(analysis.get('match_score', 0)),
            "overall_score": str(score_dashboard.get('overall_score', 0)),
            # Store best variant (first one) as reference email
            "best_email": variants[0]['email'] if variants else "",
            "best_style": variants[0]['style'] if variants else "",
            # Store suggestions as JSON string
            "suggestions": json.dumps(analysis.get('suggestions', []))
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

        if not results or not results['metadatas']:
            return []

        similar = []
        for metadata in results['metadatas'][0]:
            similar.append({
                "role": metadata.get('role'),
                "company": metadata.get('company'),
                "match_score": metadata.get('match_score'),
                "overall_score": metadata.get('overall_score'),
                "best_email": metadata.get('best_email'),
                "best_style": metadata.get('best_style'),
                "suggestions": json.loads(metadata.get('suggestions', '[]'))
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

    context = "REFERENCE EMAILS FROM SIMILAR PAST APPLICATIONS:\n\n"

    for i, job in enumerate(similar_jobs, 1):
        context += f"""
Example {i}:
Role: {job['role']} at {job['company']}
Match Score: {job['match_score']}/100
Overall Score: {job['overall_score']}/100
Best Style: {job['best_style']}
Email That Worked:
{job['best_email']}
---
"""
    return context


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