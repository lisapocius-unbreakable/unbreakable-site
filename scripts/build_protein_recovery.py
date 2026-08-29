#!/usr/bin/env python3
"""Build blog/protein-and-fracture-recovery.html by cloning the Prolia post
and swapping only the article-specific parts.

Per publishing checklist: "assemble them with a script so the shared furniture
stays byte-identical."

Outputs:
  blog/protein-and-fracture-recovery.html
  blog/index.html                  (with new card at top)
  index.html                       (with new card at top, oldest of 3 dropped)

Does NOT touch:
  sitemap.xml, feed.xml, atom.xml (GitHub Action regenerates on push)
"""
import pathlib, re, sys, json

REPO = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "blog/prolia-denosumab-explained.html"

SLUG = "protein-and-fracture-recovery"
HEADLINE_H1 = "Protein After a Fracture: What Your Recovery Actually Needs"
HEADLINE_SEO = "Protein After a Fracture: What Recovery Actually Needs"  # for JSON-LD + og:title, no |mybone suffix
TITLE_TAG = "Protein After a Fracture: What Recovery Needs"  # under 60 chars, no |mybone
META_DESC = "Protein demand goes up after a fracture and appetite often drops. What the evidence says, why plant and animal protein both work, and easy food ideas."  # 156 chars
DATE_PUBLISHED = "2026-08-29"
DATE_MODIFIED = "2026-08-29"
LAST_REVIEWED = "2026-08-29"
SECTION = "Nutrition"
CARD_BLURB = "Right after a fracture, protein needs go up and appetite usually drops. A physician who lives with osteoporosis walks through what the evidence says, why plant and animal protein both work, and easy food ideas for when you're not up to cooking."  # ~265 chars, matches neighbours
HERO_ALT = "Overhead flat lay of bone-friendly protein foods including Greek yogurt with raspberries and almonds, grilled salmon, aged parmesan, white beans, eggs, sliced roasted chicken, and a protein smoothie on a cream linen tablecloth"

