#!/usr/bin/env python3
"""
Regenerate sitemap.xml for mybone.health.

Scans every blog/*.html file, extracts its `datePublished` from the BlogPosting
JSON-LD block, and writes a fresh sitemap with:
  - the static top-level pages (homepage, FAQ, blog index)
  - every published blog post, newest first

This runs automatically on every push to `main` via .github/workflows/sitemap.yml,
and can also be run by hand:  python3 scripts/generate_sitemap.py

If sitemap.xml does not change, the file is left untouched (no spurious commits).
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = REPO_ROOT / "blog"
SITEMAP_PATH = REPO_ROOT / "sitemap.xml"
BASE_URL = "https://mybone.health"

# Static pages that aren't blog posts. Add new top-level pages here if needed.
STATIC_PAGES = [
    {"loc": f"{BASE_URL}/",           "changefreq": "weekly",  "priority": "1.0"},
    {"loc": f"{BASE_URL}/about.html", "changefreq": "monthly", "priority": "0.8"},
    {"loc": f"{BASE_URL}/faq.html",   "changefreq": "monthly", "priority": "0.8"},
    {"loc": f"{BASE_URL}/blog/",      "changefreq": "weekly",  "priority": "0.9"},
]

# Files in blog/ that aren't individual blog posts (the index, drafts, etc.)
BLOG_EXCLUDES = {"index.html"}

# Date regex: matches "2026-06-02" inside `"datePublished": "2026-06-02..."`
DATE_RE = re.compile(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})')


def extract_post_date(html_path: Path) -> str | None:
    """Return ISO date (YYYY-MM-DD) from a post's BlogPosting JSON-LD, or None."""
    try:
        text = html_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  WARN: could not read {html_path.name}: {e}", file=sys.stderr)
        return None
    m = DATE_RE.search(text)
    if not m:
        print(f"  WARN: no datePublished found in {html_path.name}", file=sys.stderr)
        return None
    return m.group(1)


def collect_blog_posts() -> list[dict]:
    """Find every blog post, return list of {loc, lastmod} sorted newest first."""
    posts = []
    for html in sorted(BLOG_DIR.glob("*.html")):
        if html.name in BLOG_EXCLUDES:
            continue
        # Skip drafts (anything starting with "draft-" or "_")
        if html.name.startswith(("draft-", "_")):
            continue
        d = extract_post_date(html)
        if not d:
            continue
        posts.append({
            "loc": f"{BASE_URL}/blog/{html.name}",
            "lastmod": d,
        })
    # newest first
    posts.sort(key=lambda p: p["lastmod"], reverse=True)
    return posts


def build_sitemap() -> str:
    today = date.today().isoformat()
    posts = collect_blog_posts()

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    # Static pages: use today's date as a reasonable "the site is alive" signal.
    for p in STATIC_PAGES:
        lines.append("  <url>")
        lines.append(f'    <loc>{p["loc"]}</loc>')
        lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append(f'    <changefreq>{p["changefreq"]}</changefreq>')
        lines.append(f'    <priority>{p["priority"]}</priority>')
        lines.append("  </url>")

    # Blog posts
    for post in posts:
        lines.append("  <url>")
        lines.append(f'    <loc>{post["loc"]}</loc>')
        lines.append(f'    <lastmod>{post["lastmod"]}</lastmod>')
        lines.append("    <changefreq>monthly</changefreq>")
        lines.append("    <priority>0.7</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main() -> int:
    new_content = build_sitemap()

    if SITEMAP_PATH.exists():
        current = SITEMAP_PATH.read_text(encoding="utf-8")
        if current == new_content:
            print(f"sitemap.xml unchanged ({SITEMAP_PATH})")
            return 0

    SITEMAP_PATH.write_text(new_content, encoding="utf-8")

    # Count what we wrote, for logs
    post_count = new_content.count("/blog/") - 1  # subtract the /blog/ index entry
    print(f"Wrote {SITEMAP_PATH}")
    print(f"  {len(STATIC_PAGES)} static pages + {post_count} blog posts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
