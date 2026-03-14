import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, SSLError


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}


def scrape_jobs(url):
    try:
        response = requests.get(url, timeout=20, headers=REQUEST_HEADERS)
        response.raise_for_status()
    except SSLError:
        # Fallback for local machines with SSL cert chain issues.
        response = requests.get(url, timeout=20, headers=REQUEST_HEADERS, verify=False)
        response.raise_for_status()
    except RequestException as exc:
        raise ValueError(f"Failed to fetch job URL: {exc}") from exc

    soup = BeautifulSoup(response.content, 'html.parser')
    text  = soup.get_text()
    return text[:5000]
