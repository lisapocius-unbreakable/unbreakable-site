#!/usr/bin/env python3
"""Style A site builder for mybone.health (approved November 2026).

What it does
  1. Re-renders every blog post in blog/*.html into the Style A article layout.
  2. Rebuilds the article library page (blog/index.html) with topic shelves,
     live counts, the newest articles and a search box.
  3. Refreshes the "article library" block on the homepage between the
     <!-- library:start --> and <!-- library:end --> markers.

It is safe to run again and again. Posts that are already in Style A are
re-read through the markers this script writes, so running it after adding a
new post simply updates counts, shelves and related links.

Adding a new post
  Put the new post in blog/ (old or new layout both work), add its slug to
  SHELF_OF below (or add <meta name="mbh-shelf" content="exercise"> in its
  <head>), then run:   python3 scripts/style_a.py

Nothing here deploys anything. Hostinger still needs a manual deploy.
"""
import html, json, math, re, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '    <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">')

# Topic shelves, in display order. "feelings" stays folded into "everyday"
# until it has at least FEELINGS_MIN posts, so the shelf never looks thin.
SHELVES = [
    ("diagnosis", "Diagnosis, tests and risk", "Your first steps, your first visit, what your scan numbers mean, and what raises your risk."),
    ("medicines", "Medicines and treatments", "Plain-language guides to the common treatments, and medicines that affect bone."),
    ("exercise", "Exercise and movement", "Safe ways to get stronger, steadier and more confident."),
    ("food", "Food, calcium and vitamin D", "Calcium, protein, vitamin D and simple meals."),
    ("everyday", "Falls, safety and everyday life", "Making your home and your days safer, and living well with a diagnosis."),
    ("feelings", "Feelings and coping", "The emotional side of osteoporosis: fear, identity, and the people around you."),
]
FEELINGS_MIN = 4
EVERYDAY_WITH_FEELINGS = "Making your home and your days safer, and the feelings that come with a diagnosis."
EVERYDAY_SPLIT_NAME = "Falls and home safety"

SHELF_OF = {
    # Diagnosis, tests and risk
    "first-30-days-osteoporosis": "diagnosis", "first-osteoporosis-visit": "diagnosis", "dexa-tbs-vfa": "diagnosis",
    "frax-score-explained": "diagnosis", "can-osteoporosis-be-reversed": "diagnosis", "osteoporosis-in-men": "diagnosis",
    "osteoporosis-runs-in-families": "diagnosis",
    # Medicines and treatments
    "osteoporosis-injections-compared": "medicines", "bisphosphonates-explained": "medicines", "bisphosphonate-tips": "medicines",
    "prolia-denosumab-explained": "medicines", "anabolic-medications": "medicines", "evenity-explained": "medicines",
    "medications-that-weaken-bone": "medicines", "glp1-and-bone-health": "medicines", "stem-cells-osteoporosis": "medicines",
    # Exercise and movement
    "squats-lifting-bending-osteoporosis": "exercise", "exercise-after-fracture": "exercise", "posture-and-osteoporosis": "exercise",
    "balance-training": "exercise", "weight-bearing-vs-resistance": "exercise",
    # Food, calcium and vitamin D
    "calcium-vit-d-study-2026": "food", "vitamin-d-and-sunshine": "food", "vitamin-d-bone-health": "food",
    "protein-and-fracture-recovery": "food", "protein-and-calcium": "food", "bone-friendly-meals": "food", "grocery-guide": "food",
    "holiday-table-bone-friendly-plate": "food",
    # Falls, safety and everyday life
    "holiday-chores-lifting-osteoporosis": "everyday", "fall-proofing-whole-house": "everyday",
    "fall-risk-medications": "everyday", "asking-ai-about-osteoporosis": "everyday",
    # Feelings and coping
    "identity-shift": "feelings", "emotional-side-new-osteoporosis-diagnosis": "feelings",
}

AUTHOR_BIO = ("I'm a physician who spent ten years in family practice. At 55, I fell in my front yard, "
              "fractured four vertebrae, and learned I had osteoporosis. Now I write plain-language guides "
              "to help people live well with it.")

FB_SVG = ('<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z"/></svg>')


