# scripts/

Small maintenance scripts for the mybone.health site.

Before publishing a new post, work through
[`docs/PUBLISHING-CHECKLIST.md`](../docs/PUBLISHING-CHECKLIST.md). It records the
SEO and AI-discoverability standards the site was brought up to in the July 2026
audit.

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

## build-feeds.py

Regenerates `feed.xml` (RSS 2.0) and `atom.xml` (Atom 1.0) by scanning `blog/`.
Each post contributes its title, description, date, tag, and full article body.

**You normally never need to run this by hand either.** As of July 2026 the same
GitHub Action runs it alongside the sitemap on every push to `main`. Before that
change the feeds were built manually, which meant they drifted: they sat for a
while carrying post titles that had already been rewritten on the site.

### Running it locally

```bash
python3 scripts/build-feeds.py
```

No dependencies beyond a standard Python 3.11+ install.

### Why the output is deterministic

Both `lastBuildDate` in the RSS feed and the feed-level `updated` in the Atom
feed are derived from the **newest post's date**, not from the current clock.
Rebuilding without publishing anything therefore produces byte-identical files,
which is what keeps the Action from creating a no-op commit on every push.

If you ever change this, the Action will start committing on every push.

### Feeds and AI discovery

The feeds carry the full article text in `content:encoded`, so they are a
complete, cheaply parseable copy of the blog. Some AI crawlers and aggregators
prefer a feed over walking the HTML. A stale feed means those systems see stale
titles and miss new posts entirely.
