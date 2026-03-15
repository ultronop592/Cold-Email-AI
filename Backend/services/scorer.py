import re


def extract_keywords(text):
    """
    Extract meaningful keywords from text.
    Filters out common stop words.
    """
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "is", "are", "was", "were",
        "be", "been", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "shall", "can",
        "this", "that", "these", "those", "we", "you", "they", "it",
        "as", "if", "then", "than", "so", "yet", "both", "either",
        "not", "no", "nor", "just", "about", "above", "after", "also",
        "our", "your", "their", "its", "my", "his", "her", "who", "which"
    }

    # Lowercase and extract words
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.-]{2,}\b', text.lower())

    # Filter stop words and short words
    keywords = [w for w in words if w not in stop_words and len(w) > 2]

    return set(keywords)


def calculate_ats_score(resume_text, job_text):
    """
    Calculate how many job keywords appear in resume.
    Returns 0-100 score and matched/missing keyword lists.
    """
    job_keywords = extract_keywords(job_text)
    resume_keywords = extract_keywords(resume_text)

    if not job_keywords:
        return {
            "score": 0,
            "matched_keywords": [],
            "missing_keywords": [],
            "total_job_keywords": 0
        }

    matched = job_keywords & resume_keywords
    missing = job_keywords - resume_keywords

    # Only show top 10 most relevant missing keywords
    # (sort by length as proxy for specificity)
    top_missing = sorted(list(missing), key=len, reverse=True)[:10]
    top_matched = sorted(list(matched), key=len, reverse=True)[:10]

    score = round((len(matched) / len(job_keywords)) * 100)

    return {
        "score": score,
        "matched_keywords": top_matched,
        "missing_keywords": top_missing,
        "total_job_keywords": len(job_keywords)
    }


def calculate_tone_score(tone_profile, variants):
    """
    Check if generated emails reflect the company tone profile.
    Returns 0-100 score.
    """
    if not tone_profile or not variants:
        return 50  # Neutral score if no tone data

    example_phrases = tone_profile.get("example_phrases", [])
    formality = tone_profile.get("formality", "semi-formal")
    vocabulary = tone_profile.get("vocabulary", "mixed")

    # Combine all variant emails into one text for checking
    all_emails = " ".join([v.get("email", "") for v in variants]).lower()

    score = 50  # Base score

    # Check if example phrases from company appear in emails
    if example_phrases:
        phrase_words = extract_keywords(" ".join(example_phrases))
        email_words = extract_keywords(all_emails)
        overlap = phrase_words & email_words
        if phrase_words:
            phrase_score = (len(overlap) / len(phrase_words)) * 30
            score += phrase_score

    # Check formality alignment
    formal_words = {"sincerely", "regarding", "furthermore", "herein", "enclosed"}
    casual_words = {"hey", "excited", "love", "awesome", "cool", "keen"}

    if formality == "casual":
        casual_found = any(w in all_emails for w in casual_words)
        score += 10 if casual_found else 0
    elif formality == "formal":
        formal_found = any(w in all_emails for w in formal_words)
        score += 10 if formal_found else 0
    else:
        score += 10  # Semi-formal always gets neutral bonus

    # Check vocabulary alignment
    tech_words = {"api", "framework", "pipeline", "backend", "frontend",
                  "infrastructure", "deployment", "architecture", "scalable"}
    if vocabulary == "technical":
        tech_found = sum(1 for w in tech_words if w in all_emails)
        score += min(tech_found * 2, 10)
    else:
        score += 5  # Neutral bonus for mixed/simple

    return min(round(score), 100)


def calculate_overall_score(match_score, resume_score, ats_score, tone_score):
    """
    Weighted average of all scores.
    Weights reflect what matters most for job applications.
    """
    weights = {
        "match_score": 0.35,    # Resume-job fit is most important
        "ats_score": 0.30,      # Keyword presence matters for ATS systems
        "resume_score": 0.20,   # Overall resume strength
        "tone_score": 0.15      # Tone matching is a bonus differentiator
    }

    overall = (
        match_score  * weights["match_score"] +
        ats_score    * weights["ats_score"] +
        resume_score * weights["resume_score"] +
        tone_score   * weights["tone_score"]
    )

    return round(overall)


def get_score_label(score):
    """Convert score to human readable label"""
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 55:
        return "Fair"
    else:
        return "Needs Work"


def build_score_dashboard(
    resume_text,
    job_text,
    tone_profile,
    variants,
    match_score,
    resume_score
):
    """
    Master function — builds complete scoring dashboard.
    Called from ai_pipeline.py
    """
    ats_result = calculate_ats_score(resume_text, job_text)
    tone_score = calculate_tone_score(tone_profile, variants)
    overall = calculate_overall_score(
        match_score,
        resume_score,
        ats_result["score"],
        tone_score
    )

    return {
        "overall_score": overall,
        "overall_label": get_score_label(overall),
        "breakdown": {
            "match_score": {
                "score": match_score,
                "label": get_score_label(match_score),
                "description": "How well your resume matches this specific job"
            },
            "ats_score": {
                "score": ats_result["score"],
                "label": get_score_label(ats_result["score"]),
                "description": "Keywords from job description found in your resume",
                "matched_keywords": ats_result["matched_keywords"],
                "missing_keywords": ats_result["missing_keywords"]
            },
            "resume_score": {
                "score": resume_score,
                "label": get_score_label(resume_score),
                "description": "Overall strength of your resume for this role"
            },
            "tone_score": {
                "score": tone_score,
                "label": get_score_label(tone_score),
                "description": "How well email tone matches company communication style"
            }
        }
    }