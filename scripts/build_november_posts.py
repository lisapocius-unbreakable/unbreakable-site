#!/usr/bin/env python3
"""Build the November 2026 posts by cloning blog/protein-and-fracture-recovery.html
and swapping only the article-specific parts, so shared furniture stays
byte-identical (per docs/PUBLISHING-CHECKLIST.md).

Article bodies live in /home/user/workspace/posts/<slug>.html.

Usage:
  python3 scripts/build_october_posts.py            # build both, in date order
  python3 scripts/build_october_posts.py <slug>...  # build only these

Each post: writes blog/<slug>.html, inserts a card at the top of blog/index.html
(demoting the previous top card to lazy), inserts a card on the homepage (keeps
exactly 3), and adds that post's inbound links. Idempotent per post.

Does NOT touch sitemap.xml, feed.xml, atom.xml (the GitHub Action regenerates them).
"""
import json, pathlib, re, sys
from datetime import datetime

REPO = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "blog/protein-and-fracture-recovery.html"
T_SLUG = "protein-and-fracture-recovery"
T_H1 = "Protein After a Fracture: What Your Recovery Actually Needs"
BODIES = pathlib.Path("/home/user/workspace/posts")
# If the sandbox copy is gone, restore it with:
#   git show origin/november-posts:scripts/november-bodies/<slug>.html

POSTS = [
    dict(
        slug="holiday-table-bone-friendly-plate",
        date="2026-11-17",
        section="Nutrition",
        h1="Holiday Table, Bone-Friendly Plate: Thanksgiving With Osteoporosis",
        seo="Holiday Table, Bone-Friendly Plate: Thanksgiving With Osteoporosis",
        title="Thanksgiving With Osteoporosis: A Bone-Friendly Plate",
        meta="One holiday meal won't make or break your bones. Easy calcium boosts, a vegetarian plate, salt, alcohol, coffee, and the real holiday risk: falls.",
        blurb="One holiday meal won't make or break your bones, so enjoy the turkey. Easy ways to add a little calcium, protein on a vegetarian plate, what to know about salt, alcohol, and coffee, and the real holiday risk to your bones, which isn't on the plate.",
        alt="A Thanksgiving table with roast turkey, mashed potatoes, green beans, Brussels sprouts, a cheese board, and pumpkin pie, as an older woman passes a bowl of roasted squash",
        about=["Osteoporosis", "Bone health", "Nutrition", "Calcium", "Fall prevention"],
        disclaimer="This blog post is for educational purposes only and isn't intended as medical advice. Always consult with your healthcare provider about the diet that's right for you, especially if you take medications that interact with alcohol.",
        related=["protein-and-calcium.html", "grocery-guide.html", "fall-proofing-whole-house.html"],
        inbound=[
            ("blog/bone-friendly-meals.html",
             "No single meal is going to transform your bone density.",
             '<p>The same goes for big holiday dinners. For easy ways to tilt a holiday meal in your bones\' favor, see <a href="holiday-table-bone-friendly-plate.html">holiday table, bone-friendly plate</a>.</p>'),
        ],
    ),
    dict(
        slug="osteoporosis-runs-in-families",
        hero_pos="18%",
        date="2026-11-24",
        section="Patient Education",
        h1="Osteoporosis Runs in Families: What to Tell Your Sister, Daughter, or Son",
        seo="Osteoporosis Runs in Families: What to Tell Your Sister, Daughter, or Son",
        title="Osteoporosis Runs in Families: What to Tell Relatives",
        meta="If you have osteoporosis, your relatives may be at higher risk too. What the research shows, who should get checked, and how to bring it up with family.",
        blurb="If you have osteoporosis, the people you share genes with may be at higher risk too. What the research shows, family clues that don't get called osteoporosis, who should get checked and when, and how to bring it up when everyone's together.",
        alt="Three generations of women, a grandmother, her daughter, and her granddaughter, smiling as they look through a family photo album at a holiday table with coffee and pie",
        about=["Osteoporosis", "Family history", "Bone density screening", "Genetics"],
        disclaimer="This blog post is for educational purposes only and isn't intended as medical advice. Always consult with your healthcare provider about whether and when bone density testing is right for you.",
        related=["frax-score-explained.html", "osteoporosis-in-men.html", "first-osteoporosis-visit.html"],
        inbound=[
            ("blog/first-osteoporosis-visit.html",
             "Genetics load the dice for both peak bone mass and rate of bone loss.",
             '<p>If osteoporosis runs in your family, your relatives may want to get checked too. I explain why, and how to bring it up, in <a href="osteoporosis-runs-in-families.html">osteoporosis runs in families</a>.</p>'),
        ],
    ),
]


def pretty(d):
    return datetime.strptime(d, "%Y-%m-%d").strftime("%B %-d, %Y")


