import asyncio
import json
import re
from urllib.parse import urlparse, parse_qs
from typing import Optional, Tuple, Dict, Any
import httpx
from bs4 import BeautifulSoup

from app.logger import get_logger
from services.exceptions import ScrapingError

logger = get_logger("job_scraper")

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

LINKEDIN_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0"
}

KNOWN_JOB_BOARDS = {
    "linkedin.com",
    "greenhouse.io",
    "lever.co",
    "ashbyhq.com",
    "workable.com",
    "indeed.com",
    "glassdoor.com",
    "ziprecruiter.com",
    "smartrecruiters.com",
    "workday.com",
    "myworkdayjobs.com",
    "bamboohr.com"
}


def clean_html_text(html_content: bytes | str) -> str:
    """Extract clean textual content by removing navigation, footer, scripts, and styling."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["nav", "footer", "script", "style", "header", "noscript", "svg"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def is_job_board_domain(netloc: str) -> bool:
    """Check if a domain belongs to a known job board or ATS platform."""
    netloc_lower = netloc.lower()
    return any(board in netloc_lower for board in KNOWN_JOB_BOARDS)


def detect_job_board(url: str) -> str:
    """Identify which job board or ATS hosts the given URL."""
    parsed = urlparse(url.lower())
    netloc = parsed.netloc

    if "linkedin.com" in netloc:
        return "linkedin"
    elif "greenhouse.io" in netloc:
        return "greenhouse"
    elif "lever.co" in netloc:
        return "lever"
    elif "ashbyhq.com" in netloc:
        return "ashby"
    elif "workable.com" in netloc:
        return "workable"
    elif "indeed.com" in netloc:
        return "indeed"
    return "generic"


def extract_company_base_url(job_url: str) -> str:
    """
    Extract base company website URL from job posting URL.
    Returns empty string if the URL is a job board platform (e.g. LinkedIn, Greenhouse)
    to prevent analyzing the job board's corporate about page.
    """
    if not job_url or not (job_url.startswith("http://") or job_url.startswith("https://")):
        return ""

    parsed = urlparse(job_url)
    if not parsed.scheme or not parsed.netloc:
        return ""

    # Never treat a job board as the employer's company website
    if is_job_board_domain(parsed.netloc):
        logger.info("Job URL is on a job board (%s). Skipping job board domain for company tone.", parsed.netloc)
        return ""

    return f"{parsed.scheme}://{parsed.netloc}"


def extract_linkedin_job_id(url: str) -> Optional[str]:
    """
    Extracts numeric job ID from various LinkedIn job URL formats:
    - https://www.linkedin.com/jobs/view/1234567890/
    - https://www.linkedin.com/jobs/view/software-engineer-at-stripe-1234567890
    - https://www.linkedin.com/jobs/search/?currentJobId=1234567890
    - https://www.linkedin.com/jobs/collections/recommended/?currentJobId=1234567890
    """
    match = re.search(r'/jobs/view/(?:[a-zA-Z0-9-]+-)?(\d+)', url)
    if match:
        return match.group(1)

    match_query = re.search(r'[?&]currentJobId=(\d+)', url)
    if match_query:
        return match_query.group(1)

    return None


def extract_greenhouse_info(url: str) -> Optional[Tuple[str, str]]:
    """Extract (company_slug, job_id) from Greenhouse URLs."""
    m = re.search(r'greenhouse\.io/([a-zA-Z0-9_-]+)/jobs/(\d+)', url)
    if m:
        return m.group(1), m.group(2)
    m2 = re.search(r'for=([a-zA-Z0-9_-]+).*token=(\d+)', url)
    if m2:
        return m2.group(1), m2.group(2)
    return None


def extract_lever_info(url: str) -> Optional[Tuple[str, str]]:
    """Extract (company_slug, job_id) from Lever URLs."""
    m = re.search(r'jobs\.lever\.co/([a-zA-Z0-9_-]+)/([a-f0-9-]+)', url)
    if m:
        return m.group(1), m.group(2)
    return None


def extract_json_ld_job_posting(html_content: str) -> Optional[Dict[str, Any]]:
    """Extract Schema.org JobPosting structured data from HTML."""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        for script in soup.find_all("script", type="application/ld+json"):
            if not script.string:
                continue
            try:
                data = json.loads(script.string)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict):
                        if item.get("@type") == "JobPosting":
                            return item
                        for sub in item.get("@graph", []):
                            if isinstance(sub, dict) and sub.get("@type") == "JobPosting":
                                return sub
            except Exception:
                continue
    except Exception:
        pass
    return None


async def scrape_linkedin_job(url: str, client: httpx.AsyncClient) -> str:
    """
    Scrape a LinkedIn job posting using LinkedIn's public guest job API endpoint.
    Falls back to direct URL and parses structured metadata with actionable error handling.
    """
    job_id = extract_linkedin_job_id(url)
    if not job_id:
        raise ScrapingError(
            "Could not extract a valid LinkedIn Job ID from the provided URL. "
            "Expected format: https://www.linkedin.com/jobs/view/<id> or https://www.linkedin.com/jobs/search/?currentJobId=<id>"
        )

    guest_api_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    logger.info("Fetching LinkedIn job via guest API: %s", guest_api_url)

    try:
        res = await client.get(guest_api_url, headers=LINKEDIN_HEADERS, timeout=12.0)

        # Fallback to direct page if guest API returns 429/999 or authwall
        if res.status_code in (429, 999) or "authwall" in str(res.url):
            logger.warning("LinkedIn restricted guest API (HTTP %s). Attempting direct view fallback.", res.status_code)
            direct_url = f"https://www.linkedin.com/jobs/view/{job_id}"
            res = await client.get(direct_url, headers=LINKEDIN_HEADERS, timeout=12.0)

        if res.status_code in (429, 999) or "authwall" in str(res.url):
            raise ScrapingError(
                "LinkedIn is currently restricting automated guest access to this posting (login challenge required). "
                "Tip: You can paste the job description text directly into the input to generate your cold email immediately!"
            )

        if res.status_code == 404:
            raise ScrapingError("This LinkedIn job posting was not found (HTTP 404). It may have expired or been removed.")

        res.raise_for_status()
        html = res.text
        soup = BeautifulSoup(html, "html.parser")

        # 1. Try JSON-LD JobPosting schema first
        ld_data = extract_json_ld_job_posting(html)
        if ld_data:
            title = ld_data.get("title", "")
            company = ld_data.get("hiringOrganization", {}).get("name", "")
            raw_desc = ld_data.get("description", "")
            desc_text = clean_html_text(raw_desc)
            if len(desc_text) > 80:
                header = f"Role: {title}\nCompany: {company}\n\nJob Description:\n" if title or company else ""
                return header + desc_text

        # 2. HTML parsing fallback
        title_el = soup.find(class_=re.compile(r'top-card-layout__title|topcard__title|job-title'))
        title = title_el.get_text(strip=True) if title_el else ""

        company_el = soup.find(class_=re.compile(r'topcard__org-name-link|topcard__flavor--black-link|topcard__flavor'))
        company = company_el.get_text(strip=True) if company_el else ""

        desc_el = soup.find(class_=re.compile(r'show-more-less-html__markup|description__text|decoratedJobPosting'))
        if desc_el:
            desc_text = desc_el.get_text(separator="\n", strip=True)
        else:
            desc_text = clean_html_text(html)

        if len(desc_text) < 50:
            raise ScrapingError(
                "Could not extract sufficient text from this LinkedIn job posting. "
                "Tip: You can paste the job description text directly into the input."
            )

        parts = []
        if title:
            parts.append(f"Role: {title}")
        if company:
            parts.append(f"Company: {company}")
        if parts:
            return "\n".join(parts) + "\n\nJob Description:\n" + desc_text

        return desc_text

    except ScrapingError:
        raise
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in (401, 403, 999):
            raise ScrapingError(
                "LinkedIn access was restricted (HTTP %d). "
                "Tip: You can paste the job description text directly into the input." % exc.response.status_code
            ) from exc
        raise ScrapingError(f"LinkedIn returned HTTP error {exc.response.status_code}.") from exc
    except Exception as exc:
        logger.error("Error scraping LinkedIn job: %s", exc, exc_info=True)
        raise ScrapingError(f"Failed to fetch LinkedIn job: {exc}. Tip: You can paste the job text directly.") from exc


async def scrape_greenhouse_job(url: str, client: httpx.AsyncClient) -> str:
    """Scrape Greenhouse postings using Greenhouse's public API endpoint with HTML fallback."""
    gh_info = extract_greenhouse_info(url)
    if gh_info:
        company_slug, job_id = gh_info
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs/{job_id}"
        logger.info("Fetching Greenhouse job via API: %s", api_url)
        try:
            res = await client.get(api_url, headers=REQUEST_HEADERS, timeout=12.0)
            if res.status_code == 200:
                data = res.json()
                title = data.get("title", "")
                raw_content = data.get("content", "")
                desc = clean_html_text(raw_content)
                return f"Role: {title}\nCompany: {company_slug.title()}\n\nJob Description:\n{desc}"
        except Exception as e:
            logger.warning("Greenhouse API request failed (%s), falling back to HTML", e)

    return await scrape_generic_job(url, client)


