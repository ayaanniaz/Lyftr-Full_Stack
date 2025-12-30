from playwright.sync_api import sync_playwright, TimeoutError


def fetch_js_rendered_html(url, interactions, timeout=30000):
    """
    Robust infinite scroll implementation:
    - Scroll-triggered DOM mutation detection
    - Ensures >= 3 scrolls
    - Tracks pages + scroll count
    """
    def perform_scrolls(page, interactions, max_scrolls=3):
            last_height = page.evaluate("document.body.scrollHeight")

            for _ in range(max_scrolls):
                page.mouse.wheel(0, last_height)
                page.wait_for_timeout(1500)

                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break

                last_height = new_height
                interactions["scrolls"] += 1
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800}
        )

        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        perform_scrolls(page, interactions)
        interactions["pages"].append(page.url)

        # Wait for first articles
        page.wait_for_selector(".article", timeout=timeout)

        last_article_count = page.locator(".article").count()

        for _ in range(3):  # REQUIRED depth
            # Scroll to bottom
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            interactions["scrolls"] += 1

            try:
                # Wait until new articles load
                page.wait_for_function(
                    """
                    () => document.querySelectorAll('.article').length > %d
                    """ % last_article_count,
                    timeout=10000
                )
            except TimeoutError:
                break  # No more content

            new_count = page.locator(".article").count()
            last_article_count = new_count

            # Track URL change (history.pushState)
            if page.url not in interactions["pages"]:
                interactions["pages"].append(page.url)

        html = page.content()


        context.close()
        browser.close()

        return html
