"""OSCE scenario generator + grader for DXM III practice.

Flow:
  1. `generate(category)` → Claude returns a patient chart + a scenario-
     specific rubric. We store the rubric server-side keyed by a UUID so it
     can't be inspected from the browser.
  2. Student reads the chart, records their focused physical exam out loud,
     and submits the transcript.
  3. `grade(scenario_id, transcript)` → Claude grades the transcript against
     the stored rubric and returns a section-aware report in the same shape
     the oral-practice page already renders.

Everything runs through the Anthropic Messages API using the same client
configured for llm_grader.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from typing import Optional

from . import llm_grader

log = logging.getLogger(__name__)

SCENARIO_TTL_SECONDS = 60 * 60 * 2  # 2 hours
_STORE: dict[str, dict] = {}

CATEGORIES = [
    ("any", "Any (random)"),
    ("neuro", "Neurology"),
    ("msk_spine", "MSK — Spine"),
    ("msk_ue", "MSK — Upper Extremity"),
    ("msk_le", "MSK — Lower Extremity"),
    ("rheum", "Rheumatology"),
    ("male_gu", "Male GU"),
    ("female_gu", "Female GU"),
    ("dxm2_mixed", "DXM II mixed (derm / HEENT / cardio / pulm / abd)"),
]

CATEGORY_LABELS = dict(CATEGORIES)

GENERATE_SYSTEM = """You generate clinical OSCE scenarios for Diagnostic Medicine III medical students.

Each scenario includes:
- A realistic patient chart the student reads before entering the exam room
- A grading rubric of the specific physical-exam components the student must perform or verbalize to get credit for a focused exam of this presentation

OSCE CONSTRAINTS (must be reflected in the rubric):
- No invasive exams on standardized patients (no DRE, no pelvic, no breast). If such an exam would be relevant, the rubric item should say the student should verbalize that they would perform it on a task trainer.
- Special tests MUST be verbalized by the student, not performed. Rubric items for special tests must read "Verbalize X test" not "Perform X test".
- No thoracolumbar range of motion (the SP will redirect).
- Every exam must include: introduction & verification of identity, hand hygiene, PPE, proper draping, general survey, basic cardiovascular screen, basic pulmonary screen, and a focused examination for the presentation.
- Rubric items must be things the student SAYS OUT LOUD during the focused physical exam. They recite what they are inspecting, palpating, auscultating, assessing, etc.
- Rubric items should be concrete and specific (e.g. "Inspect the lumbar spine for curvature, asymmetry, and muscle spasm" not "Inspect the back").
- 15-30 total items across 4-6 sections is typical.
- Mark "critical items" — actions whose omission would be a critical fail for this specific scenario (e.g. for testicular torsion, examining both testes; for suspected radiculopathy, verbalizing straight-leg raise).

Pick common, teachable presentations. Examples:
- Neuro: stroke/TIA, Bell palsy, migraine, peripheral neuropathy, carpal tunnel
- MSK Spine: lumbar radiculopathy, cervical radiculopathy, mechanical LBP, spinal stenosis
- MSK UE: rotator cuff tear, shoulder impingement, lateral epicondylitis, De Quervain
- MSK LE: knee OA, meniscus tear, ACL tear, ankle sprain, Achilles rupture, plantar fasciitis
- Rheum: RA, OA, gout, polymyalgia rheumatica
- Male GU: epididymitis, testicular torsion, varicocele, inguinal hernia, BPH
- Female GU: PID, ovarian cyst, ectopic pregnancy, endometriosis
- DXM II: pneumonia, COPD exacerbation, heart failure, MI, appendicitis, cholecystitis, cellulitis, sinusitis

Return STRICT JSON only. No prose, no markdown fences."""

GENERATE_USER_TEMPLATE = """Generate an OSCE scenario for category: {category_label}

Return JSON in this exact schema:
{{
  "title": "brief title for the case, e.g. 'Acute low back pain'",
  "body_system": "{category_slug}",
  "chart": {{
    "chief_complaint": "one-line chief complaint",
    "hpi": "full HPI paragraph including age, sex, onset, character, quality, location, radiation, associated symptoms, alleviating/aggravating factors",
    "pmh": "past medical history",
    "medications": "current meds",
    "allergies": "allergies",
    "family_history": "relevant family history",
    "social_history": "relevant social history",
    "review_of_systems": "pertinent positives and negatives",
    "vitals": {{"T": "", "HR": "", "BP": "", "RR": "", "SpO2": ""}}
  }},
  "rubric": {{
    "sections": [
      {{
        "name": "Introduction & Setup",
        "items": [
          "Introduce self with first and last name and role",
          "Verify patient identity using two identifiers",
          "Wash or sanitize hands",
          "Don appropriate PPE",
          "Ensure proper patient draping",
          "Verbalize general survey observations"
        ]
      }},
      {{
        "name": "Baseline Cardiovascular & Pulmonary",
        "items": [
          "Auscultate the heart in all four valve areas",
          "Auscultate lung fields bilaterally",
          "Assess peripheral pulses and cap refill"
        ]
      }},
      {{
        "name": "Focused [specific body system] Exam",
        "items": ["specific items here"]
      }},
      {{
        "name": "Special Tests (verbalize only)",
        "items": ["Verbalize X test to evaluate for Y"]
      }}
    ],
    "critical_items": ["exact text of any items whose omission is a critical fail for this case"]
  }}
}}