# ============================================================================
# ARTICLE BODY (HTML). Converted from the approved markdown draft.
# Uses site conventions: no em dashes, <a href="...html"> for internal links,
# <a href="https://..."> for external.
# ============================================================================
ARTICLE_BODY = '''<p>If you've just fractured, or you love someone who has, this post is about the part of recovery that gets almost no attention: what you eat.</p>

<p>The bracing, the physical therapy, the follow-up appointments, the medication conversations, all of that gets covered. Protein rarely comes up until someone in the hospital hands you a printed sheet on the way out the door, and by then you're exhausted and your appetite is gone and the sheet ends up on the counter under the mail.</p>

<p>I want to make the case for putting it back on top of the pile.</p>

<h2>Why Protein Matters More After a Fracture, Not Less</h2>

<p>A healing bone is a construction site. Your body is laying down new collagen (the protein scaffolding that holds bone together), rebuilding the fractured edges, and replacing the muscle you lost sitting still. All of that work runs on protein.</p>

<p>The trouble is that recovery collides with two things that push protein in the wrong direction. Your appetite drops after surgery, after real pain, and after the disruption a fracture forces on your whole routine. And the standard hospital or rehab meal often doesn't supply enough protein for an older adult even when it's eaten completely.</p>

<p>The International Osteoporosis Foundation puts it plainly: getting enough protein matters especially for older adults with osteoporosis and for anyone recovering from an injury (<a href="https://www.osteoporosis.foundation/health-professionals/prevention/nutrition/protein-and-other-nutrients">International Osteoporosis Foundation</a>). Under-eating protein in the weeks after a fracture is one of the things you can actually change that predicts a slower, harder recovery.</p>

<h2>What the Evidence Actually Shows</h2>

<p>The clearest research comes from hip fracture, because that's where the studies were done. In older patients recovering from a hip fracture, fixing poor protein intake improves recovery and shortens hospital stays (<a href="https://www.osteoporosis.foundation/health-professionals/prevention/nutrition/protein-and-other-nutrients">International Osteoporosis Foundation, citing Rizzoli 2014</a>). That's not a small finding. Hospital days after a hip fracture are the days when people lose independence they never get back, when pneumonia gets a foothold, when the fall behind the fall happens.</p>

<p>For spine compression fractures, I'll be straight with you: almost none of the recovery research has been done on us. Compression fractures rarely get surgery, rarely get standardized follow-up, and haven't been the focus of nutrition trials. What we have instead is a biology argument, not a study argument. The bone that has to knit back together is about a third protein by weight. The back muscles that hold a healed spine upright, and the deep belly muscles that support them, are entirely protein. You can't ask your body to rebuild without giving it the raw materials. I say this so you know what kind of evidence you're working from.</p>

<p>There's also a quieter benefit. In the weeks after a fracture, most people move much less than usual. Muscle drops fast when you don't use it, and it drops faster when you're not eating enough protein. Losing muscle during recovery is what turns a short-term weakness into a lasting one. The post on <a href="exercise-after-fracture.html">exercise after a fracture</a> walks through the movement side. Protein is the food half of the same project.</p>

<h2>Animal or Plant Protein?</h2>

<p>This question comes up almost every time protein comes up, and the answer from the biggest expert group in the field is unusually clean: a balanced diet with enough protein is good for your bones whether the protein comes from animal or plant foods, as long as you're also getting enough calcium (<a href="https://www.osteoporosis.foundation/health-professionals/prevention/nutrition/protein-and-other-nutrients">International Osteoporosis Foundation</a>). Higher intakes from either source don't appear to harm bone.</p>

<p>The practical piece: a plant-based eater usually needs a bit more total protein to get the same building blocks (called amino acids) that meat eaters get more easily. Combining plant foods across a day, like beans with rice or tofu with grains, closes the gap. Beans, lentils, tofu, tempeh, edamame, nuts, seeds, and whole grains all count. During recovery, when appetite is smaller, a plant-based eater may lean more on a plant protein powder, for the same reason: it's a lot of nutrition in something you can actually get down.</p>

<h2>How Much, and Why Now Isn't the Time to Guess</h2>

<p>For the daily numbers and how to hit them across normal meals, the post on <a href="protein-and-calcium.html">protein and calcium for bone health</a> covers the ground. The short version: adults over 65 usually need more protein than the old official target, closer to about a half gram per pound of body weight per day, spread across meals.</p>

<p>Recovery is a reason to sit at the higher end of that range for the weeks around the fracture. It isn't a reason to overhaul your diet. Doubling your protein overnight when your appetite has already cratered usually just means smaller meals and less food overall, not more.</p>

<p>Two exceptions matter.</p>

<p>If you have significant kidney disease, your protein number belongs to your kidney doctor. This isn't a call to make on your own after a fracture.</p>

<p>If you're staying in a rehab or nursing facility, ask specifically whether the meal plan gives you enough protein per meal, and ask for the actual number. Menus vary a lot, and a polite request often produces a better tray.</p>

<h2>Eating Protein When You Don't Feel Like Eating</h2>

<p>This is the part the pamphlets skip. You're in a brace, or on crutches, or newly careful about how you move. Standing at a stove isn't the answer for a while, and neither is a heroic meal-prep session. What works is a small kit of easy, high-protein items that live within reach.</p>

<p><strong>Cold options that need almost no work:</strong></p>

<ul>
<li>Plain Greek yogurt, unsweetened, with a spoon of jam or a handful of berries. About 17 grams per single-serve container.</li>
<li>Cottage cheese with sliced fruit or a shake of pepper. About 14 grams per half cup.</li>
<li>A hard-boiled egg, from a batch someone made you at the start of the week. About 6 grams each. Two, and you've got a small meal.</li>
<li>Sliced cheese and whole grain crackers. Not glamorous. It counts.</li>
</ul>

<p><strong>Warm options that need a microwave and nothing else:</strong></p>

<ul>
<li>Canned salmon or tuna stirred into a pouch of microwave rice. About 25 grams from the fish, more from the rice.</li>
<li>Bean and cheese burrito made from a can of refried beans, a tortilla, and shredded cheese, warmed for a minute.</li>
<li>Instant oatmeal made with milk instead of water, with a spoon of peanut butter on top.</li>
</ul>

<p><strong>When appetite is the enemy:</strong></p>

<p>A protein shake, or a scoop of whey or plant-based protein powder stirred into yogurt, oatmeal, or a smoothie, is a real bridge, not a failure. Twenty grams of protein you actually drink beats sixty grams of chicken you can't face. This is the season to use the tool.</p>

<p>Sip your way through the day if a full meal feels like a mountain. Your body handles protein one meal at a time, so three modest hits usually beat one big one and two small ones.</p>

<h2>The People Around You</h2>

<p>If someone else is doing your grocery run, this is the list to give them. If someone is bringing meals, tell them what you need. "Something with protein I don't have to prep" is a specific ask, and most people are grateful to have one. A friend who was going to bring a casserole often does better bringing a rotisserie chicken, a tub of hummus, or a stack of yogurt cups.</p>

<p>You're allowed to name what would help.</p>

<h2>The Short Version</h2>

<ul>
<li>Recovery raises your protein needs and often drops your appetite at the same time. That gap is the risk.</li>
<li>The evidence is clearest for hip fracture, where fixing low protein intake improves recovery and shortens hospital stays. The same biology applies to spine fractures, even though we don't have direct studies there.</li>
<li>Sit at the higher end of the usual over-65 range for the weeks around the fracture, spread across meals.</li>
<li>Animal and plant protein both work when you're getting enough calcium. Plant eaters usually need a bit more total and should combine sources across the day.</li>
<li>Aim for a protein food at every meal, even when the meal is small.</li>
<li>Easy options belong in the house before you need them: yogurt, cottage cheese, eggs, canned fish, protein powder.</li>
<li>If your kidneys are involved, that number comes from your kidney doctor.</li>
<li>Tell the people around you what you need. "Protein I don't have to prep" is a good sentence.</li>
</ul>

<p>Bones heal slowly. Muscles rebuild slowly. Both of them reward the person who feeds them, most days, even in small ways, through the whole recovery, not just the first week.</p>'''


