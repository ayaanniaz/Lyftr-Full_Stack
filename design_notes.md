# Design Notes

## Static vs JS Rendering Strategy
- The scraper first attempts **static HTML scraping** using `requests` for performance and simplicity.
- JS rendering via **Playwright** is triggered when:
  - No meaningful sections are extracted from static HTML, **or**
  - The HTML contains indicators of dynamic behavior such as infinite scroll or pagination (e.g., `data-infinite-scroll`, `pagination__next`, `load more`), **or**
  - The number of extracted sections is very small, suggesting partial content.
- This heuristic prevents false negatives on sites that return initial content statically but rely on JavaScript to load additional data.

## Heuristics for JS Rendering
- JS rendering decisions are based on both:
  - Extracted section metadata, and
  - Raw HTML inspection for dynamic-loading markers.
- Infinite-scroll sites are explicitly detected and handled even if initial static content exists.

## Wait & Synchronization Strategy (JS)
- Initial navigation waits for `domcontentloaded`.
- For infinite scroll pages:
  - Scrolling is performed programmatically.
  - The scraper waits for **DOM mutation** (increase in content elements such as `.article`) rather than relying on scroll height alone.
- Fixed delays are used conservatively after scrolls and clicks to allow asynchronous content loading.

## Click, Scroll & Pagination Strategy
- Click flows are attempted for generic interaction patterns such as:
  - “Load more”
  - “Show more”
- Infinite scroll is implemented by:
  - Repeatedly scrolling to the bottom of the page,
  - Waiting for new content to be appended to the DOM,
  - Ensuring a **minimum scroll depth of three**.
- Pagination triggered via `history.pushState` is supported and detected during scrolling.
- All interactions are recorded in the `interactions` object:
  - `clicks`: attempted click selectors or descriptions,
  - `scrolls`: number of scroll actions performed,
  - `pages`: all distinct URLs visited during the scrape.

## Section Grouping & Classification
- Semantic HTML elements (`section`, `main`, `article`, `nav`, `header`, `footer`) are treated as sections.
- Section types are inferred from tag semantics (e.g., `nav`, `footer`, `section`, `list`, `grid`).
- Section labels are derived from:
  - The first heading when present, or
  - The first few meaningful words of the section text.

## Image-Heavy & Grid-Based Pages
- Image grid layouts (e.g., Unsplash-style pages) are detected explicitly.
- `<figure>` elements representing images are grouped into a single `grid` section.
- Image URLs are extracted using a fallback strategy:
  - `src` → first candidate in `srcset` → `data-src`.
- Image metadata such as titles and alt text are extracted from attributes and structured data (`alt`, `title`, `meta[itemprop]`) rather than visible text.
- This approach supports responsive image layouts without bypassing bot protection.

## Noise Filtering & Content Validation
- Obvious noise elements such as cookie banners, modals, consent dialogs, and popups are removed during JS rendering using CSS selectors.
- Placeholder and skeleton content (e.g., repeated dashes or loading indicators) is ignored.
- Very small or non-informative sections are filtered out to avoid false positives.

## HTML Truncation
- Each section includes a `rawHtml` snapshot.
- Large HTML snippets are truncated to a fixed character limit.
- A `truncated` flag indicates whether truncation occurred.

## Error Handling & Partial Results
- Reasonable timeouts are enforced for network requests and browser actions.
- Errors are captured with clear messages and a `phase` indicator (e.g., `fetch`, `render`, `parse`).
- When failures occur, **partial but consistent results** are returned instead of aborting the entire scrape.

## Platform Considerations
- The project is platform-agnostic.
- Unix shell scripts (e.g., `run.sh`) are optional and intended for Unix-based systems.
- On Windows, the application is run directly via Python with an activated virtual environment.
