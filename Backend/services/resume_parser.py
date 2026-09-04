import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.logger import get_logger
from services.exceptions import ResumeParsingError

logger = get_logger("resume_parser")


def parse_resume(resume_file) -> str:
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


def get_relevant_resume_text(resume_file, job_text: str) -> str:
    """
    Split resume into chunks and retrieve sections most relevant to the job,
    while always preserving the header chunk containing candidate contact info.
    """
    raw_text = parse_resume(resume_file)

    doc = Document(
        page_content=raw_text,
        metadata={"source": "resume"}
    )

    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "],
        chunk_size=400,
        chunk_overlap=40,
    )

    chunks = splitter.split_documents([doc])

    if not chunks:
        return raw_text[:2000]

    # If 3 or fewer chunks, return all of them
    if len(chunks) <= 3:
        return "\n\n".join(c.page_content for c in chunks)[:2000]

    # Always keep first chunk (header with name and contact info)
    header_chunk = chunks[0]
    remaining_chunks = chunks[1:]

    job_words = set(job_text.lower().split())
    scored = []
    for chunk in remaining_chunks:
        chunk_words = set(chunk.page_content.lower().split())
        overlap = len(job_words.intersection(chunk_words))
        scored.append((chunk, overlap))

    scored.sort(key=lambda x: x[1], reverse=True)

    selected = [header_chunk.page_content] + [chunk.page_content for chunk, _ in scored[:2]]
    result = "\n\n".join(selected)
    return result[:2000]