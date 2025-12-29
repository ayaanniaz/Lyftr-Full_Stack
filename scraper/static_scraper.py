import requests
from bs4 import BeautifulSoup


def fetch_static_html(url, timeout=12):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; LyftrScraper/1.0)"
    }
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.text


def extract_meta(html):
    soup = BeautifulSoup(html, "html.parser")

    # Title
    title = ""
    if soup.title and soup.title.text:
        title = soup.title.text.strip()

    # Description
    description = ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    if desc_tag and desc_tag.get("content"):
        description = desc_tag["content"].strip()

    # Language
    language = ""
    if soup.html and soup.html.get("lang"):
        language = soup.html.get("lang")

    # Canonical
    canonical = None
    canon_tag = soup.find("link", rel="canonical")
    if canon_tag and canon_tag.get("href"):
        canonical = canon_tag["href"]

    return {
        "title": title,
        "description": description,
        "language": language,
        "canonical": canonical
    }
