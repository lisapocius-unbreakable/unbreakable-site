#!/usr/bin/env python3
"""Add BreadcrumbList JSON-LD to every blog post that does not already have one.

Idempotent: skips files that already contain '"@type": "BreadcrumbList"'.
Placement: inserts a fresh <script type="application/ld+json"> block immediately
after the closing </script> of the first BlogPosting JSON-LD block.
"""
import json
import re
from pathlib import Path

BLOG = Path(__file__).resolve().parent.parent / "blog"

# Post-title lookup for the breadcrumb's third crumb.
# Uses the current <h1> text of each post, cleaned of html entities.

def h1_text(html: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.S)
    if not m:
        return ""
    text = re.sub(r"<[^>]+>", "", m.group(1))
    text = text.replace("&amp;", "&").replace("&nbsp;", " ")
    return " ".join(text.split())


def slug_to_url(name: str) -> str:
    return f"https://mybone.health/blog/{name}"


def build_breadcrumb(slug: str, post_title: str) -> str:
    url = slug_to_url(slug)
    name_json = json.dumps(post_title)
    return f"""    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "@id": "{url}#breadcrumb",
      "itemListElement": [
        {{
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://mybone.health/"
        }},
        {{
          "@type": "ListItem",
          "position": 2,
          "name": "Blog",
          "item": "https://mybone.health/blog/"
        }},
        {{
          "@type": "ListItem",
          "position": 3,
          "name": {name_json}
        }}
      ]
    }}
    </script>"""


def process(path: Path) -> str:
    html = path.read_text(encoding="utf-8")
    if '"@type": "BreadcrumbList"' in html:
        return "skip (already present)"

    title = h1_text(html)
    if not title:
        return "skip (no h1 found)"

    # Find the first JSON-LD script block (the BlogPosting) and insert after it.
    pattern = re.compile(
        r'(<script type="application/ld\+json">.*?</script>)',
        flags=re.S,
    )
    m = pattern.search(html)
    if not m:
        return "skip (no JSON-LD block found)"

    end = m.end()
    breadcrumb = build_breadcrumb(path.name, title)
    # Validate the produced JSON before writing.
    inner = re.search(r'<script[^>]*>(.*?)</script>', breadcrumb, flags=re.S).group(1)
    json.loads(inner)
    new_html = html[:end] + "\n" + breadcrumb + html[end:]
    path.write_text(new_html, encoding="utf-8")
    return f"added ({title})"


def main():
    for path in sorted(BLOG.glob("*.html")):
        if path.name == "index.html":
            continue
        status = process(path)
        print(f"{path.name}: {status}")


if __name__ == "__main__":
    main()