def header(p, active=""):
    def link(key, href, label, cls=""):
        cur = ' aria-current="page"' if key == active else ""
        c = f' class="{cls}"' if cls else ""
        return f'<a href="{href}"{c}{cur}>{label}</a>'
    return f'''<a class="skip" href="#main">Skip to the main content</a>
<header class="top"><div class="wrap">
  <a class="logo" href="{p}index.html">mybone<span>.</span>health</a>
  <nav class="site-nav" aria-label="Main">
    {link("start", p + "index.html#start-here", "Start here")}{link("books", p + "books/", "Books")}{link("articles", p + "blog/", "Articles")}{link("about", p + "about.html", "About Lisa")}{link("cheat", p + "free/calcium-protein-cheat-sheet.html", "Free cheat sheet", "cta")}
  </nav>
</div></header>'''


def footer(p):
    return f'''<footer class="site-footer"><div class="wrap">
  <nav class="links" aria-label="Footer">
    <a href="{p}about.html">About Lisa</a><a href="{p}blog/">Articles</a><a href="{p}books/">Books</a><a href="{p}faq.html">FAQ</a><a href="{p}index.html#newsletter">Monthly letter</a><a href="mailto:lisa@mybone.health">Contact</a><a href="{p}privacy.html">Privacy</a><a href="{p}editorial-policy.html">Editorial policy</a><a href="{p}medical-disclaimer.html">Medical disclaimer</a>
  </nav>
  <div class="social"><a class="fb" href="https://www.facebook.com/mybonehealth/" target="_blank" rel="noopener noreferrer" aria-label="Follow on Facebook" title="Follow on Facebook">{FB_SVG}</a><a class="fb" href="https://www.instagram.com/mybone.health/" target="_blank" rel="noopener noreferrer" aria-label="Follow on Instagram" title="Follow on Instagram"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077"/></svg></a><a class="fb" href="https://www.youtube.com/@MyBoneHealth" target="_blank" rel="noopener noreferrer" aria-label="Watch on YouTube" title="Watch on YouTube"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg></a><a class="fb" href="https://www.tiktok.com/@mybonehealth" target="_blank" rel="noopener noreferrer" aria-label="Follow on TikTok" title="Follow on TikTok"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg></a></div>
  <p>&copy; {datetime.now().year} Lisa Pocius, MD. All rights reserved.</p>
  <p class="small">The information on this website is for educational purposes only and is not intended as medical advice. Always consult with a qualified healthcare provider before making decisions about your health.</p>
</div></footer>'''


def strip_styles(head):
    """Remove inline <style> blocks and old font links, then add the shared stylesheet."""
    head = re.sub(r"\s*<style\b.*?</style>", "", head, flags=re.S)
    head = re.sub(r'\s*<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"[^>]*>', "", head)
    head = re.sub(r'\s*<link href="https://fonts\.googleapis\.com/css2[^"]*" rel="stylesheet">', "", head)
    head = re.sub(r"\s*<!-- Fonts -->", "", head)
    head = re.sub(r'\s*<link rel="stylesheet" href="[./]*css/site\.css[^"]*">', "", head)
    head = head.replace("<!-- mbh-style-a -->", "")
    return re.sub(r"(\n[ \t]*){2,}", "\n", head).rstrip()


def add_css(head, p):
    tag = f'\n    <!-- mbh-style-a -->\n    {FONTS}\n    <link rel="stylesheet" href="{p}css/site.css?v=2">'
    return head.replace("</head>", tag + "\n</head>", 1) if "</head>" in head else head + tag + "\n"


def grab(pattern, text, default=""):
    m = re.search(pattern, text, flags=re.S)
    return m.group(1).strip() if m else default


