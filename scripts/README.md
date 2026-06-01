# scripts/

Small maintenance scripts for the mybone.health site.

## generate_sitemap.py

Regenerates the site's `sitemap.xml` automatically.

**You normally never need to run this by hand.** A GitHub Action
(`.github/workflows/sitemap.yml`) runs it on every push to `main` and commits
the updated `sitemap.xml` back to the repo if anything changed.

### How it works

1. Scans every `blog/*.html` file (skipping `index.html` and any `draft-*` files)
2. Pulls each post's `datePublished` from its embedded `BlogPosting` JSON-LD
3. Writes a fresh `sitemap.xml` with:
   - Static pages (homepage, FAQ, blog index) with today's date
   - Every blog post, sorted newest first, with its actual publish date

### Running it locally

```bash
python3 scripts/generate_sitemap.py
```

No dependencies beyond a standard Python 3.11+ install. Prints what it wrote
and exits 0 either way (changed or unchanged).

### Adding a new top-level page

If you add a new static page (e.g. `/about.html`), edit the `STATIC_PAGES` list
near the top of `generate_sitemap.py`. The script handles all blog posts
automatically — you only edit this when adding non-blog pages.

### Why we do this

Crawlers (Google, Bing, GPTBot, PerplexityBot, ClaudeBot, etc.) read
`sitemap.xml` to discover and re-fetch pages. Missing entries slow down
indexing, especially for AI crawlers that are less exhaustive than Google.
Keeping it auto-generated means we can never forget to add a new post.
