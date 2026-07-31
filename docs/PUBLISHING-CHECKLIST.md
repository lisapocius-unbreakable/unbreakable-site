# Publishing checklist for mybone.health

Every standard on this page came out of the SEO and AI-discoverability audit of
July 30, 2026. The site was measured against these items and brought into line
with them. This file exists so that a new post never quietly undoes that work.

Work top to bottom. Nothing here is optional, and nothing here requires
judgment about whether it matters. The judgment already happened.

---

## 1. Writing standards

- **No em dashes.** Not the character (`—`), not the HTML entity (`&mdash;`), not
  en dashes standing in for them. The only permitted `&mdash;` on a post page is
  inside the "Ask Lisa" boilerplate and the `post-meta` byline separator, which
  are template furniture rather than prose.
- **No AI cadence.** Avoid lists of three used for rhythm, "not just X but Y",
  "if not this, then that", "Here's the thing", "the bottom line", "it's
  important to note", "delve", "crucial", "robust", "leverage", "landscape",
  "testament", "Moreover", "Furthermore", "Additionally".
- **Vary sentence length deliberately.** Target a mean near 20 words with a real
  spread. A run of similar-length sentences reads synthetic even when the words
  are fine.
- **First person, physician voice.** Lisa writes as a doctor who also has this
  disease. Both halves matter.
- **Do not solicit medication questions from readers.** Inviting topic
  suggestions is fine and the Ask Lisa box does that. Inviting questions about a
  reader's own drugs edges toward individual medical advice.

## 2. Clinical accuracy, which is also legal exposure

Naming a brand-name drug raises the stakes. Assume every sentence could be read
by the manufacturer.

- **Every clinical claim traces to a primary source.** The FDA label, the trial
  publication, or the guideline document. Not a secondary summary, not a
  manufacturer's marketing site, not a health-content aggregator.
- **If a number cannot be verified in a primary source, it does not appear.**
  Leaving out a compelling statistic is always cheaper than defending it.
- **Watch for combined FDA label PDFs.** Several Amgen labels bundle two
  products in one file at very different doses. Confirm which product a section
  belongs to before quoting it.
- **Present both benefit and risk in proportion**, and give absolute numbers
  alongside relative ones. "68% reduction" and "about five fractures prevented
  per hundred women over three years" are the same fact, and readers need both.
- **Recommend an annual risk and benefit review with the reader's own provider**
  on any long-term medication post, and attribute that recommendation to Lisa
  rather than to a guideline unless a guideline actually says it.
- **Trials against placebo are not trials against each other.** If a post gives
  a percentage that a reader might set beside a percentage in another post, say
  plainly that the comparison is not head to head.

## 3. Cross-post consistency

Run this before publishing. A contradiction between two posts is worse than a
gap in one.

- Pull every numeric claim on the new post's topic out of the existing posts and
  compare them. Look especially at fracture-rate reductions, side-effect
  frequencies, and mortality figures.
- Check the arithmetic **inside** the new post. If two figures come from
  different analyses, a reader may divide one by the other and find they
  disagree. Drop one or explain the difference.
- Where two posts cite legitimately different figures for the same risk, say so
  and explain why the studies are not comparable rather than leaving the reader
  to notice.
- Do not imply a ranking between drug classes that the evidence does not
  support. The American College of Physicians places bisphosphonates first line;
  posts should not undercut that in passing.

## 4. Required page structure

- Exactly **one `<h1>`** per page.
- Heading levels descend without skipping. No `<h3>` directly under an `<h1>`.
- `<title>` **under 60 characters**, and no `| mybone.health` suffix on blog
  posts. The brand has no search demand yet and the suffix costs 15 characters.
  The `<title>` may differ from the `<h1>`; the title is for search results and
  the h1 is for the reader.
- Meta description **140 to 158 characters**. Not 90, not 190.
- Self-referencing `rel="canonical"`.
- `og:image` and `twitter:card` set to `summary_large_image`.

## 5. Structured data

Copy the JSON-LD block from the most recent medication post and edit it. Do not
write it from scratch.

- `BlogPosting` with `@id` ending `#article`
- `headline`, `description`, `url`, `articleSection`, `inLanguage`
- Both `datePublished` and `dateModified`
- `isPartOf` pointing at `https://mybone.health/blog/#blog`
- `mainEntityOfPage`
- `author` referencing the stable Person node `https://mybone.health/#lisa-pocius`
- `publisher`
- Absolute `image` URL
- Validate that it parses as JSON before committing.