async def scrape_lever_job(url: str, client: httpx.AsyncClient) -> str:
    """Scrape Lever postings using Lever's public API endpoint with HTML fallback."""
    lever_info = extract_lever_info(url)
    if lever_info:
        company_slug, job_id = lever_info
        api_url = f"https://api.lever.co/v0/postings/{company_slug}/{job_id}"
        logger.info("Fetching Lever job via API: %s", api_url)
        try:
            res = await client.get(api_url, headers=REQUEST_HEADERS, timeout=12.0)
            if res.status_code == 200:
                data = res.json()
                title = data.get("text", "")
                raw_desc = data.get("description", "")
                desc = clean_html_text(raw_desc)
                lists = data.get("lists", [])
                list_texts = []
                for l in lists:
                    l_title = l.get("text", "")
                    l_content = clean_html_text(l.get("content", ""))
                    if l_title or l_content:
                        list_texts.append(f"{l_title}:\n{l_content}")
                full_desc = desc + ("\n\n" + "\n\n".join(list_texts) if list_texts else "")
                return f"Role: {title}\nCompany: {company_slug.title()}\n\nJob Description:\n{full_desc.strip()}"
        except Exception as e:
            logger.warning("Lever API request failed (%s), falling back to HTML", e)

    return await scrape_generic_job(url, client)


