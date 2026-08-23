#!/usr/bin/env python3
"""Enrich medication-post JSON-LD with medical-authority fields.

For each medication post:
- Change "@type": "BlogPosting" to ["BlogPosting", "MedicalWebPage"].
- Add "lastReviewed" (today's date, YYYY-MM-DD).
- Add "reviewedBy" pointing to the same #lisa-pocius Person.
- Add "about" listing a Drug entity for each drug the post covers.

Idempotent: skips if "MedicalWebPage" already present in the first JSON-LD
block.

Runs a JSON parse over the modified block before writing.
"""
import json
import re
from datetime import date
from pathlib import Path

BLOG = Path(__file__).resolve().parent.parent / "blog"
TODAY = date.today().isoformat()

# Which post covers which drugs. Names use the schema.org Drug convention
# (nonproprietaryName for generic, name for brand).
POSTS = {
    "prolia-denosumab-explained.html": [
        {"@type": "Drug", "name": "Prolia", "nonproprietaryName": "denosumab"},
    ],
    "bisphosphonates-explained.html": [
        {"@type": "Drug", "name": "Fosamax", "nonproprietaryName": "alendronate"},
        {"@type": "Drug", "name": "Actonel", "nonproprietaryName": "risedronate"},
        {"@type": "Drug", "name": "Boniva", "nonproprietaryName": "ibandronate"},
        {"@type": "Drug", "name": "Reclast", "nonproprietaryName": "zoledronic acid"},
    ],
    "bisphosphonate-tips.html": [
        {"@type": "Drug", "name": "Fosamax", "nonproprietaryName": "alendronate"},
        {"@type": "Drug", "name": "Actonel", "nonproprietaryName": "risedronate"},
    ],
    "evenity-explained.html": [
        {"@type": "Drug", "name": "Evenity", "nonproprietaryName": "romosozumab"},
    ],
    "anabolic-medications.html": [
        {"@type": "Drug", "name": "Forteo", "nonproprietaryName": "teriparatide"},
        {"@type": "Drug", "name": "Tymlos", "nonproprietaryName": "abaloparatide"},
    ],
}

REVIEWED_BY = {"@id": "https://mybone.health/#lisa-pocius"}


def enrich(path: Path, drugs: list) -> str:
    html = path.read_text(encoding="utf-8")

    # Locate first JSON-LD block.
    pattern = re.compile(
        r'(<script type="application/ld\+json">\s*)(\{.*?\})(\s*</script>)',
        flags=re.S,
    )
    m = pattern.search(html)
    if not m:
        return "skip (no JSON-LD block)"

    raw = m.group(2)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return f"skip (JSON parse failed: {e})"

    # Idempotency check.
    existing_type = data.get("@type")
    if isinstance(existing_type, list) and "MedicalWebPage" in existing_type:
        return "skip (already enriched)"
    if existing_type == "MedicalWebPage":
        return "skip (already MedicalWebPage)"

    # Add MedicalWebPage as co-type.
    if isinstance(existing_type, str):
        data["@type"] = [existing_type, "MedicalWebPage"]
    elif isinstance(existing_type, list):
        data["@type"] = list(dict.fromkeys(existing_type + ["MedicalWebPage"]))
    else:
        return "skip (unexpected @type)"

    # Add medical-authority fields. Preserve any existing "about".
    data["lastReviewed"] = TODAY
    data["reviewedBy"] = REVIEWED_BY

    existing_about = data.get("about")
    if isinstance(existing_about, list):
        merged = existing_about + drugs
    elif existing_about:
        merged = [existing_about] + drugs
    else:
        merged = drugs
    data["about"] = merged

    new_block = json.dumps(data, indent=2, ensure_ascii=False)
    # Re-indent to match surrounding four-space style.
    new_block = "\n".join(("    " + line) if line else line for line in new_block.splitlines())

    new_html = html[:m.start(2)] + new_block + html[m.end(2):]
    # Validate parse.
    check = pattern.search(new_html)
    json.loads(check.group(2))
    path.write_text(new_html, encoding="utf-8")
    return "enriched"


def main():
    for name, drugs in POSTS.items():
        path = BLOG / name
        if not path.exists():
            print(f"{name}: skip (not found)")
            continue
        print(f"{name}: {enrich(path, drugs)}")


if __name__ == "__main__":
    main()
