#!/usr/bin/env python3
"""One-off consistency sweep for protein/muscle/fall/recovery claims across all blog posts.

Follows references/consistency-check.md: works on rendered body, not raw HTML.
"""
import pathlib, re, html, sys, json

BLOG = pathlib.Path("blog")

def body(path):
    s = pathlib.Path(path).read_text()
    m = re.search(r'<article class="post-body">(.*?)(<aside class="ask-lisa"|</article>)', s, re.S)
    if not m:
        # fallback: try main content between <main> and footer
        m = re.search(r'<main.*?>(.*?)</main>', s, re.S)
    if not m:
        return ""
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(1))))

# Topic sweeps for Option B (protein/recovery/falls/muscle)
TOPIC_PATTERNS = {
    "protein_g_per_kg": re.compile(r'\d+(?:\.\d+)?\s*(?:to|-)?\s*\d*(?:\.\d+)?\s*(?:g|gram|grams)\s*(?:per|/)\s*(?:kg|kilogram|pound|lb)', re.I),
    "protein_grams_per_meal": re.compile(r'\d+\s*(?:to|-)?\s*\d*\s*(?:g|gram|grams)\s*(?:per\s*meal|at\s*each\s*meal|each\s*meal)', re.I),
    "protein_word": re.compile(r'\bprotein\b', re.I),
    "muscle_word": re.compile(r'\b(muscle|sarcopeni|strength\s*training|resistance)', re.I),
    "fall_word": re.compile(r'\b(fall|falling|falls|balance)\b', re.I),
    "recovery_word": re.compile(r'\b(recovery|rehab|hip\s*fracture|hospital|recover)', re.I),
    "igf": re.compile(r'\b(IGF|insulin.like\s*growth)', re.I),
    "hip_fx_mortality": re.compile(r'\b\d+\s*%[^.]{0,60}(mortality|die|death|first\s*year)', re.I),
    "ranking": re.compile(r'\b(most effective|strongest|most powerful|first.line|second.line|gold standard|best (?:option|treatment|drug)|more effective)\b', re.I),
}

def sentences(text):
    return re.split(r'(?<=[.!?])\s+', text)

def sweep():
    findings = {}
    for f in sorted(BLOG.glob("*.html")):
        if f.name == "index.html":
            continue
        text = body(f)
        if not text:
            continue
        sents = sentences(text)
        hits = {}
        for topic, pat in TOPIC_PATTERNS.items():
            matches = [s.strip() for s in sents if pat.search(s)]
            if matches:
                hits[topic] = matches
        if hits:
            findings[f.name] = hits
    return findings

if __name__ == "__main__":
    out = sweep()
    print(json.dumps(out, indent=2))
