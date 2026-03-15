def build_reasoning_summary(analysis, variants, score_dashboard):
    """
    Builds a complete human-readable reasoning report
    explaining every AI decision made in this pipeline run.
    Zero API calls — pure assembly from existing data.
    """

    reasoning = analysis.get("analysis_reasoning", {})
    job = analysis.get("job_analysis", {})
    resume = analysis.get("resume_analysis", {})
    tone = analysis.get("tone_profile", {})
    breakdown = score_dashboard.get("breakdown", {})

    return {

        # Overall picture
        "overall_assessment": reasoning.get("overall_assessment", ""),
        "biggest_strength": reasoning.get("biggest_strength", ""),
        "biggest_gap": reasoning.get("biggest_gap", ""),

        # Why scores are what they are
        "score_explanations": {
            "match_score": {
                "score": breakdown.get("match_score", {}).get("score"),
                "why": reasoning.get("why_this_match_score", "")
            },
            "resume_score": {
                "score": breakdown.get("resume_score", {}).get("score"),
                "why": reasoning.get("why_this_resume_score", "")
            },
            "ats_score": {
                "score": breakdown.get("ats_score", {}).get("score"),
                "why": f"Your resume contains {len(breakdown.get('ats_score', {}).get('matched_keywords', []))} of the key job keywords. "
                       f"Missing: {', '.join(breakdown.get('ats_score', {}).get('missing_keywords', [])[:5])}"
            },
            "tone_score": {
                "score": breakdown.get("tone_score", {}).get("score"),
                "why": f"Company tone is {tone.get('formality', 'unknown')} and {tone.get('vocabulary', 'unknown')} vocabulary. "
                       f"Emails were written to reflect: {', '.join(tone.get('personality', []))}"
            }
        },

        # Why each email variant was written the way it was
        "email_reasoning": [
            {
                "style": v.get("style"),
                "reasoning": v.get("reasoning", {})
            }
            for v in variants
        ],

        # Why each suggestion was made
        "suggestion_reasoning": [
            {
                "type": s.get("type"),
                "section": s.get("section"),
                "action": s.get("action"),
                "why": s.get("reasoning", "")
            }
            for s in analysis.get("suggestions", [])
        ],

        # Context summary
        "context_used": {
            "role_targeted": job.get("role", ""),
            "company_targeted": job.get("company", ""),
            "candidate_name": resume.get("candidate_name", ""),
            "experience_level_detected": job.get("experience_level", ""),
            "tone_detected": tone.get("formality", "not detected")
        }
    }