Return ONLY the JSON object, nothing else."""

GRADE_SYSTEM = """You are grading a DXM III medical student's focused physical exam recitation for an OSCE scenario.

The student received a patient chart and was instructed to perform a focused physical exam. They recited aloud what they were doing; you have the Whisper transcript.

For each rubric item, decide whether the student covered that specific action.

Rules:
- ACCEPT paraphrasing and layman synonyms: "feel" ≈ "palpate", "look at" ≈ "inspect", "check" ≈ "assess", "listen to" ≈ "auscultate". Both medical-speak and lay-speak count.
- ACCEPT partial verbalization of a bundled item: if an item lists several sub-components and the student mentioned the item and most of its sub-components, count it covered.
- REJECT negated statements: "I would not do X" is NOT coverage of X.
- REJECT vague mentions that don't actually address the specific item.
- Special tests must be verbalized with the test name. If an item reads "Verbalize straight-leg raise test", the student must at minimum say they would perform that test.
- IGNORE minor Whisper transcription errors.

Return STRICT JSON: array where each element is {"id": int, "covered": bool, "reason": "short, <=15 words"}. Include one entry per rubric item. JSON only, no prose, no markdown fences."""


def status() -> dict:
    return {
        "available": llm_grader.status()["available"],
        "model": llm_grader.MODEL,
        "stored": len(_STORE),
    }


def _prune_store() -> None:
    now = time.time()
    expired = [k for k, v in _STORE.items() if v["_expires_at"] < now]
    for k in expired:
        _STORE.pop(k, None)


def _parse_json_object(text: str) -> dict:
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"\n?```$", "", s)
    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON object in output")
    return json.loads(s[start : end + 1])


def _parse_json_array(text: str) -> list:
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"\n?```$", "", s)
    start = s.find("[")
    end = s.rfind("]")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON array in output")
    return json.loads(s[start : end + 1])


def generate(category: str = "any") -> Optional[dict]:
    """Generate a new scenario via Claude. Returns a dict with scenario_id +
    chart for the frontend; the hidden rubric is kept in _STORE."""
    client = llm_grader._get_client()
    if client is None:
        log.warning("scenario generate: no Anthropic client")
        return None

    if category not in CATEGORY_LABELS:
        category = "any"
    cat_label = CATEGORY_LABELS[category]
    cat_slug = category if category != "any" else "pick a random one"

    user_msg = GENERATE_USER_TEMPLATE.format(
        category_label=cat_label, category_slug=cat_slug
    )

    try:
        resp = client.messages.create(
            model=llm_grader.MODEL,
            max_tokens=4096,
            system=GENERATE_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as e:  # pragma: no cover
        log.warning("scenario generate API call failed: %s", e)
        return None

    try:
        text_parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
        raw = "\n".join(text_parts)
        data = _parse_json_object(raw)
    except Exception as e:
        log.warning("scenario generate parse failed: %s", e)
        return None

    # Validate shape
    if not all(k in data for k in ("title", "chart", "rubric")):
        log.warning("scenario generate missing required keys")
        return None
    if "sections" not in data["rubric"]:
        return None

    scenario_id = uuid.uuid4().hex
    _STORE[scenario_id] = {
        "_expires_at": time.time() + SCENARIO_TTL_SECONDS,
        "title": data["title"],
        "body_system": data.get("body_system", "unknown"),
        "chart": data["chart"],
        "rubric": data["rubric"],
        "category": category,
    }
    _prune_store()

    return {
        "scenario_id": scenario_id,
        "title": data["title"],
        "body_system": data.get("body_system", "unknown"),
        "category": category,
        "category_label": cat_label,
        "chart": data["chart"],
    }


def get(scenario_id: str) -> Optional[dict]:
    _prune_store()
    sc = _STORE.get(scenario_id)
    if not sc:
        return None
    return {
        "scenario_id": scenario_id,
        "title": sc["title"],
        "body_system": sc["body_system"],
        "category": sc["category"],
        "category_label": CATEGORY_LABELS.get(sc["category"], sc["category"]),
        "chart": sc["chart"],
    }


def _flatten_rubric(rubric: dict) -> list[dict]:
    out: list[dict] = []
    for sec in rubric.get("sections", []):
        for item in sec.get("items", []):
            out.append({
                "id": len(out),
                "section": sec["name"],
                "text": item,
            })
    return out


def grade(scenario_id: str, transcript: str) -> Optional[dict]:
    """Grade the student's transcript against the stored rubric for this
    scenario. Returns a report in the same shape the oral-practice page
    already renders (grader='llm' with section/subsection breakdown)."""
    _prune_store()
    sc = _STORE.get(scenario_id)
    if not sc:
        return None
    client = llm_grader._get_client()
    if client is None:
        return None

    rubric = sc["rubric"]
    items = _flatten_rubric(rubric)
    if not items:
        return None

    # Normalize critical-item matching: strip a leading "CRITICAL:" prefix
    # (the LLM sometimes adds it) and lowercase, so we catch them regardless
    # of how the model formatted them in the two lists.
    def _norm(s: str) -> str:
        s = (s or "").strip()
        s = re.sub(r"^CRITICAL\s*[:\-]\s*", "", s, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", s.lower())

    critical_norms: set[str] = set()
    for t in rubric.get("critical_items", []) or []:
        critical_norms.add(_norm(t))
    # Also treat any rubric item whose text already starts with "CRITICAL:"
    # as critical — some models inline-flag items instead of using the list.
    for it in items:
        if re.match(r"^CRITICAL\s*[:\-]", it["text"], flags=re.IGNORECASE):
            critical_norms.add(_norm(it["text"]))

    items_text = "\n".join(
        f"{it['id']}. [{it['section']}] {it['text']}" for it in items
    )
    user_msg = (
        f"Scenario: {sc['title']}\n\n"
        f"Rubric items (numbered):\n{items_text}\n\n"
        f"Student transcript:\n\"\"\"\n{transcript.strip() or '(empty)'}\n\"\"\"\n\n"
        f"Return a JSON array with {len(items)} entries — one per rubric id — "
        f"in the format described in the system prompt."
    )

    try:
        resp = client.messages.create(
            model=llm_grader.MODEL,
            max_tokens=llm_grader.MAX_OUTPUT_TOKENS,
            system=GRADE_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as e:  # pragma: no cover
        log.warning("scenario grade API call failed: %s", e)
        return None

    try:
        text_parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
        raw = "\n".join(text_parts)
        grades = _parse_json_array(raw)
    except Exception as e:
        log.warning("scenario grade parse failed: %s", e)
        return None

    grade_map: dict[int, dict] = {}
    for g in grades:
        gid = g.get("id")
        if isinstance(gid, int):
            grade_map[gid] = g

    # Build report. Each rubric "section" becomes a top-level section with a
    # single "Steps" subsection so it renders with the same oral-practice UI.
    total = 0
    covered = 0
    critical_missed: list[dict] = []
    sec_reports: list[dict] = []
    flat_idx = 0
    for sec in rubric.get("sections", []):
        sec_total = 0
        sec_cov = 0
        item_reports: list[dict] = []
        for item in sec.get("items", []):
            g = grade_map.get(flat_idx, {})
            is_cov = bool(g.get("covered", False))
            reason = (g.get("reason") or "").strip()
            is_critical = _norm(item) in critical_norms
            # Display text: strip any redundant "CRITICAL: " prefix the model
            # added, since the UI tags critical items with a badge.
            display_text = re.sub(
                r"^CRITICAL\s*[:\-]\s*", "", item, flags=re.IGNORECASE
            )
            item_reports.append({
                "item": display_text,
                "covered": is_cov,
                "reason": reason,
                "coverage": 1.0 if is_cov else 0.0,
                "critical": is_critical,
                "keywords": [],
                "hits": [],
            })
            sec_total += 1
            if is_cov:
                sec_cov += 1
            elif is_critical:
                critical_missed.append({"section": sec["name"], "item": display_text})
            flat_idx += 1
        if sec_total == 0:
            continue
        sec_reports.append({
            "name": sec["name"],
            "total": sec_total,
            "covered": sec_cov,
            "score_pct": round(100 * sec_cov / sec_total, 1),
            "subsections": [
                {
                    "name": "Steps",
                    "total": sec_total,
                    "covered": sec_cov,
                    "score_pct": round(100 * sec_cov / sec_total, 1),
                    "items": item_reports,
                }
            ],
        })
        total += sec_total
        covered += sec_cov

    if total == 0:
        return None

    score_pct = round(100 * covered / total, 1)
    weakest = sorted(sec_reports, key=lambda s: s["score_pct"])[:5]
    return {
        "exam": {"slug": f"scenario:{scenario_id}", "title": sc["title"]},
        "score_pct": score_pct,
        "passing_threshold": 70.0,
        "passing": score_pct >= 70.0 and not critical_missed,
        "total_items": total,
        "covered_items": covered,
        "word_count": len(transcript.split()),
        "sections": sec_reports,
        "weakest_sections": [
            {"name": s["name"], "score_pct": s["score_pct"], "covered": s["covered"], "total": s["total"]}
            for s in weakest
        ],
        "critical_missed": critical_missed,
        "grader": "llm",
        "model": llm_grader.MODEL,
        "scenario": {
            "title": sc["title"],
            "body_system": sc["body_system"],
        },
    }