# ============================================================================
# RELATED POSTS (3, at the foot of the article)
# Pick posts that make natural sense as continuation for this reader:
#   1. protein-and-calcium.html (daily protein basics)
#   2. exercise-after-fracture.html (the movement half of recovery)
#   3. bone-friendly-meals.html (menu ideas)
# ============================================================================
RELATED = [
    {
        "href": "protein-and-calcium.html",
        "tag": "Nutrition",
        "title": "Protein, Calcium, and the Mistake of Picking One: What Your Bones Actually Need at Once",
        "img_slug": "protein",
        "img_ext": "png",
        "img_w": 1536, "img_h": 1024,
        "img_alt": "Overhead view of bone-supportive foods including salmon, Greek yogurt, milk, egg, kale and white beans, and aged cheese",
        "widths": [400, 800, 1536],
    },
    {
        "href": "exercise-after-fracture.html",
        "tag": "Exercise",
        "title": "Exercise After a Fracture: How to Modify Safely",
        "img_slug": "exercise-after-fracture",
        "img_ext": "png",
        "img_w": 1536, "img_h": 1024,
        "img_alt": "A woman in her sixties performing a modified wall-supported squat in a bright gym with a physical therapist standing nearby for form guidance",
        "widths": [400, 800, 1536],
    },
    {
        "href": "bone-friendly-meals.html",
        "tag": "Nutrition",
        "title": "5 Bone-Friendly Meals You Can Make in 20 Minutes",
        "img_slug": "bone-friendly-meals",
        "img_ext": "png",
        "img_w": 1536, "img_h": 1024,
        "img_alt": "Overhead view of a bone-friendly meal with salmon, greens, and beans",
        "widths": [400, 800, 1536],
    },
]


def build_related_html():
    parts = []
    for r in RELATED:
        srcset = ", ".join(
            f"../images/blog-{r['img_slug']}-{w}.webp {w}w" for w in r['widths']
        )
        parts.append(f'''            <a href="{r['href']}" class="related-card">
                <div class="related-card-image">
                    <picture><source type="image/webp" srcset="{srcset}" sizes="(max-width: 768px) 100vw, 320px"><img src="../images/blog-{r['img_slug']}.{r['img_ext']}" alt="{r['img_alt']}" width="{r['img_w']}" height="{r['img_h']}" loading="lazy" decoding="async"></picture>
                </div>
                <div class="related-card-body">
                    <span class="related-card-tag">{r['tag']}</span>
                    <h4 class="related-card-title">{r['title']}</h4>
                </div>
            </a>''')
    return "\n".join(parts)