async def scrape_generic_job(url: str, client: httpx.AsyncClient) -> str:
    """Standard generic web scraper with JSON-LD JobPosting schema extraction."""
    logger.info("Scraping generic job URL: %s", url)
    response = await client.get(url.strip())
    response.raise_for_status()

    # Try Schema.org JobPosting structured data
    ld_data = extract_json_ld_job_posting(response.text)
    if ld_data:
        title = ld_data.get("title", "")
        company = ld_data.get("hiringOrganization", {}).get("name", "")
        raw_desc = ld_data.get("description", "")
        desc = clean_html_text(raw_desc)
        if len(desc) > 80:
            header = f"Role: {title}\nCompany: {company}\n\nJob Description:\n" if title or company else ""
            return (header + desc)[:5000]

    text = clean_html_text(response.content)
    if len(text) < 50:
        raise ScrapingError(
            "Job posting page returned very little text. "
            "The site may require JavaScript or authentication. "
            "Tip: You can copy and paste the job description text directly into the input!"
        )

    logger.info("Successfully scraped job posting (%d characters extracted)", len(text))
    return text[:5000]


async def scrape_jobs_async(url_or_text: str, client: httpx.AsyncClient | None = None) -> str:
    """
    Fetch job description text asynchronously.
    Supports:
    1. Direct job description text (bypasses scraping).
    2. LinkedIn job postings (guest API + fallback).
    3. Greenhouse, Lever, Ashby, Workable, and generic career pages.
    """
    if not url_or_text or not url_or_text.strip():
        raise ScrapingError("Job input cannot be empty. Please provide a job URL or paste the job description.")

    clean_input = url_or_text.strip()

    # Direct job text bypass: If input is not a URL, it is already the job description
    if not clean_input.startswith("http://") and not clean_input.startswith("https://"):
        if len(clean_input) >= 30:
            logger.info("Direct job description text provided (%d chars), bypassing web scraper", len(clean_input))
            return clean_input[:5000]
        else:
            raise ScrapingError("Provided job description is too short (minimum 30 characters required).")

    should_close = False
    if client is None:
        client = httpx.AsyncClient(headers=REQUEST_HEADERS, timeout=12.0, follow_redirects=True)
        should_close = True

    try:
        board = detect_job_board(clean_input)
        if board == "linkedin":
            return await scrape_linkedin_job(clean_input, client)
        elif board == "greenhouse":
            return await scrape_greenhouse_job(clean_input, client)
        elif board == "lever":
            return await scrape_lever_job(clean_input, client)
        else:
            return await scrape_generic_job(clean_input, client)

    except httpx.HTTPStatusError as exc:
        code = exc.response.status_code
        logger.error("Job URL returned HTTP %d: %s", code, clean_input)
        if code in (401, 403):
            raise ScrapingError(f"Access to job page was denied (HTTP {code}). Tip: You can paste the job text directly.") from exc
        elif code == 404:
            raise ScrapingError(f"Job posting URL not found (HTTP 404). Please verify the link.") from exc
        else:
            raise ScrapingError(f"Job posting page returned error HTTP {code}.") from exc

    except httpx.TimeoutException as exc:
        logger.error("Timeout scraping job URL: %s", clean_input)
        raise ScrapingError(f"Timed out while connecting to job site. The site may be slow. Tip: You can paste the job text directly.") from exc

    except ScrapingError:
        raise

    except Exception as exc:
        logger.error("Unexpected error scraping job URL %s: %s", clean_input, exc, exc_info=True)
        raise ScrapingError(f"Failed to fetch job URL: {exc}. Tip: You can paste the job description text directly.") from exc

    finally:
        if should_close:
            await client.aclose()


