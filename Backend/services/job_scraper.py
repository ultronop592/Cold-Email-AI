import requests
from bs4 import BeautifulSoup

def scrape_jobs(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text  = soup.get_text()
    return text[:5000]