def build_post_page():
    """Clone the Prolia post; swap only article-specific parts. Shared furniture untouched."""
    src = TEMPLATE.read_text()

    # 1. <meta name="description">
    src = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{META_DESC}">',
        src, count=1
    )

    # 2. <title>
    src = re.sub(r'<title>[^<]*</title>', f'<title>{TITLE_TAG}</title>', src, count=1)

    # 3. First JSON-LD block: BlogPosting/MedicalWebPage. Rebuild from scratch to control fields.
    author_person = {
        "@type": "Person",
        "@id": "https://mybone.health/#lisa-pocius",
        "name": "Lisa Pocius, MD",
        "givenName": "Lisa",
        "familyName": "Pocius",
        "honorificSuffix": "MD",
        "description": "Lisa Pocius, MD is a physician-author and former family physician who lives with osteoporosis. After her own diagnosis with low bone density and vertebral compression fractures, she set out to write the patient guide she wishes she'd had on day one. She writes about bone health at mybone.health and is the author of \"Osteoporosis: The Book I Wish I'd Had When I Was Diagnosed\" (2026).",
        "url": "https://mybone.health/",
        "image": "https://mybone.health/images/author-headshot.jpg?v=2",
        "sameAs": [
            "https://www.goodreads.com/author/show/70033876.Lisa_Pocius_MD",
            "https://www.amazon.com/stores/Lisa-Pocius-MD/author/B0H35GD38J",
            "https://www.facebook.com/mybonehealth/"
        ],
        "knowsAbout": [
            "Osteoporosis", "Bone health", "Bisphosphonates",
            "Fracture prevention", "Bone density", "Patient education"
        ]
    }
    blogposting = {
        "@context": "https://schema.org",
        "@type": ["BlogPosting", "MedicalWebPage"],
        "@id": f"https://mybone.health/blog/{SLUG}.html#article",
        "headline": HEADLINE_SEO,
        "description": META_DESC,
        "url": f"https://mybone.health/blog/{SLUG}.html",
        "datePublished": f"{DATE_PUBLISHED}T00:00:00Z",
        "dateModified": f"{DATE_MODIFIED}T00:00:00Z",
        "inLanguage": "en",
        "isPartOf": {"@id": "https://mybone.health/blog/#blog"},
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://mybone.health/blog/{SLUG}.html"
        },
        "articleSection": SECTION,
        "image": f"https://mybone.health/images/blog-{SLUG}.png",
        "author": author_person,
        "publisher": author_person,
        "about": ["Osteoporosis", "Bone health", "Nutrition", "Fracture recovery"],
        "mentions": {"@id": "https://mybone.health/#book"},
        "lastReviewed": LAST_REVIEWED,
        "reviewedBy": {"@id": "https://mybone.health/#lisa-pocius"}
    }
    jsonld_str = json.dumps(blogposting, indent=6, ensure_ascii=False)
    # Match the first application/ld+json script and replace its content
    # The template has extra leading whitespace inside <script>; mimic loosely.
    src = re.sub(
        r'(<script type="application/ld\+json">)\s*\{.*?"reviewedBy":\s*\{[^}]*\}\s*\}\s*(</script>)',
        lambda m: m.group(1) + "\n        " + jsonld_str + "\n    " + m.group(2),
        src, count=1, flags=re.S
    )

    # 4. Second JSON-LD: BreadcrumbList
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "@id": f"https://mybone.health/blog/{SLUG}.html#breadcrumb",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://mybone.health/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://mybone.health/blog/"},
            {"@type": "ListItem", "position": 3, "name": HEADLINE_SEO}
        ]
    }
    bc_str = json.dumps(breadcrumb, indent=6, ensure_ascii=False)
    src = re.sub(
        r'(<script type="application/ld\+json">)\s*\{\s*"@context":\s*"https://schema\.org",\s*"@type":\s*"BreadcrumbList".*?\}\s*(</script>)',
        lambda m: m.group(1) + "\n    " + bc_str + "\n    " + m.group(2),
        src, count=1, flags=re.S
    )

    # 5. canonical
    src = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="https://mybone.health/blog/{SLUG}.html">',
        src, count=1
    )

    # 6. og:title, og:description, og:url, og:image
    og_title = f"{HEADLINE_SEO} | mybone.health"
    src = re.sub(r'<meta property="og:title" content="[^"]*">',
                 f'<meta property="og:title" content="{og_title}">', src, count=1)
    src = re.sub(r'<meta property="og:description" content="[^"]*">',
                 f'<meta property="og:description" content="{META_DESC}">', src, count=1)
    src = re.sub(r'<meta property="og:url" content="[^"]*">',
                 f'<meta property="og:url" content="https://mybone.health/blog/{SLUG}.html">', src, count=1)
    src = re.sub(r'<meta property="og:image" content="[^"]*">',
                 f'<meta property="og:image" content="https://mybone.health/images/blog-{SLUG}.png">', src, count=1)

    # 7. twitter:title, twitter:description, twitter:image
    src = re.sub(r'<meta name="twitter:title" content="[^"]*">',
                 f'<meta name="twitter:title" content="{og_title}">', src, count=1)
    src = re.sub(r'<meta name="twitter:description" content="[^"]*">',
                 f'<meta name="twitter:description" content="{META_DESC}">', src, count=1)
    src = re.sub(r'<meta name="twitter:image" content="[^"]*">',
                 f'<meta name="twitter:image" content="https://mybone.health/images/blog-{SLUG}.png">', src, count=1)

    # 8. Hero picture
    new_hero = (
        f'<picture><source type="image/webp" srcset="'
        f'../images/blog-{SLUG}-400.webp 400w, '
        f'../images/blog-{SLUG}-800.webp 800w, '
        f'../images/blog-{SLUG}-1536.webp 1536w" sizes="100vw">'
        f'<img src="../images/blog-{SLUG}.png" alt="{HERO_ALT}" '
        f'width="1536" height="1024" fetchpriority="high" decoding="async"></picture>'
    )
    src = re.sub(
        r'<picture><source type="image/webp" srcset="\.\./images/blog-prolia-denosumab-explained-.*?</picture>',
        new_hero, src, count=1
    )

    # 9. Post tag (Medication -> Nutrition), h1, post-meta date
    src = re.sub(r'<span class="post-tag">Medication</span>',
                 f'<span class="post-tag">{SECTION}</span>', src, count=1)
    src = re.sub(
        r'<h1>Prolia \(Denosumab\): What It Does Well, and Why You Cannot Simply Stop</h1>',
        f'<h1>{HEADLINE_H1}</h1>', src, count=1
    )
    # Format the date like "August 29, 2026"
    from datetime import datetime
    date_pretty = datetime.strptime(DATE_PUBLISHED, "%Y-%m-%d").strftime("%B %-d, %Y")
    src = re.sub(
        r'<p class="post-meta">July 30, 2026 &middot; By Lisa Pocius, MD</p>',
        f'<p class="post-meta">{date_pretty} &middot; By Lisa Pocius, MD</p>',
        src, count=1
    )

    # 10. Article body. Replace everything between <article class="post-body"> and
    # the Related Posts <aside>.
    new_body = ARTICLE_BODY.strip() + '\n\n        <!-- Ask Lisa: reader question form -->\n\n        <!-- Related Posts -->\n        <aside class="related-posts" aria-label="Related posts">\n            <h2 class="related-heading">Keep reading</h2>\n            <div class="related-grid">\n' + build_related_html() + '\n            </div>\n        </aside>'
    # Indent each line of ARTICLE_BODY by 8 spaces (to match the source formatting)
    indented_body_lines = []
    for line in new_body.split('\n'):
        if line.strip() == '':
            indented_body_lines.append('')
        elif line.startswith('        '):  # already indented (aside/related)
            indented_body_lines.append(line)
        else:
            indented_body_lines.append('        ' + line)
    new_body_indented = '\n'.join(indented_body_lines)

    src = re.sub(
        r'(<article class="post-body">)(.*?)(<div class="post-disclaimer">)',
        lambda m: m.group(1) + '\n' + new_body_indented + '\n\n        ' + m.group(3),
        src, count=1, flags=re.S
    )

    # 11. Update disclaimer language to match the nutrition-post pattern
    src = re.sub(
        r'This blog post is for educational purposes only and is not intended as medical advice\. Always consult with your healthcare provider about your specific treatment options\.',
        "This blog post is for educational purposes only and isn't intended as medical advice. Always consult with your healthcare provider about your specific nutrition and treatment plan.",
        src, count=1
    )

    return src


