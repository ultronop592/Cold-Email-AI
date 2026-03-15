import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, SSLError
from urllib.parse import urlparse


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}


def scrape_jobs(url):
    try:
        response = requests.get(url, timeout=10, headers=REQUEST_HEADERS)
        response.raise_for_status()
    except SSLError:
        response = requests.get(url, timeout=10, headers=REQUEST_HEADERS, verify=False)
        response.raise_for_status()
    except RequestException as exc:
        raise ValueError(f"Failed to fetch job URL: {exc}") from exc

    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()
    return text[:5000]


def extract_company_base_url(job_url):
    """Extract base company URL from job posting URL"""
    parsed = urlparse(job_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    return base


def scrape_company_page(job_url):
    """
    Try to scrape company about/blog page to analyze their tone.
    Falls back gracefully if page is not accessible.
    """
    base_url = extract_company_base_url(job_url)

    # Pages to try in order
    candidate_pages = [
        f"{base_url}/about",
        f"{base_url}/about-us",
        f"{base_url}/blog",
        f"{base_url}/company",
        base_url
    ]

    for page_url in candidate_pages:
        try:
            response = requests.get(
                page_url,
                timeout=10,
                headers=REQUEST_HEADERS
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                # Remove nav, footer, scripts — we only want body copy
                for tag in soup(["nav", "footer", "script", "style", "header"]):
                    tag.decompose()

                text = soup.get_text(separator=" ", strip=True)

                # Only return if we got meaningful content
                if len(text) > 200:
                    return text[:2000]

        except Exception:
            # Silently try next page
            continue

    # If nothing worked return empty string
    # Pipeline handles this gracefully
    return ""