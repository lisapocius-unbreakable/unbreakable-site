#!/usr/bin/env python3
"""Build the October 2026 posts by cloning blog/protein-and-fracture-recovery.html
and swapping only the article-specific parts, so shared furniture stays
byte-identical (per docs/PUBLISHING-CHECKLIST.md).

Article bodies live in /home/user/workspace/posts/<slug>.html.

Usage:
  python3 scripts/build_october_posts.py            # build all four, in date order
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

POSTS = [
    dict(
        slug="squats-lifting-bending-osteoporosis",
        date="2026-10-13",
        section="Exercise",
        hero_pos="12%",
        h1="Can I Do Squats With Osteoporosis? Lifting, Bending, and Twisting Safely",
        seo="Can I Do Squats With Osteoporosis? Lifting, Bending, and Twisting Safely",
        title="Can I Do Squats With Osteoporosis? A Physician's Answer",
        meta="Squats, lifting, and gardening are usually safe with osteoporosis. The one movement to avoid, how to do a hip hinge, and when to see a physical therapist.",
        blurb="Most people with osteoporosis can squat, lift, and garden. What matters is how your spine is positioned. The one movement that deserves respect, how to learn a hip hinge, and what the research shows about lifting.",
        alt="A woman in her sixties with silver hair doing a controlled chair squat in a bright living room, hips pushed back toward a wooden chair with her back long and arms reaching forward",
        about=["Osteoporosis", "Bone health", "Exercise", "Safe movement"],
        disclaimer="This blog post is for educational purposes only and isn't intended as medical advice. Always consult with your healthcare provider or a physical therapist about the exercise plan that's right for you.",
        related=["exercise-after-fracture.html", "weight-bearing-vs-resistance.html", "posture-and-osteoporosis.html"],
        inbound=[
            ("blog/exercise-after-fracture.html",
             "Exercise after a fracture is not the same as exercise before one.",
             '<p>If you haven\'t had a fracture and you\'re wondering what\'s safe in everyday life, from squats to gardening to picking up a grandchild, see <a href="squats-lifting-bending-osteoporosis.html">can I do squats with osteoporosis?</a></p>'),
        ],
    ),
    dict(
        slug="medications-that-weaken-bone",
        date="2026-10-20",
        section="Medication",
        h1="Medications That Can Quietly Weaken Your Bones",
        seo="Medications That Can Quietly Weaken Your Bones",
        title="Medications That Can Quietly Weaken Your Bones",
        meta="Steroids, some cancer drugs, acid reflux pills, and too much thyroid hormone can weaken bone. What the evidence shows, and why not to stop on your own.",
        blurb="Some of the most common causes of bone loss come from the pharmacy. Steroids, hormone-blocking cancer drugs, acid reflux pills, and too much thyroid hormone, what the evidence shows, and the questions to bring to your doctor.",
        alt="Amber prescription bottles and a weekly pill organizer on a kitchen counter beside a handwritten medication list and reading glasses",
        about=["Osteoporosis", "Bone health", "Medication side effects", "Secondary osteoporosis"],
        disclaimer="This blog post is for educational purposes only and isn't intended as medical advice. Don't stop or change any medication without talking with your healthcare provider.",
        related=["fall-risk-medications.html", "first-osteoporosis-visit.html", "frax-score-explained.html"],
        inbound=[
            ("blog/first-osteoporosis-visit.html",
             "Can we go through these and talk about which might be affecting my bones?",
             '<p>I go through the most common bone-thieving medications, and what the evidence shows for each, in <a href="medications-that-weaken-bone.html">medications that can quietly weaken your bones</a>.</p>'),
            ("blog/fall-risk-medications.html",
             "Sometimes a small dose adjustment, a switch to a different drug in the same class",
             '<p>Some medications raise fracture risk a different way, by weakening the bone itself. That\'s a separate list, and I cover it in <a href="medications-that-weaken-bone.html">medications that can quietly weaken your bones</a>.</p>'),
        ],
    ),
    dict(
        slug="osteoporosis-in-men",
        hero_pos="22%",
        date="2026-10-27",
        section="Patient Education",
        h1="Men Get Osteoporosis Too: What Every Man Over 50 Should Know",
        seo="Men Get Osteoporosis Too: What Every Man Over 50 Should Know",
        title="Osteoporosis in Men: What Men Over 50 Should Know",
        meta="About one in five men over 50 will break a bone from osteoporosis, yet few are tested. Risk factors, when men should be screened, and treatments for men.",
        blurb="About one in five men over 50 will break a bone from osteoporosis, and men do worse than women after a hip fracture. Why men get missed, the risk factors to watch for, when to get tested, and the treatments approved for men.",
        alt="A smiling man in his late sixties in a navy sweater walking briskly with light hand weights on a leafy autumn path, with his wife walking behind him",
        about=["Osteoporosis", "Osteoporosis in men", "Bone density screening", "Fracture prevention"],
        disclaimer="This blog post is for educational purposes only and isn't intended as medical advice. Always consult with your healthcare provider about your specific testing and treatment options.",
        related=["medications-that-weaken-bone.html", "frax-score-explained.html", "osteoporosis-injections-compared.html"],
        inbound=[],
    ),
    dict(
        slug="first-30-days-osteoporosis",
        date="2026-11-03",
        section="Patient Education",
        h1="Just Diagnosed? Your First 30 Days With Osteoporosis",
        seo="Just Diagnosed? Your First 30 Days With Osteoporosis",
        title="Diagnosed With Osteoporosis? Your First 30 Days",
        meta="Just diagnosed with osteoporosis? A week-by-week plan for your first month: get your numbers, make your home safer, prepare for your visit, build your team.",
        blurb="A new osteoporosis diagnosis can bring a flood of information with no sense of order. A week-by-week plan for your first month, from getting your DEXA numbers to fall-proofing your home, plus what changes if you got here through a fracture.",
        alt="A woman in her fifties writing in an open notebook at a wooden kitchen table, with a blue folder, a cup of tea, reading glasses, and a weekly pill organizer nearby",
        about=["Osteoporosis", "Newly diagnosed", "Self-advocacy", "Fall prevention"],
        disclaimer="This blog post is for educational purposes only and isn't intended as medical advice. Always consult with your healthcare provider about your specific treatment plan.",
        related=["first-osteoporosis-visit.html", "identity-shift.html", "fall-proofing-whole-house.html"],
        inbound=[
            ("blog/first-osteoporosis-visit.html",
             "If you walked out without these, it isn't too late.",
             '<p>If you\'re still in the first weeks after your diagnosis, my <a href="first-30-days-osteoporosis.html">week-by-week plan for your first 30 days</a> puts this visit in context with everything else you can do that month.</p>'),
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
