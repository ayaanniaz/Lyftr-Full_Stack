from datetime import datetime
from scraper.static_scraper import fetch_static_html, extract_meta
from scraper.js_scraper import fetch_js_rendered_html
from scraper.parser import extract_sections
from scraper.heuristics import needs_js_rendering


def scrape_url(url):
    # ---- REQUIRED FIELDS (ALWAYS INITIALIZED) ----
    meta = {
        "title": "",
        "description": "",
        "language": "",
        "canonical": None
    }

    interactions = {
        "clicks": [],
        "scrolls": 0,
        "pages": [url]
    }

    errors = []
    sections = []
    html = ""

    # ---- STATIC SCRAPING ----
    static_failed = False
    try:
        html = fetch_static_html(url)
        meta = extract_meta(html) or meta
        sections = extract_sections(html, url)
    except Exception as e:
        static_failed = True
        errors.append({
            "message": str(e),
            "phase": "fetch"
        })

    # ---- JS FALLBACK ----
    try:
        # Run JS if:
        # 1. static scraping failed OR
        # 2. static content looks insufficient
        if needs_js_rendering(sections, html):
            html = fetch_js_rendered_html(url, interactions)
            sections = extract_sections(html, url)
    except Exception as e:
        errors.append({
            "message": str(e),
            "phase": "render"
        })

    # ---- FINAL SAFETY ----
    # Only add parse error if:
    # - no sections
    # - and no fetch/render errors already explain why
    if not sections and not errors:
        errors.append({
            "message": "No meaningful content sections found",
            "phase": "parse"
        })

    # Remove duplicate pages (clean output)
    interactions["pages"] = list(dict.fromkeys(interactions["pages"]))

    # ---- FINAL RESULT ----
    return {
        "url": url,
        "scrapedAt": datetime.utcnow().isoformat() + "Z",
        "meta": meta,
        "sections": sections,
        "interactions": interactions,
        "errors": errors
    }
