"""LLM-based oral-practice grader using Claude.

Sends the full PDF checklist plus the student's transcript to
claude-haiku-4-5 and asks for a per-item covered/not-covered judgement with a
short reason. Handles paraphrasing, synonyms, and negation — unlike the
keyword scorer.

Falls back to None on any failure (missing API key, network, parse error) so
the caller can gracefully use the keyword scorer instead.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Optional

log = logging.getLogger(__name__)

_client = None
_client_error: str | None = None

MODEL = os.environ.get("LLM_MODEL", "claude-haiku-4-5")
MAX_OUTPUT_TOKENS = 8000

SYSTEM_PROMPT = """You are grading a medical student's oral recitation of a physical exam checklist.
The student has recited the exam aloud from memory; you receive the Whisper transcript and the checklist.

For each numbered checklist item, decide whether the student covered that specific item.

Rules:
- ACCEPT paraphrasing and common synonyms: "feel" ≈ "palpate", "look at" ≈ "inspect", "check" ≈ "assess", "listen to" ≈ "auscultate". Medical-speak and lay-speak both count.
- ACCEPT partial verbalization of a bundled item: if an item lists several sub-components and the student mentioned the item and most of its sub-components, count it covered.
- REJECT negated statements: "I would not do X" is NOT coverage of X.
- REJECT vague mentions that don't actually address the specific item.
- IGNORE minor Whisper transcription errors (word-level misspellings).
- The student may go out of order; that's fine — grade on whether it was covered, not on ordering.

Return STRICT JSON: an array where each element is {"id": int, "covered": bool, "reason": "short phrase, <=15 words"}.
Include one entry per numbered checklist item. Return only the JSON — no prose, no markdown fences."""


def _get_client():
    global _client, _client_error
    if _client is not None:
        return _client
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        _client_error = "ANTHROPIC_API_KEY not set"
        return None
    try:
        import anthropic  # type: ignore

        _client = anthropic.Anthropic(api_key=key)
        _client_error = None
        return _client
    except Exception as e:  # pragma: no cover
        _client_error = f"{type(e).__name__}: {e}"
        return None


def status() -> dict:
    key_set = bool(os.environ.get("ANTHROPIC_API_KEY"))
    return {
        "available": key_set and _client_error is None,
        "model": MODEL,
        "error": _client_error,
    }


def _flatten(exam: dict) -> list[dict]:
    out: list[dict] = []
    for sec in exam.get("sections", []):
        for sub in sec.get("subsections", []):
            for item in sub.get("items", []):
                out.append({
                    "id": len(out),
                    "section": sec["name"],
                    "subsection": sub["name"],
                    "text": item,
                })
    return out


def _parse_grades_json(text: str) -> list[dict]:
    """Robustly parse Claude's JSON output (handles stray fences / prose)."""
    s = text.strip()
    if s.startswith("```"):
        # strip ``` fences
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"\n?```$", "", s)
    # Find first [ and last ]
    start = s.find("[")
    end = s.rfind("]")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON array found in LLM output")
    return json.loads(s[start : end + 1])


def llm_grade(exam: dict, transcript: str) -> Optional[dict]:
    """Run the LLM grader on a transcript. Returns a report dict in the same
    shape as the keyword scorer, with `grader: 'llm'`. Returns None on failure.
    """
    client = _get_client()
    if client is None:
        return None

    items = _flatten(exam)
    if not items:
        return None

    items_text = "\n".join(
        f"{it['id']}. [{it['section']} → {it['subsection']}] {it['text']}"
        for it in items
    )
    user_msg = (
        f"Exam: {exam['title']}\n\n"
        f"Checklist items (one per line, numbered):\n{items_text}\n\n"
        f"Student transcript:\n\"\"\"\n{transcript.strip() or '(empty)'}\n\"\"\"\n\n"
        f"Return a JSON array with {len(items)} entries — one per checklist id — "
        f"using the format described in the system prompt."
    )

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_OUTPUT_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as e:  # pragma: no cover
        log.warning("LLM grader API call failed: %s", e)
        return None

    # Extract text from response
    try:
        text_parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
        raw_text = "\n".join(text_parts) if text_parts else resp.content[0].text  # type: ignore[attr-defined]
    except Exception as e:  # pragma: no cover
        log.warning("LLM grader response shape unexpected: %s", e)
        return None

    try:
        grades = _parse_grades_json(raw_text)
    except Exception as e:
        log.warning("LLM grader JSON parse failed: %s; raw=%r", e, raw_text[:300])
        return None

    grade_map: dict[int, dict] = {}
    for g in grades:
        gid = g.get("id")
        if isinstance(gid, int):
            grade_map[gid] = g

    # Build the report in the same shape as the keyword scorer.
    total = 0
    covered = 0
    sec_reports: list[dict] = []
    flat_idx = 0
    for sec in exam.get("sections", []):
        sec_total = 0
        sec_cov = 0
        sub_reports: list[dict] = []
        for sub in sec.get("subsections", []):
            sub_total = 0
            sub_cov = 0
            item_reports: list[dict] = []
            for item in sub.get("items", []):
                g = grade_map.get(flat_idx, {})
                is_cov = bool(g.get("covered", False))
                reason = (g.get("reason") or "").strip()
                item_reports.append({
                    "item": item,
                    "covered": is_cov,
                    "reason": reason,
                    "coverage": 1.0 if is_cov else 0.0,
                    "keywords": [],
                    "hits": [],
                })
                sub_total += 1
                if is_cov:
                    sub_cov += 1
                flat_idx += 1
            if sub_total == 0:
                continue
            sub_reports.append({
                "name": sub["name"],
                "total": sub_total,
                "covered": sub_cov,
                "score_pct": round(100 * sub_cov / sub_total, 1),
                "items": item_reports,
            })
            sec_total += sub_total
            sec_cov += sub_cov
        if sec_total == 0:
            continue
        sec_reports.append({
            "name": sec["name"],
            "total": sec_total,
            "covered": sec_cov,
            "score_pct": round(100 * sec_cov / sec_total, 1),
            "subsections": sub_reports,
        })
        total += sec_total
        covered += sec_cov

    if total == 0:
        return None

    return {
        "exam": {"slug": exam["slug"], "title": exam["title"]},
        "score_pct": round(100 * covered / total, 1),
        "total_items": total,
        "covered_items": covered,
        "word_count": len(transcript.split()),
        "sections": sec_reports,
        "weakest_sections": sorted(
            [
                {
                    "name": s["name"],
                    "score_pct": s["score_pct"],
                    "covered": s["covered"],
                    "total": s["total"],
                }
                for s in sec_reports
            ],
            key=lambda s: s["score_pct"],
        )[:5],
        "grader": "llm",
        "model": MODEL,
    }