## 6. Images

The audit found 40 MB of PNG heroes on the blog index. Do not reintroduce that.

- Generate the hero at 1536x1024.
- Produce WebP variants at **400, 800, and 1536 px wide, quality 82, method 6**.
  `scripts/` has the conversion pattern; reuse it.
- Serve through `<picture>` with a WebP `<source srcset>` and the PNG as the
  `<img>` fallback. Real example from `blog/prolia-denosumab-explained.html`:

  ```html
  <picture><source type="image/webp"
    srcset="../images/blog-SLUG-400.webp 400w,
            ../images/blog-SLUG-800.webp 800w,
            ../images/blog-SLUG-1536.webp 1536w"
    sizes="100vw"><img src="../images/blog-SLUG.png"
    alt="..." width="1536" height="1024"
    fetchpriority="high" decoding="async"></picture>
  ```

- Always set explicit `width` and `height`. Missing dimensions cause layout
  shift, which is a measured ranking factor.
- `sizes` differs by context: `100vw` for a post hero, `(max-width: 768px)
  100vw, 380px` for a blog-index card, `(max-width: 768px) 100vw, 320px` for a
  related-posts card.
- **At most three images per page may be eager.** Everything else gets
  `loading="lazy"`. When a new card goes to the top of the blog index, demote the
  card that fell out of the top three from `fetchpriority="high"` to
  `loading="lazy"`.
- Alt text describes the picture for someone who cannot see it. It is not a
  keyword slot.

## 7. Wiring the post into the site

- Insert a card at the top of `.blog-grid` in `blog/index.html`.
- Insert a card at the top of `.blog-grid` in `index.html`, and remove the last
  card so the homepage keeps exactly three.
- Card blurb length should match its neighbours. Around 250 to 270 characters
  keeps the cards visually balanced.
- Note the path difference: blog pages use `../images/...`, the homepage uses
  `images/...`.
- Add three related-post cards at the foot of the new post.
- **Add inbound links from existing posts.** A post nothing links to is a dead
  end for crawlers and for readers. Search the existing posts for the new topic
  and link the first natural mention in each.

## 8. Verify before committing

- All internal links and image files resolve on disk.
- Every HTML tag balanced; one `h1`; JSON-LD parses.
- Render the page at 1440px and at 390px. Read the screenshots. Check for text
  overflow, mid-word wrapping, broken headings, and horizontal scroll.
- Confirm the browser picks the expected WebP variant at each width.
- Re-run the em dash and AI-cadence scans on the final file, not the draft.

## 9. Committing and deploying

- Commit to `main` on `lisapocius-unbreakable/unbreakable-site`.
- Pushing a change under `blog/**.html` triggers the **Auto-update sitemap and
  feeds** Action, which regenerates `sitemap.xml`, `feed.xml`, and `atom.xml` and
  commits them back. Do not hand-edit those three files.
- That Action creates its own commit. **Pull before pushing anything else**, or
  the next push is rejected.
- **Hostinger does not auto-deploy.** Lisa deploys manually. Say so explicitly
  every time; a pushed post is not a published post.

## 10. Confirm in production

`fetch_url` is blocked by the site's robots handling. Use `curl` with a browser
User-Agent, or Playwright.

Check the post URL, the images, the sitemap entry, the feed item count, both
listing pages, and the inbound links. Note that nejm.org and acpjournals.org
return 403 to command-line requests; those links are fine for readers.

---

## Known deliberate exceptions

- The hero band is a fixed 350px `object-fit: cover` (220px on mobile), so every
  hero crops. This is site-wide and intentional. Do not adjust the template for
  one post.
- Four older posts have `-fb.png` and `-pin.png` social variants. That belongs to
  a separate social workflow and is not part of publishing a post.

## Audit items still outstanding

Not yet approved or done, kept here so they are not forgotten:

`MedicalWebPage` schema with `lastReviewed` and `reviewedBy`; `Drug` entities on
medication posts; `FAQPage` markup on posts with question-shaped headings;
`llms.txt`; `/about.html` author entity page; `BreadcrumbList`; privacy,
editorial-policy, and medical-disclaimer pages; the `www` to non-www 301 at the
Hostinger level.
