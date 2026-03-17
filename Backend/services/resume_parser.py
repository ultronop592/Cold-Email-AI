import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def parse_resume(resume_file):
    
    text = ""
    
    with pdfplumber.open(resume_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
            
    return text.strip()

def get_relevant_resume_text(resume_file, job_text):
    """ 
     Split resume into chunks using LangChain TextSplitter.
    Retrieve only sections most relevant to this specific job.
    This is real RAG applied to resume parsing.
    """

    raw_text = parse_resume(resume_file)

    if not raw_text:
        return ""

    # wrap in langchain document
    doc = Document(
        page_content=raw_text,
        metadata={
            "source": "resume"
        }
    )

    # split intelligently at natural boundaries
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "],
        chunk_size=400,
        chunk_overlap=40,
    )

    chunks = splitter.split_documents([doc])

    if not chunks:
        return raw_text[:2000]

    # Score each chunk by keywords overlap with job
    job_words = set(job_text.lower().split())
    scored = []

    for chunk in chunks:
        chunk_words = set(chunk.page_content.lower().split())
        overlap = len(job_words.intersection(chunk_words))
        scored.append((
            chunk,
            overlap
        ))

    # sort by overlap score
    scored.sort(key=lambda x: x[1], reverse=True)

    # top 3 chunks
    top = [chunk.page_content for chunk, _ in scored[:3]]
    result = "\n\n".join(top)

    return result[:2000]