def build_blog_index_card():
    """Card for blog/index.html top position. Uses ../images/... path convention."""
    return f'''                <a href="{SLUG}.html" class="blog-card">
                    <div class="blog-card-image">
                        <picture><source type="image/webp" srcset="../images/blog-{SLUG}-400.webp 400w, ../images/blog-{SLUG}-800.webp 800w, ../images/blog-{SLUG}-1536.webp 1536w" sizes="(max-width: 768px) 100vw, 380px"><img src="../images/blog-{SLUG}.png" alt="{HERO_ALT}" width="1536" height="1024" fetchpriority="high" decoding="async"></picture>
                    </div>
                    <div class="blog-card-content">
                        <span class="blog-card-tag">{SECTION}</span>
                        <div class="blog-card-date">{datetime_pretty()}</div>
                        <h3>{HEADLINE_H1}</h3>
                        <p>{CARD_BLURB}</p>
                    </div>
                </a>'''


def build_homepage_card():
    """Card for homepage. Uses images/... (no ../). No tag. Has Read More link."""
    return f'''                <article class="blog-card">
                    <div class="blog-card-image">
                        <picture><source type="image/webp" srcset="images/blog-{SLUG}-400.webp 400w, images/blog-{SLUG}-800.webp 800w, images/blog-{SLUG}-1536.webp 1536w" sizes="(max-width: 768px) 100vw, 380px"><img src="images/blog-{SLUG}.png" alt="{HERO_ALT}" width="1536" height="1024" loading="lazy" decoding="async"></picture>
                    </div>
                    <div class="blog-card-content">
                        <div class="blog-card-date">{datetime_pretty()}</div>
                        <h3>{HEADLINE_H1}</h3>
                        <p>{CARD_BLURB}</p>
                        <a href="blog/{SLUG}.html">Read More &rarr;</a>
                    </div>
                </article>'''


