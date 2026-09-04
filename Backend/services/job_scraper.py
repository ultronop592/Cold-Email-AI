import asyncio
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def extract_company_base_url(job_url: str) -> str:
    """Extract base company URL from job posting URL"""
    parsed = urlparse(job_url)
    return f"{parsed.scheme}://{parsed.netloc}"


def clean_html_text(html_content: bytes | str) -> str:
    """Extract clean textual content by removing navigation, footer, scripts, etc."""
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["nav", "footer", "script", "style", "header", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


async def scrape_jobs_async(url: str, client: httpx.AsyncClient | None = None) -> str:
    """
    Fetch job description text asynchronously.
    """
    should_close = False
    if client is None:
        client = httpx.AsyncClient(headers=REQUEST_HEADERS, timeout=10.0, follow_redirects=True)
        should_close = True

    try:
        response = await client.get(url)
        response.raise_for_status()
        text = clean_html_text(response.content)
        return text[:5000]
    except httpx.HTTPError as exc:
        raise ValueError(f"Failed to fetch job URL: {exc}") from exc
    except Exception as exc:
        raise ValueError(f"Failed to parse job URL content: {exc}") from exc
    finally:
        if should_close:
            await client.aclose()


async def scrape_company_page_async(job_url: str, client: httpx.AsyncClient | None = None) -> str:
    """
    Scrape company about/blog page to analyze their tone.
    Fires concurrent requests to candidate pages with asyncio.gather
    and returns the highest-priority page with meaningful text.
    """
    base_url = extract_company_base_url(job_url)

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
        # Request all candidate pages concurrently
        results = await asyncio.gather(
            *[_fetch_candidate(page_url) for page_url in candidate_pages],
            return_exceptions=True
        )

        # Iterate in priority order and return first successful content
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