#!/usr/bin/env python3
"""Give non-article pages the Style A header, footer and shared stylesheet. Safe to run again."""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import style_a as S

PAGES = {
    "about.html": ("", "about"), "faq.html": ("", ""), "privacy.html": ("", ""),
    "editorial-policy.html": ("", ""), "medical-disclaimer.html": ("", ""),
    "free/calcium-protein-cheat-sheet.html": ("../", "cheat"), "books/index.html": ("../", "books"),
    "books/osteoporosis-exercises-for-beginners/index.html": ("../../", "books"),
    "listen/index.html": ("../", "books"), "exercise-trackers/index.html": ("../", "books"),
}

def fix_css(css):
    # Old page CSS targeted bare nav/footer tags. Point those rules at retired class names.
    css = re.sub(r'(^|[\s,}])nav(?=[\s.{:,])', r'\1.old-nav', css)
    css = re.sub(r'(^|[\s,}])footer(?=[\s.{:,])', r'\1.old-footer', css)
    return css

def charset_first(t):
    """Browsers only look for the charset in the first 1024 bytes, so keep it right after <head>."""
    t = re.sub(r'\s*<meta charset="UTF-8">', "", t, count=1, flags=re.I)
    return t.replace("<head>", '<head>\n    <meta charset="UTF-8">', 1)

def swap(path, p, active):
    t = open(path, encoding="utf-8").read()
    t = charset_first(t)
    if 'class="legacy"' not in t:
        t = t.replace('<html lang="en">', '<html lang="en" class="legacy">', 1)
    head, body = t.split("<body", 1)
    head = re.sub(r"<style\b.*?</style>", lambda m: fix_css(m.group(0)), head, flags=re.S)
    if "mbh-style-a" not in head:
        head = S.add_css(head.replace("</head>", "").rstrip() + "\n</head>", p) if False else S.add_css(head, p)
    body = "<body" + body
    # remove the old shell pieces
    body = re.sub(r"\s*<!-- (Navigation|Nav) -->", "", body)
    body = re.sub(r"\s*<nav>.*?</nav>", "", body, count=1, flags=re.S)
    body = re.sub(r"\s*<!-- Pre-?order Banner -->", "", body, flags=re.I)
    body = re.sub(r"\s*<style>\s*\.preorder-banner\b.*?</style>", "", body, flags=re.S)
    body = re.sub(r'\s*<div class="preorder-banner">.*?</div>\s*</div>', "", body, count=1, flags=re.S)
    body = re.sub(r"<style>(.*?)</style>", lambda m: "<style>" + fix_css(m.group(1)) + "</style>"
                  if "formkit" not in m.group(1) else m.group(0), body, flags=re.S)
    body = re.sub(r"\s*<!-- Footer -->", "", body)
    body = re.sub(r"\s*<footer>.*?</footer>", "", body, count=1, flags=re.S)
    body = re.sub(r"\s*<!-- mbh:header -->.*?<!-- /mbh:header -->", "", body, flags=re.S)
    body = re.sub(r"\s*<!-- mbh:footer -->.*?<!-- /mbh:footer -->", "", body, flags=re.S)
    m = re.match(r"<body[^>]*>", body)
    body = (m.group(0) + "\n<!-- mbh:header -->\n" + S.header(p, active) + "\n<!-- /mbh:header -->"
            + body[m.end():])
    if 'id="main"' not in body:
        body = re.sub(r"<main\b", '<main id="main"', body, count=1) if "<main" in body else \
            body.replace("<!-- /mbh:header -->", '<!-- /mbh:header -->\n<span id="main"></span>', 1)
    # footer goes before the first trailing script block after content, or before </body>
    foot = "\n<!-- mbh:footer -->\n" + S.footer(p) + "\n<!-- /mbh:footer -->\n"
    pre, post = body.rsplit("</body>", 1)
    body = pre.rstrip() + "\n" + foot + "</body>" + post
    open(path, "w", encoding="utf-8").write(head + body)

if __name__ == "__main__":
    root = os.path.join(os.path.dirname(__file__), "..")
    import glob
    for f in glob.glob(os.path.join(root, "**", "*.html"), recursive=True):
        if "/node_modules/" in f or "/.git/" in f:
            continue
        s = open(f, encoding="utf-8").read()
        if 'charset="UTF-8"' in s.upper().replace('CHARSET="UTF-8"', 'charset="UTF-8"') and "<head>" in s:
            n = charset_first(s)
            if n != s:
                open(f, "w", encoding="utf-8").write(n)
    for f, (p, a) in PAGES.items():
        swap(os.path.join(root, f), p, a)
        print("ok", f)