def datetime_pretty():
    from datetime import datetime
    return datetime.strptime(DATE_PUBLISHED, "%Y-%m-%d").strftime("%B %-d, %Y")


def update_blog_index():
    p = REPO / 'blog/index.html'
    s = p.read_text()
    # Find the FIRST <a class="blog-card"> and insert the new card just before it.
    m = re.search(r'(<a href="[^"]+" class="blog-card">)', s)
    if not m:
        raise SystemExit("blog/index.html: could not find first blog-card")
    # Preserve the existing top card's current fetchpriority: the checklist says
    # demote the card that drops out of top 3 for eager-loading. This is a
    # list page, not a homepage, so it's less strict. Just downgrade the
    # currently-first card's fetchpriority to loading="lazy".
    old_top_card_start = m.start()
    # Find the end of the currently-first card
    end = s.find('</a>', old_top_card_start) + len('</a>')
    old_top_card = s[old_top_card_start:end]
    demoted = old_top_card.replace('fetchpriority="high"', 'loading="lazy"')
    new_card = build_blog_index_card()
    new_s = s[:old_top_card_start] + new_card + '\n                ' + demoted + s[end:]
    p.write_text(new_s)
    print(f"  updated {p} (inserted card, demoted previous top card)")


def update_homepage():
    p = REPO / 'index.html'
    s = p.read_text()
    # Homepage has exactly 3 cards in <div class="blog-grid">. Insert new card
    # at top, drop the third (oldest) so it stays 3.
    m = re.search(r'(<div class="blog-grid">)(.*?)(</div>\s*<div style="text-align: center;)', s, re.S)
    if not m:
        raise SystemExit("index.html: could not locate homepage blog-grid")
    grid_inner = m.group(2)
    # Split into <article> chunks
    articles = re.findall(r'<article class="blog-card">.*?</article>', grid_inner, re.S)
    if len(articles) != 3:
        raise SystemExit(f"index.html: expected 3 homepage cards, found {len(articles)}")
    new_card = build_homepage_card()
    # New order: new, prev[0], prev[1]. Drop prev[2].
    new_grid_inner = '\n' + new_card + '\n                ' + articles[0] + '\n                ' + articles[1] + '\n                \n            '
    new_s = s[:m.start(2)] + new_grid_inner + s[m.end(2):]
    p.write_text(new_s)
    print(f"  updated {p} (inserted new card, dropped oldest)")


