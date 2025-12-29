from bs4 import BeautifulSoup
from scraper.utils import make_absolute_url, truncate_html, clean_text

def extract_image_grid(soup, base_url):
    sections = []

    figures = soup.find_all("figure", attrs={"itemprop": "image"})
    if not figures:
        return sections

    images = []

    for fig in figures:
        img = fig.find("img")
        if not img:
            continue

        # Image URL
        src = extract_image_src(img)
        if not src:
            continue

        # Title / description
        title = ""
        link = fig.find("a", title=True)
        if link:
            title = link.get("title", "")

        meta_name = fig.find("meta", attrs={"itemprop": "name"})
        if meta_name:
            title = meta_name.get("content", title)

        alt = img.get("alt", title)

        images.append({
            "src": make_absolute_url(base_url, src),
            "alt": alt
        })

    if images:
        raw_html, truncated = truncate_html(str(figures[0]))

        sections.append({
            "id": "grid-0",
            "type": "grid",
            "label": "Image results",
            "sourceUrl": base_url,
            "content": {
                "headings": [],
                "text": "",
                "links": [],
                "images": images,
                "lists": [],
                "tables": []
            },
            "rawHtml": raw_html,
            "truncated": truncated
        })

    return sections


SEMANTIC_TAGS = ["section", "main", "article", "nav", "footer", "header"]
def is_placeholder_text(text):
    if not text:
        return True
    stripped = text.replace("–", "").replace("-", "").strip()
    return len(stripped) < 10


def infer_section_type(tag_name):
    mapping = {
        "nav": "nav",
        "footer": "footer",
        "header": "hero",
        "main": "section",
        "article": "section",
        "section": "section",
        "table": "list"
    }
    return mapping.get(tag_name, "unknown")


def extract_semantic_sections(soup, base_url):
    sections = []

    candidates = soup.find_all(SEMANTIC_TAGS)

    for idx, node in enumerate(candidates):
        text = clean_text(node.get_text(" ", strip=True))
        if len(text) < 50:
            continue

        headings = [
            clean_text(h.get_text())
            for h in node.find_all(["h1", "h2", "h3"])
        ]

        label = headings[0] if headings else " ".join(text.split()[:6])

        links = []
        for a in node.find_all("a", href=True):
            links.append({
                "text": clean_text(a.get_text()),
                "href": make_absolute_url(base_url, a.get("href"))
            })

        raw_html, truncated = truncate_html(str(node))

        sections.append({
            "id": f"{infer_section_type(node.name)}-{idx}",
            "type": infer_section_type(node.name),
            "label": label,
            "sourceUrl": base_url,
            "content": {
                "headings": headings,
                "text": text,
                "links": links,
                "images": [],
                "lists": [],
                "tables": []
            },
            "rawHtml": raw_html,
            "truncated": truncated
        })

    return sections


def extract_table_based_sections(soup, base_url):
    """
    Fallback for table-based sites like Hacker News
    """
    sections = []

    rows = soup.find_all("tr", class_="athing")

    for idx, row in enumerate(rows):
        title_link = row.find("a", class_="storylink") or row.find("a")
        if not title_link:
            continue

        title = clean_text(title_link.get_text())
        href = make_absolute_url(base_url, title_link.get("href"))

        text = title
        raw_html, truncated = truncate_html(str(row))

        sections.append({
            "id": f"item-{idx}",
            "type": "list",
            "label": title[:80],
            "sourceUrl": base_url,
            "content": {
                "headings": [title],
                "text": text,
                "links": [
                    {
                        "text": title,
                        "href": href
                    }
                ],
                "images": [],
                "lists": [],
                "tables": []
            },
            "rawHtml": raw_html,
            "truncated": truncated
        })

    return sections

def extract_image_src(img_tag):
    """
    Extracts best possible image URL from img tag.
    Handles src, srcset, and data-src.
    """
    # 1. Normal src
    if img_tag.get("src"):
        return img_tag.get("src")

    # 2. srcset (take first URL)
    srcset = img_tag.get("srcset")
    if srcset:
        # Format: "url1 200w, url2 400w"
        first = srcset.split(",")[0].strip()
        return first.split(" ")[0]

    # 3. data-src fallback
    if img_tag.get("data-src"):
        return img_tag.get("data-src")

    return None

def extract_sections(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    sections = []

    # ---- 1. SEMANTIC SECTIONS (existing logic) ----
    semantic_nodes = soup.find_all(
        ["section", "main", "article", "nav", "header", "footer"]
    )

    idx = 0
    for node in semantic_nodes:
        text = clean_text(node.get_text(" ", strip=True))
        if len(text) < 50 or is_placeholder_text(text):
            continue

        headings = [
            clean_text(h.get_text())
            for h in node.find_all(["h1", "h2", "h3"])
        ]

        label = headings[0] if headings else " ".join(text.split()[:6])

        images = []
        for img in node.find_all("img"):
            src = extract_image_src(img)
            if src:
                images.append({
                    "src": make_absolute_url(base_url, src),
                    "alt": img.get("alt", "")
                })

        links = [
            {
                "text": clean_text(a.get_text()),
                "href": make_absolute_url(base_url, a.get("href"))
            }
            for a in node.find_all("a", href=True)
        ]

        raw_html, truncated = truncate_html(str(node))

        sections.append({
            "id": f"{node.name}-{idx}",
            "type": "nav" if node.name == "nav" else "footer" if node.name == "footer" else "section",
            "label": label,
            "sourceUrl": base_url,
            "content": {
                "headings": headings,
                "text": text,
                "links": links,
                "images": images,
                "lists": [],
                "tables": []
            },
            "rawHtml": raw_html,
            "truncated": truncated
        })
        idx += 1

    # ---- 2. IMAGE GRID FALLBACK (Unsplash-style) ----
    # ---- 2. IMAGE GRID EXTRACTION (Unsplash-style) ----
    grid_sections = extract_image_grid(soup, base_url)
    sections.extend(grid_sections)


    return sections