async def scrape_company_page_async(job_url: str, client: httpx.AsyncClient | None = None) -> str:
    """
    Scrape company about/blog page to analyze company tone.
    Skips job boards (LinkedIn, Greenhouse, etc.) to prevent analyzing the job board's tone.
    """
    if not job_url or not (job_url.startswith("http://") or job_url.startswith("https://")):
        return ""

    base_url = extract_company_base_url(job_url)
    if not base_url:
        return ""

    candidate_pages = [
        f"{base_url}/about",
        f"{base_url}/about-us",
        f"{base_url}/blog",
        f"{base_url}/company",
        base_url
    ]

    should_close = False
    if client is None:
        client = httpx.AsyncClient(headers=REQUEST_HEADERS, timeout=8.0, follow_redirects=True)
        should_close = True

    async def _fetch_candidate(page_url: str) -> str:
        try:
            res = await client.get(page_url)
            if res.status_code == 200:
                text = clean_html_text(res.content)
                if len(text) > 200:
                    return text[:2000]
        except Exception:
            pass
        return ""

    try:
        results = await asyncio.gather(
            *[_fetch_candidate(page_url) for page_url in candidate_pages],
            return_exceptions=True
        )
        for candidate_text in results:
            if isinstance(candidate_text, str) and candidate_text:
                return candidate_text
        return ""
    finally:
        if should_close:
            await client.aclose()


def scrape_jobs(url: str) -> str:
    """Synchronous compatibility wrapper"""
    return asyncio.run(scrape_jobs_async(url))


def scrape_company_page(job_url: str) -> str:
    """Synchronous compatibility wrapper"""
    return asyncio.run(scrape_company_page_async(job_url))