def add_inbound_links():
    """Per checklist: add inbound links from existing posts. The consistency sweep
    identified two natural targets: protein-and-calcium.html and
    exercise-after-fracture.html.
    We add one link each, at the first natural mention. This is intentionally
    conservative; more inbound links can be added later after Lisa reviews."""
    inbound_targets = [
        {
            "file": "blog/protein-and-calcium.html",
            "find": "Combine all of this with resistance training",
            "note": "insert 'for what to eat during recovery, see...' sentence right after this paragraph",
            # We insert a whole new paragraph. Find the CLOSING </p> of the paragraph that
            # contains 'Combine all of this with resistance training' and insert after it.
            "insert_after_containing": "Combine all of this with resistance training",
            "new_paragraph": f'<p>If you or someone you love is recovering from a fracture, protein demand goes up right when appetite often drops. That specific window is covered in the follow-on post on <a href="{SLUG}.html">protein after a fracture</a>.</p>',
        },
        {
            "file": "blog/exercise-after-fracture.html",
            "insert_after_containing": "It protects against the fast loss of muscle that turns a temporary weakness into a lasting one.",
            "new_paragraph": f'<p>Movement is one half of that project. The other half is food, and specifically protein. Muscle and healing bone are both mostly protein, and appetite tends to drop right when the body needs more of it. The companion post on <a href="{SLUG}.html">protein after a fracture</a> covers what to eat during recovery, including easy options when cooking is not the answer.</p>',
        },
    ]

    for target in inbound_targets:
        p = REPO / target["file"]
        if not p.exists():
            print(f"  ! {target['file']} not found, skipping")
            continue
        s = p.read_text()
        # Find the paragraph containing the marker text and insert new paragraph after its closing </p>.
        marker = re.escape(target["insert_after_containing"])
        pat = re.compile(r'(<p[^>]*>[^<]*' + marker + r'[^<]*</p>)', re.S)
        m = pat.search(s)
        if not m:
            # Try looser match: the marker appears anywhere inside a <p>...</p> block
            pat2 = re.compile(r'(<p[^>]*>(?:[^<]|<(?!p[\s>]))*?' + marker + r'.*?</p>)', re.S)
            m = pat2.search(s)
        if not m:
            print(f"  ! could not locate insertion point in {target['file']} for marker: {target['insert_after_containing'][:60]}")
            continue
        # Idempotence: if the new_paragraph is already in the file, skip
        if target["new_paragraph"] in s:
            print(f"  = inbound link already present in {target['file']}, skipping")
            continue
        insertion = m.group(1) + '\n\n        ' + target["new_paragraph"]
        s = s[:m.start()] + insertion + s[m.end():]
        p.write_text(s)
        print(f"  updated {target['file']} (added inbound link paragraph)")


def main():
    print("[1/4] Building post page...")
    post = build_post_page()
    (REPO / f'blog/{SLUG}.html').write_text(post)
    print(f"       wrote blog/{SLUG}.html ({len(post)} bytes)")

    print("[2/4] Updating blog/index.html listing...")
    update_blog_index()

    print("[3/4] Updating homepage listing...")
    update_homepage()

    print("[4/4] Adding inbound links from existing posts...")
    add_inbound_links()

    print("\nDone.")


if __name__ == '__main__':
    main()