def read_post(path):
    raw = path.read_text(encoding="utf-8")
    slug = path.stem
    head = raw[: raw.find("<body")]
    head = head[: head.rfind("</head>")] if "</head>" in head else head
    d = {"slug": slug, "head": head}
    d["title"] = html.unescape(re.sub(r"<[^>]+>", "", grab(r"<h1[^>]*>(.*?)</h1>", raw))).strip()
    d["page_title"] = html.unescape(grab(r"<title>(.*?)</title>", raw))
    d["desc"] = html.unescape(grab(r'<meta\s+name="description"\s+content="([^"]*)"', raw))
    d["date_text"] = grab(r'<p class="post-meta">\s*([A-Z][a-z]+ \d{1,2}, \d{4})', raw)
    try:
        d["date"] = datetime.strptime(d["date_text"], "%B %d, %Y")
    except ValueError:
        iso = grab(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', raw)
        d["date"] = datetime.strptime(iso, "%Y-%m-%d")
        d["date_text"] = d["date"].strftime("%B %-d, %Y")
    d["shelf_meta"] = grab(r'<meta name="mbh-shelf" content="([a-z]+)"', raw)
    d["picture"] = grab(r'<div class="(?:post-hero-image|hero-img)">\s*(<picture>.*?</picture>)', raw)
    if "<!-- mbh:body:start -->" in raw:
        body = raw.split("<!-- mbh:body:start -->", 1)[1].split("<!-- mbh:body:end -->", 1)[0]
    else:
        s = raw.find('<article class="post-body">') + len('<article class="post-body">')
        ends = [i for i in (raw.find("<!-- Ask Lisa", s), raw.find('<aside class="related-posts"', s),
                            raw.find("<!-- Related Posts -->", s), raw.find('<div class="post-disclaimer">', s)) if i > 0]
        body = raw[s:min(ends)]
    d["body"] = body.strip("\n")
    d["disclaimer"] = grab(r'<(?:div|p) class="post-disclaimer">(.*?)</(?:div|p)>', raw)
    rel = grab(r'<aside class="related-posts".*?>(.*?)</aside>', raw) or grab(r"<!-- mbh:related -->(.*?)<!-- /mbh:related -->", raw)
    d["related"] = [h[:-5] for h in re.findall(r'href="([a-z0-9-]+\.html)"', rel)]
    d["tail_scripts"] = ""
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    d["minutes"] = max(3, math.ceil(words / 230))
    d["has_book_cta"] = "book-cta" in body
    d["img800"] = ""
    for cand in re.findall(r"\.\./images/([\w.-]+-800\.webp)", d["picture"]) + re.findall(r"\.\./images/([\w.-]+-400\.webp)", d["picture"]):
        if (ROOT / "images" / cand).exists():
            d["img800"] = cand
            break
    return d


def shelf_key(post, feelings_live):
    k = post.get("shelf_meta") or SHELF_OF.get(post["slug"])
    if not k:
        sys.exit(f"No shelf for {post['slug']}. Add it to SHELF_OF in scripts/style_a.py.")
    if k == "feelings" and not feelings_live:
        return "everyday"
    return k


def shelf_list(feelings_live):
    out = []
    for key, name, blurb in SHELVES:
        if key == "feelings" and not feelings_live:
            continue
        if key == "everyday":
            if feelings_live:
                name = EVERYDAY_SPLIT_NAME
                blurb = "Making your home and your days safer."
            else:
                blurb = EVERYDAY_WITH_FEELINGS
        out.append((key, name, blurb))
    return out


def card(post, p, shelf_name, img_prefix):
    img = (f'<img src="{img_prefix}images/{post["img800"]}" alt="" width="800" height="533" loading="lazy" decoding="async">'
           if post["img800"] else '<div class="noimg" aria-hidden="true"></div>')
    return (f'<a class="post" href="{p}{post["slug"]}.html">{img}<div class="card-body">'
            f'<h3>{html.escape(post["title"])}</h3><p>{html.escape(shelf_name)}</p></div></a>')


def render_post(post, posts, shelves, feelings_live):
    names = {k: n for k, n, _ in shelves}
    key = shelf_key(post, feelings_live)
    sname = names[key]
    by_slug = {q["slug"]: q for q in posts}
    rel = [s for s in post["related"] if s in by_slug and s != post["slug"]]
    same = sorted((q for q in posts if shelf_key(q, feelings_live) == key and q["slug"] != post["slug"] and q["slug"] not in rel),
                  key=lambda q: q["date"], reverse=True)
    rel = (rel + [q["slug"] for q in same])[:3]
    if len(rel) < 3:
        rel += [q["slug"] for q in sorted(posts, key=lambda q: q["date"], reverse=True)
                if q["slug"] not in rel and q["slug"] != post["slug"]][: 3 - len(rel)]
    cards = "\n    ".join(card(by_slug[s], "", names[shelf_key(by_slug[s], feelings_live)], "../") for s in rel)

    hero = ""
    if post["picture"]:
        hero = f'<div class="hero-img">\n    {post["picture"]}\n</div>'

    callout = ""
    if not post["has_book_cta"]:
        if key == "exercise":
            callout = ('<div class="callout"><div class="box"><img src="../images/exercise-book-cover-400.webp" alt="Osteoporosis Exercises for Beginners book cover" width="400" height="600" loading="lazy">'
                       '<div><h2>Want a simple plan to get stronger at home?</h2><p>My book <em>Osteoporosis Exercises for Beginners</em> teaches more than 40 illustrated exercises and builds them into a 12-week home program with a chair, a wall and a counter.</p>'
                       '<a class="btn primary" href="../books/osteoporosis-exercises-for-beginners/">See the exercise book</a></div></div></div>')
        else:
            callout = ('<div class="callout main-book"><div class="box"><img src="../images/book-cover-400.webp" alt="Osteoporosis: The Book I Wish I\'d Had When I Was Diagnosed book cover" width="400" height="600" loading="lazy">'
                       '<div><h2>Everything in one place</h2><p>My book <em>Osteoporosis: The Book I Wish I\'d Had When I Was Diagnosed</em> puts what I\'ve learned into plain language, from your first scan to everyday life.</p>'
                       '<a class="btn primary" href="https://www.amazon.com/dp/B0GZ271ZWC" target="_blank" rel="noopener">See the book on Amazon</a></div></div></div>')

    disclaimer = post["disclaimer"] or "This article is for educational purposes only and isn't intended as medical advice. Talk with your own doctor about your situation."
    total = len(posts)
    head = add_css(strip_styles(post["head"]), "../")
    if 'name="mbh-shelf"' not in head:
        head += f'\n    <meta name="mbh-shelf" content="{post.get("shelf_meta") or SHELF_OF.get(post["slug"])}">'
    return f'''{head.rstrip()}
</head>
<body>
{header("../", "articles")}
<main id="main">
<div class="crumbs"><a href="./">Article library</a> &rsaquo; <a href="./#{key}">{sname}</a></div>
<div class="post-head">
  <a class="post-tag-link" href="./#{key}"><span class="post-tag">{sname}</span></a>
  <h1>{html.escape(post["title"])}</h1>
  <div class="byline"><img src="../images/author-headshot-400.webp" alt="" width="56" height="56"><div><strong>Lisa Pocius, MD</strong><p class="post-meta">{post["date_text"]} &middot; About {"an" if str(post["minutes"]).startswith("8") or str(post["minutes"]) in ("11","18") else "a"} {post["minutes"]}-minute read</p></div></div>
</div>
{hero}
<article class="post-body">
<!-- mbh:body:start -->
{post["body"]}
<!-- mbh:body:end -->
</article>
{callout}
<div class="author"><div class="box"><img src="../images/author-headshot-400.webp" alt="Lisa Pocius, MD" width="84" height="84" loading="lazy"><div><strong>About Lisa Pocius, MD</strong><p>{AUTHOR_BIO} <a href="../about.html">Read my story</a></p></div></div></div>
<p class="post-disclaimer">{disclaimer.strip()}</p>
<section class="band more-shelf" aria-label="More from the article library"><div class="wrap">
  <h2>More from the library</h2>
  <p class="section-sub">Related articles you might find helpful.</p>
  <!-- mbh:related -->
  <div class="posts">
    {cards}
  </div>
  <!-- /mbh:related -->
  <div class="back"><a class="btn primary" href="./">Browse all {total} articles</a><a class="btn secondary" href="./#{key}">More on {sname[0].lower() + sname[1:]}</a></div>
</div></section>
<section><div class="wrap">
  <div class="letter">
    <div><h2>A short letter, once a month</h2><p>One useful bone health email a month, plus my free Calcium and Protein Cheat Sheet.</p></div>
    <div><a class="btn" href="../index.html#newsletter">Sign up for the monthly letter</a></div>
  </div>
</div></section>
</main>
{footer("../")}
</body>
</html>
'''


def month(d):
    return d.strftime("%B %Y")


def render_library(posts, shelves, feelings_live):
    raw = (BLOG / "index.html").read_text(encoding="utf-8")
    head = raw[: raw.find("<body")]
    head = head[: head.rfind("</head>")]
    head = add_css(strip_styles(head), "../")
    names = {k: n for k, n, _ in shelves}
    newest = sorted(posts, key=lambda q: q["date"], reverse=True)
    groups = {k: [] for k, _, _ in shelves}
    for q in newest:
        groups[shelf_key(q, feelings_live)].append(q)
    topics = "".join(f'<a class="topic" href="#{k}">{n}<span>{len(groups[k])} article{"s" if len(groups[k]) != 1 else ""}</span></a>' for k, n, _ in shelves)
    cards = "\n    ".join(card(q, "", names[shelf_key(q, feelings_live)], "../") for q in newest[:3])
    shelf_html = ""
    for k, n, blurb in shelves:
        items = "".join(f'<li><a href="{q["slug"]}.html">{html.escape(q["title"])}</a><p>{html.escape(q["desc"])}</p><div class="when">{month(q["date"])}</div></li>' for q in groups[k])
        shelf_html += f'<section class="shelf" id="{k}"><div class="wrap"><h2>{n}</h2><p>{blurb}</p><ul class="list">{items}</ul><a class="top-link" href="#main">Back to all topics &uarr;</a></div></section>\n'
    return f'''{head.rstrip()}
</head>
<body>
{header("../", "articles")}
<main id="main">
<div class="page-head"><div class="wrap">
  <span class="count">{len(posts)} articles and growing</span>
  <h1>The article library</h1>
  <p>Every article I've written, sorted by topic. New articles come out twice a month.</p>
  <div class="search"><label for="q">Search the library</label><input id="q" type="search" placeholder="Try: Prolia, vitamin D, squats" autocomplete="off"></div>
  <p class="empty" id="empty" role="status">No articles match that yet. Try a shorter word.</p>
  <div class="topics">{topics}</div>
</div></div>
<section class="new-row"><div class="wrap">
  <h2>Newest articles</h2>
  <div class="posts">
    {cards}
  </div>
</div></section>
{shelf_html}</main>
{footer("../")}
<script>
(function(){{var q=document.getElementById('q');q.addEventListener('input',function(){{var v=q.value.trim().toLowerCase(),n=0;document.querySelectorAll('.list li').forEach(function(li){{var m=!v||li.textContent.toLowerCase().indexOf(v)>-1;li.style.display=m?'':'none';if(m)n++}});document.querySelectorAll('.shelf').forEach(function(s){{s.style.display=[].some.call(s.querySelectorAll('li'),function(li){{return li.style.display!=='none'}})?'':'none'}});document.querySelector('.new-row').style.display=v?'none':'';document.getElementById('empty').style.display=n?'none':'block'}})}})();
</script>
</body>
</html>
'''


def render_home_block(posts, shelves, feelings_live):
    names = {k: n for k, n, _ in shelves}
    newest = sorted(posts, key=lambda q: q["date"], reverse=True)
    counts = {k: 0 for k, _, _ in shelves}
    for q in posts:
        counts[shelf_key(q, feelings_live)] += 1
    pills = "".join(f'<a href="blog/#{k}">{n} <span>{counts[k]}</span></a>' for k, n, _ in shelves)
    cards = "\n      ".join(card(q, "blog/", names[shelf_key(q, feelings_live)], "") for q in newest[:3])
    return f'''<!-- library:start -->
<section id="blog"><div class="wrap">
  <h2 class="section-title">The article library</h2>
  <p class="section-sub">{len(posts)} plain-language articles so far, with new ones twice a month.</p>
  <div class="libtopics">{pills}</div>
  <h3 class="newest">Newest articles</h3>
  <div class="posts">
      {cards}
  </div>
  <div class="center"><a class="btn primary" href="blog/">Browse all {len(posts)} articles</a></div>
</div></section>
<!-- library:end -->'''


def main():
    paths = sorted(p for p in BLOG.glob("*.html") if p.name != "index.html" and not p.name.startswith("draft-"))
    posts = [read_post(p) for p in paths]
    feelings = sum(1 for q in posts if (q.get("shelf_meta") or SHELF_OF.get(q["slug"])) == "feelings")
    feelings_live = feelings >= FEELINGS_MIN
    shelves = shelf_list(feelings_live)
    for q, path in zip(posts, paths):
        path.write_text(render_post(q, posts, shelves, feelings_live), encoding="utf-8")
    (BLOG / "index.html").write_text(render_library(posts, shelves, feelings_live), encoding="utf-8")
    home = ROOT / "index.html"
    h = home.read_text(encoding="utf-8")
    if "<!-- library:start -->" in h:
        h = re.sub(r"<!-- library:start -->.*?<!-- library:end -->", lambda m: render_home_block(posts, shelves, feelings_live), h, flags=re.S)
        home.write_text(h, encoding="utf-8")
    print(f"{len(posts)} posts restyled. Feelings and coping shelf: {'on' if feelings_live else f'waiting ({feelings}/{FEELINGS_MIN} posts)'}.")


if __name__ == "__main__":
    main()
