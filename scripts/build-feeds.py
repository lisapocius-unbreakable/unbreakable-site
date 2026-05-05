#!/usr/bin/env python3
"""
Build RSS 2.0 (feed.xml) and Atom 1.0 (atom.xml) feeds for mybone.health
by scanning the blog/ folder.

Usage (from repo root):
    python3 scripts/build-feeds.py

Outputs:
    feed.xml  (RSS 2.0)
    atom.xml  (Atom 1.0)

Each blog post is parsed for title, description, date, tag, and article body.
The script intentionally has no external dependencies so it runs anywhere.
"""

import os
import re
import sys
import html
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

# Site configuration
SITE_URL = "https://mybone.health"
SITE_TITLE = "mybone.health Blog"
SITE_DESCRIPTION = "Evidence-based articles on osteoporosis, bone health, and living well with bone loss, by Dr. Lisa Pocius."
SITE_AUTHOR_NAME = "Dr. Lisa Pocius"
SITE_AUTHOR_EMAIL = "lisa.pocius@gmail.com"
SITE_LANGUAGE = "en-us"

# Locate paths relative to this script's location, so it works from any CWD
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BLOG_DIR = REPO_ROOT / "blog"
RSS_OUT = REPO_ROOT / "feed.xml"
ATOM_OUT = REPO_ROOT / "atom.xml"


def extract(pattern, text, flags=re.DOTALL, group=1, default=""):
    m = re.search(pattern, text, flags)
    return m.group(group).strip() if m else default


def parse_post(html_path: Path):
    """Extract metadata and article body from a single blog post."""
    raw = html_path.read_text(encoding="utf-8")
    slug = html_path.stem

    # Title: from <title>...</title>, strip any trailing " | mybone.health"
    # or " | Osteoporosis" suffix used in older posts.
    page_title = extract(r"<title>(.*?)</title>", raw)
    title = re.sub(
        r"\s*\|\s*(mybone\.health|Osteoporosis)\s*$", "", page_title, flags=re.IGNORECASE
    ).strip()

    # Description: from <meta name="description" content="...">
    description = extract(
        r'<meta\s+name="description"\s+content="([^"]+)"', raw, flags=re.IGNORECASE
    )

    # Tag: from <span class="post-tag">...</span>
    tag = extract(r'<span class="post-tag">(.*?)</span>', raw)

    # Date: from <p class="post-meta">May 3, 2026 &middot; By ...</p>
    meta_text = extract(r'<p class="post-meta">(.*?)</p>', raw)
    # Strip HTML entities and pull just the date portion before the middot/bullet
    meta_clean = re.sub(r"<[^>]+>", "", meta_text)
    meta_clean = html.unescape(meta_clean)
    date_str = re.split(r"[·•]|By\s", meta_clean)[0].strip()
    try:
        post_date = datetime.strptime(date_str, "%B %d, %Y").replace(tzinfo=timezone.utc)
    except ValueError:
        # Fallback: file mtime
        post_date = datetime.fromtimestamp(html_path.stat().st_mtime, tz=timezone.utc)

    # Article body: contents of <article class="post-body">...</article>
    body = extract(r'<article class="post-body">(.*?)</article>', raw)
    # Drop the disclaimer block and the back link; feed readers don't need them
    body = re.sub(r'<div class="post-disclaimer">.*?</div>', "", body, flags=re.DOTALL)
    body = re.sub(r'<a href="index\.html" class="back-link">.*?</a>', "", body, flags=re.DOTALL)
    body = body.strip()

    return {
        "slug": slug,
        "title": title,
        "description": description,
        "tag": tag,
        "date": post_date,
        "body_html": body,
        "url": f"{SITE_URL}/blog/{slug}.html",
    }


def collect_posts():
    posts = []
    for path in sorted(BLOG_DIR.glob("*.html")):
        if path.name == "index.html":
            continue
        try:
            posts.append(parse_post(path))
        except Exception as e:
            print(f"  ! Skipping {path.name}: {e}", file=sys.stderr)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def xml_escape(text):
    """Escape text for safe inclusion in XML element/attribute values."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_rss(posts):
    now = datetime.now(timezone.utc)
    items = []
    for p in posts:
        items.append(
            f"""    <item>
      <title>{xml_escape(p['title'])}</title>
      <link>{p['url']}</link>
      <guid isPermaLink="true">{p['url']}</guid>
      <pubDate>{format_datetime(p['date'])}</pubDate>
      <category>{xml_escape(p['tag'])}</category>
      <description>{xml_escape(p['description'])}</description>
      <content:encoded><![CDATA[{p['body_html']}]]></content:encoded>
    </item>"""
        )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{xml_escape(SITE_TITLE)}</title>
    <link>{SITE_URL}</link>
    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml" />
    <description>{xml_escape(SITE_DESCRIPTION)}</description>
    <language>{SITE_LANGUAGE}</language>
    <lastBuildDate>{format_datetime(now)}</lastBuildDate>
    <managingEditor>{SITE_AUTHOR_EMAIL} ({SITE_AUTHOR_NAME})</managingEditor>
{chr(10).join(items)}
  </channel>
</rss>
"""


def iso8601(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_atom(posts):
    now = datetime.now(timezone.utc)
    updated = posts[0]["date"] if posts else now
    entries = []
    for p in posts:
        entries.append(
            f"""  <entry>
    <title>{xml_escape(p['title'])}</title>
    <link href="{p['url']}" />
    <id>{p['url']}</id>
    <updated>{iso8601(p['date'])}</updated>
    <published>{iso8601(p['date'])}</published>
    <category term="{xml_escape(p['tag'])}" />
    <summary>{xml_escape(p['description'])}</summary>
    <content type="html"><![CDATA[{p['body_html']}]]></content>
    <author>
      <name>{xml_escape(SITE_AUTHOR_NAME)}</name>
      <email>{SITE_AUTHOR_EMAIL}</email>
    </author>
  </entry>"""
        )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{xml_escape(SITE_TITLE)}</title>
  <subtitle>{xml_escape(SITE_DESCRIPTION)}</subtitle>
  <link href="{SITE_URL}/atom.xml" rel="self" />
  <link href="{SITE_URL}" />
  <id>{SITE_URL}/</id>
  <updated>{iso8601(updated)}</updated>
  <author>
    <name>{xml_escape(SITE_AUTHOR_NAME)}</name>
    <email>{SITE_AUTHOR_EMAIL}</email>
  </author>
{chr(10).join(entries)}
</feed>
"""


def main():
    if not BLOG_DIR.is_dir():
        print(f"Blog directory not found: {BLOG_DIR}", file=sys.stderr)
        sys.exit(1)

    posts = collect_posts()
    if not posts:
        print("No posts found.", file=sys.stderr)
        sys.exit(1)

    RSS_OUT.write_text(build_rss(posts), encoding="utf-8")
    ATOM_OUT.write_text(build_atom(posts), encoding="utf-8")

    print(f"Built feeds from {len(posts)} posts:")
    for p in posts:
        print(f"  - {p['date'].strftime('%Y-%m-%d')}  {p['title']}")
    print(f"\nWrote:")
    print(f"  {RSS_OUT.relative_to(REPO_ROOT)}")
    print(f"  {ATOM_OUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