def related_card(href):
    """Reuse the card's existing picture from blog/index.html so image names/widths are right."""
    idx = (REPO / "blog/index.html").read_text()
    m = re.search(r'<a href="' + re.escape(href) + r'" class="blog-card">(.*?)</a>', idx, re.S)
    if not m:
        raise SystemExit(f"related: no blog/index.html card for {href}")
    card = m.group(1)
    pic = re.search(r"<picture>.*?</picture>", card, re.S).group(0)
    pic = re.sub(r'sizes="[^"]*"', 'sizes="(max-width: 768px) 100vw, 320px"', pic)
    pic = pic.replace('fetchpriority="high"', 'loading="lazy"')
    if 'loading="lazy"' not in pic:
        pic = pic.replace("<img ", '<img loading="lazy" ', 1)
    tag = re.search(r'<span class="blog-card-tag">([^<]*)</span>', card).group(1)
    title = re.search(r"<h[23]>(.*?)</h[23]>", card, re.S).group(1).strip()
    return f'''            <a href="{href}" class="related-card">
                <div class="related-card-image">
                    {pic}
                </div>
                <div class="related-card-body">
                    <span class="related-card-tag">{tag}</span>
                    <h4 class="related-card-title">{title}</h4>
                </div>
            </a>'''


def build_page(p):
    s = TEMPLATE.read_text()
    slug = p["slug"]
    url = f"https://mybone.health/blog/{slug}.html"
    img = f"https://mybone.health/images/blog-{slug}.png"

    def sub1(pat, rep, flags=0):
        nonlocal s
        new, n = re.subn(pat, lambda m: rep, s, count=1, flags=flags)
        if n != 1:
            raise SystemExit(f"{slug}: pattern not found: {pat[:60]}")
        s = new

    sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{p["meta"]}">')
    sub1(r"<title>[^<]*</title>", f'<title>{p["title"]}</title>')

    # JSON-LD 1: load the template's, update article fields, keep author/publisher as-is
    m = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', s, re.S)
    ld = json.loads(m.group(2))
    ld.update({
        "@id": f"{url}#article", "headline": p["seo"], "description": p["meta"], "url": url,
        "datePublished": f'{p["date"]}T00:00:00Z', "dateModified": f'{p["date"]}T00:00:00Z',
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "articleSection": p["section"], "image": img, "about": p["about"],
        "lastReviewed": p["date"],
    })
    s = s[:m.start(2)] + "\n        " + json.dumps(ld, indent=6, ensure_ascii=False) + "\n    " + s[m.end(2):]

    bc = {
        "@context": "https://schema.org", "@type": "BreadcrumbList", "@id": f"{url}#breadcrumb",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://mybone.health/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://mybone.health/blog/"},
            {"@type": "ListItem", "position": 3, "name": p["seo"]},
        ],
    }
    sub1(r'(?<=<script type="application/ld\+json">)\s*\{\s*"@context":\s*"https://schema\.org",\s*"@type":\s*"BreadcrumbList".*?\}\s*(?=</script>)',
         "\n    " + json.dumps(bc, indent=6, ensure_ascii=False) + "\n    ", re.S)

    og = f'{p["seo"]} | mybone.health'
    sub1(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">')
    sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{og}">')
    sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{p["meta"]}">')
    sub1(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">')
    sub1(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{img}">')
    sub1(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{og}">')
    sub1(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{p["meta"]}">')
    sub1(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{img}">')

    pos = f' style="object-position: center {p["hero_pos"]}"' if p.get("hero_pos") else ""
    hero = (f'<picture><source type="image/webp" srcset="../images/blog-{slug}-400.webp 400w, '
            f'../images/blog-{slug}-800.webp 800w, ../images/blog-{slug}-1536.webp 1536w" sizes="100vw">'
            f'<img src="../images/blog-{slug}.png" alt="{p["alt"]}" width="1536" height="1024" '
            f'fetchpriority="high" decoding="async"{pos}></picture>')
    sub1(r'<picture><source type="image/webp" srcset="\.\./images/blog-' + T_SLUG + r'-400.*?</picture>', hero, re.S)
    sub1(r'<span class="post-tag">[^<]*</span>', f'<span class="post-tag">{p["section"]}</span>')
    sub1(r"<h1>" + re.escape(T_H1) + r"</h1>", f'<h1>{p["h1"]}</h1>')
    sub1(r'<p class="post-meta">[^<]*&middot; By Lisa Pocius, MD</p>',
         f'<p class="post-meta">{pretty(p["date"])} &middot; By Lisa Pocius, MD</p>')

    body = (BODIES / f"{slug}.html").read_text().strip()
    body = "\n".join(("        " + l) if l.strip() else "" for l in body.split("\n"))
    related = "\n".join(related_card(h) for h in p["related"])
    block = (body + '\n\n        <!-- Ask Lisa: reader question form -->\n\n        <!-- Related Posts -->\n'
             '        <aside class="related-posts" aria-label="Related posts">\n'
             '            <h2 class="related-heading">Keep reading</h2>\n'
             '            <div class="related-grid">\n' + related + '\n            </div>\n        </aside>')
    sub1(r'(?<=<article class="post-body">).*?(?=<div class="post-disclaimer">)', "\n" + block + "\n\n        ", re.S)
    sub1(r'(?<=<div class="post-disclaimer">)\s*[^<]*?\s*(?=</div>)', "\n            " + p["disclaimer"] + "\n        ", re.S)
    return s


def update_blog_index(p):
    path = REPO / "blog/index.html"
    s = path.read_text()
    slug = p["slug"]
    if f'href="{slug}.html" class="blog-card"' in s:
        print(f"  = blog/index.html already has {slug}")
        return False
    m = re.search(r'<a href="[^"]+" class="blog-card">', s)
    end = s.find("</a>", m.start()) + 4
    old = s[m.start():end].replace('fetchpriority="high"', 'loading="lazy"')
    card = f'''<a href="{slug}.html" class="blog-card">
                    <div class="blog-card-image">
                        <picture><source type="image/webp" srcset="../images/blog-{slug}-400.webp 400w, ../images/blog-{slug}-800.webp 800w, ../images/blog-{slug}-1536.webp 1536w" sizes="(max-width: 768px) 100vw, 380px"><img src="../images/blog-{slug}.png" alt="{p["alt"]}" width="1536" height="1024" fetchpriority="high" decoding="async"></picture>
                    </div>
                    <div class="blog-card-content">
                        <span class="blog-card-tag">{p["section"]}</span>
                        <div class="blog-card-date">{pretty(p["date"])}</div>
                        <h3>{p["h1"]}</h3>
                        <p>{p["blurb"]}</p>
                    </div>
                </a>'''
    path.write_text(s[:m.start()] + card + "\n                " + old + s[end:])
    print(f"  updated blog/index.html (+{slug})")
    return True


def update_homepage(p):
    path = REPO / "index.html"
    s = path.read_text()
    slug = p["slug"]
    if f'blog/{slug}.html' in s:
        print(f"  = index.html already has {slug}")
        return
    m = re.search(r'(<div class="blog-grid">)(.*?)(</div>\s*<div style="text-align: center;)', s, re.S)
    arts = re.findall(r'<article class="blog-card">.*?</article>', m.group(2), re.S)
    if len(arts) != 3:
        raise SystemExit(f"homepage: expected 3 cards, found {len(arts)}")
    card = f'''                <article class="blog-card">
                    <div class="blog-card-image">
                        <picture><source type="image/webp" srcset="images/blog-{slug}-400.webp 400w, images/blog-{slug}-800.webp 800w, images/blog-{slug}-1536.webp 1536w" sizes="(max-width: 768px) 100vw, 380px"><img src="images/blog-{slug}.png" alt="{p["alt"]}" width="1536" height="1024" loading="lazy" decoding="async"></picture>
                    </div>
                    <div class="blog-card-content">
                        <div class="blog-card-date">{pretty(p["date"])}</div>
                        <h3>{p["h1"]}</h3>
                        <p>{p["blurb"]}</p>
                        <a href="blog/{slug}.html">Read More &rarr;</a>
                    </div>
                </article>'''
    inner = "\n" + card + "\n                " + arts[0] + "\n                " + arts[1] + "\n                \n            "
    path.write_text(s[:m.start(2)] + inner + s[m.end(2):])
    print(f"  updated index.html (+{slug}, dropped oldest)")


def add_inbound(p):
    for f, marker, para in p["inbound"]:
        path = REPO / f
        s = path.read_text()
        if para in s:
            print(f"  = inbound already in {f}")
            continue
        i = s.find(marker)
        if i < 0:
            raise SystemExit(f"inbound marker not found in {f}: {marker[:50]}")
        end = s.find("</p>", i) + 4
        path.write_text(s[:end] + "\n\n        " + para + s[end:])
        print(f"  updated {f} (inbound link to {p['slug']})")


def normalize_listing_priority():
    """Top 3 cards on blog/index.html load eagerly (fetchpriority=high); the rest lazy."""
    path = REPO / "blog/index.html"
    s = path.read_text()
    out, last = [], 0
    for i, m in enumerate(re.finditer(r'<a href="[^"]+" class="blog-card">.*?</a>', s, re.S)):
        c = m.group(0)
        if i < 3:
            if "fetchpriority" not in c:
                c = c.replace('loading="lazy"', 'fetchpriority="high"')
        else:
            c = c.replace('fetchpriority="high"', 'loading="lazy"')
        out.append(s[last:m.start()] + c)
        last = m.end()
    out.append(s[last:])
    path.write_text("".join(out))


def main():
    want = sys.argv[1:]
    for p in POSTS:  # date order, so the newest ends up on top
        if want and p["slug"] not in want:
            continue
        print(f"[{p['slug']}]")
        (REPO / f"blog/{p['slug']}.html").write_text(build_page(p))
        # Homepage only changes when the post is new to the listing, so rebuilding
        # an older post never pushes it back onto the homepage.
        if update_blog_index(p):
            update_homepage(p)
        add_inbound(p)
    normalize_listing_priority()


if __name__ == "__main__":
    main()
