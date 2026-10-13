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

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = REPO_ROOT / "blog"
SITEMAP_PATH = REPO_ROOT / "sitemap.xml"
BASE_URL = "https://mybone.health"

# Static pages that aren't blog posts. Add new top-level pages here if needed.
STATIC_PAGES = [
    {"loc": f"{BASE_URL}/",                                          "changefreq": "weekly",  "priority": "1.0"},
    {"loc": f"{BASE_URL}/about.html",                                "changefreq": "monthly", "priority": "0.8"},
    {"loc": f"{BASE_URL}/faq.html",                                  "changefreq": "monthly", "priority": "0.8"},
    {"loc": f"{BASE_URL}/blog/",                                     "changefreq": "weekly",  "priority": "0.9"},
    {"loc": f"{BASE_URL}/free/calcium-protein-cheat-sheet.html",     "changefreq": "monthly", "priority": "0.8"},
    {"loc": f"{BASE_URL}/editorial-policy.html",                     "changefreq": "yearly",  "priority": "0.7"},
    {"loc": f"{BASE_URL}/medical-disclaimer.html",                   "changefreq": "yearly",  "priority": "0.6"},
    {"loc": f"{BASE_URL}/privacy.html",                              "changefreq": "yearly",  "priority": "0.3"},
]

# Files in blog/ that aren't individual blog posts (the index, drafts, etc.)
BLOG_EXCLUDES = {"index.html"}

# Date regex: matches "2026-06-02" inside `"datePublished": "2026-06-02..."`
DATE_RE = re.compile(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})')
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

# Node types that describe the page itself (as opposed to a Book or Person
# that happens to be embedded on the page).
PAGE_TYPES = {"BlogPosting", "MedicalWebPage", "WebPage", "AboutPage", "FAQPage",
              "CollectionPage", "Article"}


def page_dates(text: str) -> dict:
    """Return the datePublished/dateModified/lastReviewed of the page-level node."""
    for block in LD_RE.findall(text):
        try:
            data = json.loads(block)
        except Exception:
            continue
        stack = [data]
        while stack:
            n = stack.pop()
            if isinstance(n, list):
                stack.extend(n)
                continue
            if not isinstance(n, dict):
                continue
            t = n.get("@type")
            types = set(t if isinstance(t, list) else [t])
            if types & PAGE_TYPES and any(k in n for k in ("datePublished", "dateModified", "lastReviewed")):
                return {k: str(n[k])[:10] for k in ("datePublished", "dateModified", "lastReviewed") if n.get(k)}
            stack.extend(n.get("@graph", []) if isinstance(n.get("@graph"), list) else [])
    return {}


def git_date(path: Path) -> str | None:
    """Date of the last commit that touched this file (needs full git history)."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path)],
                             cwd=REPO_ROOT, capture_output=True, text=True, timeout=20)
        d = out.stdout.strip()
        return d if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) else None
    except Exception:
        return None


def static_lastmod(loc: str, newest_post: str | None) -> str | None:
    """Real last-modified date for a static page instead of today's date.

    Homepage and blog index change whenever a post is added, so they use the
    newest post date. Other pages use their own JSON-LD dateModified, then the
    file's last git commit. If nothing is known, lastmod is omitted, which is
    better for search engines than a date that changes every day.
    """
    rel = loc.replace(BASE_URL + "/", "") or "index.html"
    if rel.endswith("/"):
        rel += "index.html"
    path = REPO_ROOT / rel
    candidates = []
    if rel in ("index.html", "blog/index.html") and newest_post:
        candidates.append(newest_post)
    if path.exists():
        d = page_dates(path.read_text(encoding="utf-8"))
        if d.get("dateModified") or d.get("datePublished"):
            candidates.append(d.get("dateModified") or d.get("datePublished"))
        elif rel not in ("index.html", "blog/index.html"):
            g = git_date(path)
            if g:
                candidates.append(g)
    return max(candidates) if candidates else None


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
        # lastmod = the most recent real content date: dateModified or
        # lastReviewed when the post has been updated or medically re-reviewed.
        pd = page_dates(html.read_text(encoding="utf-8"))
        lastmod = max([d] + [v for k, v in pd.items() if k in ("dateModified", "lastReviewed")])
        posts.append({
            "loc": f"{BASE_URL}/blog/{html.name}",
            "published": d,
            "lastmod": lastmod,
        })
    # newest first (by publication date, so the order stays stable)
    posts.sort(key=lambda p: p["published"], reverse=True)
    return posts


def build_sitemap() -> str:
    posts = collect_blog_posts()
    newest_post = max((p["lastmod"] for p in posts), default=None)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    # Static pages: use each page's real last-modified date (see static_lastmod).
    for p in STATIC_PAGES:
        lines.append("  <url>")
        lines.append(f'    <loc>{p["loc"]}</loc>')
        lm = static_lastmod(p["loc"], newest_post)
        if lm:
            lines.append(f"    <lastmod>{lm}</lastmod>")
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
