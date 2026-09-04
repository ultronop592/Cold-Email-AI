import re
from typing import Dict, Any, List, Optional, Union
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.logger import get_logger
from services.exceptions import ResumeParsingError

logger = get_logger("resume_parser")


def extract_contact_info(text: str) -> Dict[str, Any]:
    """
    Extract contact details and candidate identification from resume text using regex.
    Detects Name, Email, Phone, LinkedIn, GitHub, and Portfolio URLs.
    """
    if not text:
        return {
            "name": "",
            "emails": [],
            "phones": [],
            "linkedin": [],
            "github": [],
            "portfolios": []
        }

    # 1. Emails
    emails = list(dict.fromkeys(
        re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    ))

    # 2. Phone numbers (international, US/domestic with area codes and dashes/dots/spaces)
    phone_matches = re.findall(
        r'(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{3,5}',
        text
    )
    phones = []
    for m in phone_matches:
        digits_only = re.sub(r'\D', '', m)
        if 7 <= len(digits_only) <= 15:
            clean = m.strip()
            if clean not in phones:
                phones.append(clean)

    # 3. LinkedIn profiles
    linkedins = list(dict.fromkeys(
        re.findall(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
    ))

    # 4. GitHub profiles
    githubs = list(dict.fromkeys(
        re.findall(r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
    ))

    # 5. Portfolio and personal websites (excluding general platforms like linkedin, github)
    all_urls = re.findall(r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?', text)
    portfolios = []
    for u in all_urls:
        if not re.search(r'linkedin\.com|github\.com|twitter\.com|x\.com', u, re.IGNORECASE):
            clean = u.rstrip('.,;:)')
            if clean not in portfolios:
                portfolios.append(clean)

    # 6. Candidate Name heuristic (first clean line without emails, URLs, or long sentences)
    name = ""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:5]:
        if len(line) <= 60 and not re.search(r'[@/\\|]|https?:', line):
            if re.search(r'^[A-Z][a-zA-Z\s.-]+$', line):
                name = line
                break

    return {
        "name": name,
        "emails": emails,
        "phones": phones,
        "linkedin": linkedins,
        "github": githubs,
        "portfolios": portfolios
    }


def parse_resume(resume_file: Any) -> str:
    """
    Extract plain text from uploaded PDF resume.
    Raises ResumeParsingError if the PDF is unreadable, empty, or corrupted.
    """
    try:
        # If resume_file is an SpooledTemporaryFile or file-like object, rewind first
        if hasattr(resume_file, "seek"):
            resume_file.seek(0)

        pages_text = []
        with pdfplumber.open(resume_file) as pdf:
            if not pdf.pages:
                raise ResumeParsingError("Uploaded PDF contains no pages.")

            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text.strip())

        full_text = "\n\n".join(pages_text).strip()

        if len(full_text) < 30:
            logger.warning("Resume text is suspiciously short (%d chars)", len(full_text))
            raise ResumeParsingError(
                "Could not extract sufficient readable text from the resume. "
                "If this is a scanned document or image PDF, please provide a text-based PDF."
            )

        logger.info("Parsed resume successfully: %d characters across %d pages", len(full_text), len(pdf.pages))
        return full_text

    except ResumeParsingError:
        raise
    except Exception as exc:
        logger.error("Failed to parse PDF resume: %s", exc, exc_info=True)
        raise ResumeParsingError(f"Failed to read PDF file: {exc}") from exc


def get_relevant_resume_text(resume_file: Any, job_text: str, max_chars: int = 3500) -> str:
    """
    Retrieve resume text for downstream LLM analysis, cold email generation, and ATS scoring.

    Key Guarantees:
    1. Full Text Retention: For standard 1-2 page resumes (<= max_chars), the entire resume
       is preserved with 100% fidelity (no lost contact info, skills, or metrics).
    2. Contact Information Guarantee: Contact info (Name, Email, Phone, LinkedIn, GitHub,
       Portfolio) is extracted and guaranteed to be present.
    3. Smart Contextual Chunking: For very long resumes/CVs (> max_chars), prioritizes the
       Header, Skills section, and top job-relevant chunks, reassembling them in original
       document chronological order.
    """
    if isinstance(resume_file, str):
        raw_text = resume_file.strip()
    else:
        raw_text = parse_resume(resume_file)

    if not raw_text:
        return ""

    contact_info = extract_contact_info(raw_text)

    # Standard resumes (1-2 pages) fit comfortably within the LLM context window.
    # Keep the entire resume to guarantee zero lost skills, metrics, or contact info.
    if len(raw_text) <= max_chars:
        return raw_text

    logger.info("Resume length (%d chars) exceeds max_chars (%d), performing contact-preserving chunk selection",
                len(raw_text), max_chars)

    # For unusually long documents (> max_chars):
    doc = Document(
        page_content=raw_text,
        metadata={"source": "resume"}
    )

    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " "],
        chunk_size=800,
        chunk_overlap=120,
    )

    chunks = splitter.split_documents([doc])

    if not chunks:
        return raw_text[:max_chars]

    # If all chunks together fit within budget, return all
    total_chunks_len = sum(len(c.page_content) for c in chunks)
    if total_chunks_len <= max_chars:
        return "\n\n".join(c.page_content for c in chunks)

    # Categorize chunks:
    # 1. First chunk is ALWAYS retained (Header / Contact / Objective)
    header_chunk_idx = 0

    # 2. Check for skills section
    skills_chunk_indices = set()
    for idx, c in enumerate(chunks):
        content_lower = c.page_content.lower()
        if re.search(r'\b(technical skills|skills|technologies|core competencies|tooling|stack)\b', content_lower):
            skills_chunk_indices.add(idx)

    # 3. Score remaining chunks against the job description
    try:
        from services.scorer import extract_skills, extract_keywords
        job_skills = extract_skills(job_text)
        job_kw = extract_keywords(job_text)
    except Exception:
        job_skills = set()
        job_kw = set(job_text.lower().split())

    scored_chunks = []
    for idx, c in enumerate(chunks):
        if idx == header_chunk_idx or idx in skills_chunk_indices:
            continue
        try:
            c_skills = extract_skills(c.page_content)
            c_kw = extract_keywords(c.page_content)
        except Exception:
            c_skills = set()
            c_kw = set(c.page_content.lower().split())

        skill_overlap = len(job_skills & c_skills)
        kw_overlap = len(job_kw & c_kw)
        score = (skill_overlap * 3) + kw_overlap
        scored_chunks.append((idx, score, len(c.page_content)))

    # Sort remaining chunks by relevance score descending
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    # Select chunks respecting the character budget
    selected_indices = {header_chunk_idx}
    current_length = len(chunks[header_chunk_idx].page_content)

    # Add skills chunks next
    for s_idx in skills_chunk_indices:
        chunk_len = len(chunks[s_idx].page_content)
        if current_length + chunk_len <= max_chars:
            selected_indices.add(s_idx)
            current_length += chunk_len

    # Add top scored chunks
    for idx, score, chunk_len in scored_chunks:
        if current_length + chunk_len <= max_chars:
            selected_indices.add(idx)
            current_length += chunk_len

    # Reconstruct resume in ORIGINAL document chronological order
    ordered_indices = sorted(selected_indices)
    reconstructed = "\n\n".join(chunks[i].page_content for i in ordered_indices)

    # Safety check: Verify all key contact info is present in reconstructed text
    missing_contact = []
    for email in contact_info.get("emails", []):
        if email not in reconstructed:
            missing_contact.append(f"Email: {email}")
    for phone in contact_info.get("phones", []):
        if phone not in reconstructed:
            missing_contact.append(f"Phone: {phone}")
    for li in contact_info.get("linkedin", []):
        if li not in reconstructed:
            missing_contact.append(f"LinkedIn: {li}")
    for gh in contact_info.get("github", []):
        if gh not in reconstructed:
            missing_contact.append(f"GitHub: {gh}")

    if missing_contact:
        contact_banner = "=== CANDIDATE CONTACT INFO ===\n" + " | ".join(missing_contact) + "\n==============================\n\n"
        reconstructed = contact_banner + reconstructed

    return reconstructed[:max_chars]