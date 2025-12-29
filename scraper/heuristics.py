def needs_js_rendering(sections, html=None):
    """
    Decide whether JS rendering is needed.
    """

    # 1. No sections at all → JS needed
    if not sections:
        return True

    # 2. Infinite scroll / pagination indicators
    if html:
        html_lower = html.lower()
        infinite_markers = [
            "infinite-scroll",
            "pagination__next",
            "load more",
            "data-infinite-scroll",
        ]
        if any(marker in html_lower for marker in infinite_markers):
            return True

    # 3. Sections exist but very few (likely partial load)
    if len(sections) < 3:
        return True

    return False

