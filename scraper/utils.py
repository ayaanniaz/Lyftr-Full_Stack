from urllib.parse import urljoin
import re

MAX_HTML_CHARS = 2000


def make_absolute_url(base_url, link):
    """
    Converts relative URLs to absolute URLs
    """
    if not link:
        return None
    return urljoin(base_url, link)


def truncate_html(html):
    """
    Truncates raw HTML and indicates if truncation occurred
    """
    if len(html) <= MAX_HTML_CHARS:
        return html, False
    return html[:MAX_HTML_CHARS], True


def clean_text(text):
    """
    Normalizes whitespace and strips text
    """
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()
