"""Re-extract exam PDFs into structured JSON using pdfplumber tables.

Each PDF is a 2-3 column table:
  col 0 = subsection label (may be None for continuation rows)
  col 1 = checklist item text
  col 2 = (usually empty / student notes)

Major section headers appear as rows where only col 0 has text and cols 1..N are
None. They're also typically ALL CAPS.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber

EXAMS_DIR = Path(__file__).resolve().parent.parent / "exams"
OUT_FILE = Path(__file__).resolve().parent.parent / "app" / "data" / "exams.json"

TITLES = {
    "Breast and Axilla CO27 DXM PE Checklists": "Breast & Axilla",
    "CO27 DXM Female GU PE Checklist": "Female GU",
    "CO27 DXM LE PE Checklists": "Lower Extremity (MSK)",
    "CO27 DXM MSK-UE PE Checklists": "Upper Extremity (MSK)",
    "CO27 DXM Spine PE Checklists": "Spine (MSK)",
    "Male GU PE Checklist": "Male GU",
    "Neuro Checklist": "Neurologic",
}

# Items that are page titles / course headers.
DROP_ITEM_PATTERNS = [
    r"diagnostic medicine",
    r"physical exam checklist",
    r"^starting the patient encounter$",
]
DROP_ITEM_RE = re.compile("|".join(DROP_ITEM_PATTERNS), re.IGNORECASE)


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


_ANNOTATION_RE = re.compile(
    r"("
    r"↳.*?$"            # student arrow annotations (disease associations etc.)
    r"|⊥.*?$"
    r"|→.*?$"
    r"|(?<!^)↑.*?$"    # ↑ stripped only if not at the very start
    r"|\s+~.*?$"
    r"|=\s*ipsi.*?$"
    r")"
)

# Patterns that appear as trailing gibberish on subsection names (student notes
# written in the header cell of the printed checklist, which pdfplumber picks up).
_LABEL_TRAILING_NOISE_RE = re.compile(
    r"\s+("
    r"SS[A-Z]{2,}[A-Z]*"           # SSCOULDR, SSSDDCC, SSSC, SSSS mnemonic letters
    r"|non\s*$"                    # "PALPATION BILATERALLY non"
    r"|IDC\b.*"
    r"|Also in\b.*"
    r"|Taysupine.*"
    r"|Trendenberg.*"
    r"|copymy movements"
    r"|9\)\s*Joint.*"
    r"|inflammaati"
    r"|um\s*leave"
    r"|Nipple inversion,?\s*Nipple retraction.*"
    r"|\"[^\"]*\""
    r")\s*$"
)


def clean_label(text: str) -> str:
    s = clean_text(text)
    # Iteratively strip trailing noise
    while True:
        new = _LABEL_TRAILING_NOISE_RE.sub("", s).strip()
        if new == s:
            break
        s = new
    # Drop stray trailing punctuation
    s = re.sub(r"[\s:–-]+$", "", s).strip()
    # Normalize titlecase for all-caps section names
    if s.isupper():
        s = s.title()
    return s


def clean_text(text: str | None) -> str:
    if not text:
        return ""
    s = text.replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    # Strip (cid:N) PDF character-encoding failures
    s = re.sub(r"\(cid:\d+\)", "", s).strip()
    # Remove handwritten annotations bleeding across cell edges
    s = _ANNOTATION_RE.sub("", s).strip()
    # Strip trailing garbage single-letter student marks (e.g., " I", " 3", " Y")
    s = re.sub(r"\s+[A-Za-z0-9]{1,2}\s*$", "", s)
    # Collapse any doubled spaces created by removals
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Specific handwritten fragments that bled into the PDF text layer. These are
# discovered by auditing the parsed output. If a checklist item is exactly one
# of these (or contains one as an obvious trailing suffix), we drop/strip it.
_ITEM_NOISE_FULL = {
    "Stront",
    "HOU Road",
    "Sam",
    "LIFE",
    "IDC",
    "Im",
    "IT Ssce",
    "Ams",
    "non",
    "PB ASS",
}
_ITEM_TRAILING_NOISE_RE = re.compile(
    r"\s+("
    r"back"
    r"|Sam"
    r"|LIFE"
    r"|IDC"
    r"|Im"
    r"|Ams"
    r"|HOU Road"
    r"|PB ASS"
    r"|L for Anterior"
    r")\s*$"
)


def scrub_item(text: str) -> str | None:
    """Remove known handwritten-annotation noise. Returns None if the item
    is entirely noise (so the caller should drop it)."""
    s = text.strip()
    if s in _ITEM_NOISE_FULL:
        return None
    # Strip trailing annotations
    prev = None
    while prev != s:
        prev = s
        s = _ITEM_TRAILING_NOISE_RE.sub("", s).strip()
    if not s or s in _ITEM_NOISE_FULL:
        return None
    return s


def is_all_caps(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    return sum(1 for c in letters if c.isupper()) / len(letters) >= 0.8


def split_items(cell: str) -> list[str]:
    """Split a multi-line cell into discrete checklist items."""
    if not cell:
        return []
    # pdfplumber preserves newlines in cells → each line is usually one item.
    parts = [p.strip() for p in cell.split("\n")]
    # Re-merge continuation lines (start with lowercase / comma / paren / hyphen).
    merged: list[str] = []
    for p in parts:
        if not p:
            continue
        if merged and p and (p[0].islower() or p.startswith(("(", ")", "-", ","))):
            merged[-1] = (merged[-1] + " " + p).strip()
        else:
            merged.append(p)
    # Clean each
    cleaned: list[str] = []
    for m in merged:
        c = clean_text(m)
        if not c:
            continue
        if len(c) < 4:
            continue
        if DROP_ITEM_RE.search(c):
            continue
        cleaned.append(c)
    return cleaned


def parse_pdf(pdf_path: Path) -> list[dict]:
    sections: list[dict] = []
    current_major: dict | None = None
    current_sub: dict | None = None

    def ensure_major(name: str) -> dict:
        nonlocal current_major
        for s in sections:
            if s["name"] == name:
                return s
        s = {"name": name, "subsections": []}
        sections.append(s)
        return s

    def ensure_sub(major: dict, name: str) -> dict:
        for sub in major["subsections"]:
            if sub["name"] == name:
                return sub
        sub = {"name": name, "items": []}
        major["subsections"].append(sub)
        return sub

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            tables = page.find_tables()
            for table in tables:
                rows = table.extract()
                for row in rows:
                    # Drop Nones and empties at tail for easier inspection
                    if not row or all(not (c or "").strip() for c in row):
                        continue
                    label_cell = (row[0] or "").strip() if len(row) > 0 else ""
                    other_cells = [(c or "").strip() for c in row[1:]]
                    non_empty_others = [c for c in other_cells if c]

                    # Long sentence-like col-0 rows are checklist items (test
                    # descriptions), NOT subsection labels — even if col 2 has
                    # stray text (pdfplumber sometimes splits word wraps across
                    # columns: e.g. "lumbarradiculo" in col 0 and "pathy" in
                    # col 2). Treat the entire row as one item.
                    if label_cell and len(label_cell) > 60 and " " in label_cell:
                        if current_major is None:
                            current_major = ensure_major("General")
                        if current_sub is None:
                            current_sub = ensure_sub(current_major, "Steps")
                        # Merge col 0 + other non-empty cells. If the col-0 text
                        # ends mid-word (no trailing space) and the other cell
                        # is a short fragment, join directly (no space).
                        col0 = clean_text(label_cell)
                        extras = [clean_text(c) for c in other_cells if c and c.strip()]
                        merged = col0
                        for ex in extras:
                            if len(ex) <= 12 and merged and merged[-1].isalpha() and ex[0].isalpha():
                                merged = merged + ex  # continuation fragment
                            else:
                                merged = merged + " " + ex
                        for item in split_items(merged):
                            current_sub["items"].append(item)
                        continue

                    # Major section: label is set, other columns all empty/None
                    if label_cell and not non_empty_others:
                        name = clean_text(label_cell)
                        if is_all_caps(name):
                            current_major = ensure_major(clean_label(name))
                            current_sub = None
                            continue
                        # Otherwise it's a subsection label for a default major.
                        if current_major is None:
                            current_major = ensure_major("General")
                        current_sub = ensure_sub(current_major, clean_label(name))
                        continue

                    # Subsection header + item row
                    if label_cell:
                        if current_major is None:
                            current_major = ensure_major("General")
                        current_sub = ensure_sub(current_major, clean_label(label_cell))

                    if current_sub is None:
                        if current_major is None:
                            current_major = ensure_major("General")
                        current_sub = ensure_sub(current_major, "Steps")

                    # Use the FIRST non-empty "other" column as item content.
                    # Columns beyond col 1 are usually empty or notes; skip them.
                    item_cell = non_empty_others[0] if non_empty_others else ""
                    for item in split_items(item_cell):
                        current_sub["items"].append(item)

    # Scrub handwritten noise, dedupe, and drop empties
    for sec in sections:
        for sub in sec["subsections"]:
            seen = set()
            uniq = []
            for it in sub["items"]:
                scrubbed = scrub_item(it)
                if not scrubbed:
                    continue
                k = re.sub(r"\s+", " ", scrubbed.lower()).strip()
                if k in seen:
                    continue
                seen.add(k)
                uniq.append(scrubbed)
            sub["items"] = uniq
        sec["subsections"] = [s for s in sec["subsections"] if s["items"]]
    sections = [s for s in sections if s["subsections"]]
    return sections


def main() -> None:
    out = {}
    for pdf in sorted(EXAMS_DIR.glob("*.pdf")):
        key = pdf.stem
        title = TITLES.get(key, key)
        slug = slugify(title)
        sections = parse_pdf(pdf)
        item_count = sum(len(sub["items"]) for sec in sections for sub in sec["subsections"])
        sub_count = sum(len(sec["subsections"]) for sec in sections)
        out[slug] = {
            "slug": slug,
            "title": title,
            "source_file": pdf.name,
            "sections": sections,
            "item_count": item_count,
        }
        print(f"{slug}: {len(sections)} sections, {sub_count} subs, {item_count} items")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
