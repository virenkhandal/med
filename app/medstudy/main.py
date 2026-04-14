from __future__ import annotations

import json
import os
import random
import re
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .questions import generate_quiz
from . import llm_grader
from . import scenarios

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "exams.json"
STATIC_DIR = ROOT / "static"

with DATA_FILE.open() as f:
    EXAMS: dict[str, dict] = json.load(f)


# --------- text utilities ----------

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "for", "in", "on", "with",
    "at", "by", "is", "are", "be", "as", "that", "this", "from", "into",
    "using", "use", "if", "it", "not", "no", "any", "each", "both", "all",
    "verbalize", "verbalizes", "verbalized", "verbalizing",
    "assess", "assesses", "perform", "performs",
    "ask", "asking", "check", "checks", "their", "your", "my", "you",
    "repeat", "compare", "bilaterally", "side", "would", "should", "may",
    "will", "have", "has", "then", "than", "other", "some", "while",
    "across", "between", "patients", "examiner", "patient",
}


def tokenize(text: str) -> list[str]:
    return [
        w
        for w in re.findall(r"[a-z][a-z0-9\-]+", text.lower())
        if w not in STOPWORDS and len(w) > 2
    ]


def keywords_from_item(item: str, min_len: int = 4) -> set[str]:
    return {w for w in tokenize(item) if len(w) >= min_len}


# --------- exam traversal helpers ----------

def iter_items(exam: dict) -> list[str]:
    out: list[str] = []
    for sec in exam.get("sections", []):
        for sub in sec.get("subsections", []):
            out.extend(sub.get("items", []))
    return out


# --------- FastAPI app ----------

app = FastAPI(title="Med Study")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/healthz")
def health():
    return {
        "ok": True,
        "exams": len(EXAMS),
        "whisper": _whisper_status(),
        "llm_grader": llm_grader.status(),
        "scenarios": scenarios.status(),
    }


@app.get("/api/exams")
def list_exams():
    return [
        {
            "slug": e["slug"],
            "title": e["title"],
            "item_count": e.get("item_count") or len(iter_items(e)),
            "section_count": len(e.get("sections", [])),
        }
        for e in EXAMS.values()
    ]


@app.get("/api/exam/{slug}")
def get_exam(slug: str):
    if slug not in EXAMS:
        raise HTTPException(404, "Exam not found")
    return EXAMS[slug]


# --------- quiz ----------

class QuizRequest(BaseModel):
    count: int = 10


@app.post("/api/exam/{slug}/quiz")
def make_quiz(slug: str, req: QuizRequest):
    if slug not in EXAMS:
        raise HTTPException(404, "Exam not found")
    exam = EXAMS[slug]
    n = max(1, min(req.count, 30))
    questions = generate_quiz(slug, exam, n)
    if not questions:
        raise HTTPException(400, "No questions could be generated for this exam")
    return {
        "exam": {"slug": exam["slug"], "title": exam["title"]},
        "questions": questions,
        "question_count": len(questions),
    }


# --------- scoring (section-aware) ----------

class ScoreRequest(BaseModel):
    transcript: str


def _score_item(item: str, transcript_tokens: set[str]) -> dict:
    kws = keywords_from_item(item)
    if not kws:
        return {"item": item, "keywords": [], "hits": [], "coverage": 0.0, "covered": False}
    hits = kws & transcript_tokens
    ratio = len(hits) / len(kws)
    return {
        "item": item,
        "keywords": sorted(kws),
        "hits": sorted(hits),
        "coverage": round(ratio, 2),
        "covered": ratio >= 0.5,
    }


def _keyword_score(exam: dict, transcript: str) -> dict:
    transcript_tokens = set(tokenize(transcript))
    total_items = 0
    total_covered = 0
    section_reports: list[dict] = []

    for sec in exam.get("sections", []):
        sec_total = 0
        sec_covered = 0
        sub_reports: list[dict] = []
        for sub in sec.get("subsections", []):
            item_reports: list[dict] = []
            sub_total = 0
            sub_covered = 0
            for item in sub.get("items", []):
                r = _score_item(item, transcript_tokens)
                if not r["keywords"]:
                    continue
                item_reports.append(r)
                sub_total += 1
                if r["covered"]:
                    sub_covered += 1
            if sub_total == 0:
                continue
            sub_reports.append({
                "name": sub["name"],
                "total": sub_total,
                "covered": sub_covered,
                "score_pct": round(100 * sub_covered / sub_total, 1),
                "items": item_reports,
            })
            sec_total += sub_total
            sec_covered += sub_covered
        if sec_total == 0:
            continue
        section_reports.append({
            "name": sec["name"],
            "total": sec_total,
            "covered": sec_covered,
            "score_pct": round(100 * sec_covered / sec_total, 1),
            "subsections": sub_reports,
        })
        total_items += sec_total
        total_covered += sec_covered

    score_pct = round(100 * total_covered / total_items, 1) if total_items else 0.0
    weakest = sorted(section_reports, key=lambda s: s["score_pct"])[:5]
    return {
        "exam": {"slug": exam["slug"], "title": exam["title"]},
        "score_pct": score_pct,
        "total_items": total_items,
        "covered_items": total_covered,
        "word_count": len(transcript.split()),
        "sections": section_reports,
        "weakest_sections": [
            {"name": s["name"], "score_pct": s["score_pct"], "covered": s["covered"], "total": s["total"]}
            for s in weakest
        ],
        "grader": "keyword",
    }


@app.post("/api/exam/{slug}/score")
def score_oral(slug: str, req: ScoreRequest):
    if slug not in EXAMS:
        raise HTTPException(404, "Exam not found")
    exam = EXAMS[slug]
    transcript = (req.transcript or "").strip()

    # Try the LLM grader first; fall back to keyword on any failure.
    report = llm_grader.llm_grade(exam, transcript)
    if report is None:
        report = _keyword_score(exam, transcript)
    return report


# --------- Whisper transcription ----------

_whisper_model = None
_whisper_error: str | None = None


def _whisper_status() -> dict:
    return {"loaded": _whisper_model is not None, "error": _whisper_error}


def _get_whisper():
    global _whisper_model, _whisper_error
    if _whisper_model is not None:
        return _whisper_model
    try:
        from faster_whisper import WhisperModel  # type: ignore

        model_name = os.environ.get("WHISPER_MODEL", "tiny.en")
        compute_type = os.environ.get("WHISPER_COMPUTE", "int8")
        _whisper_model = WhisperModel(model_name, device="cpu", compute_type=compute_type)
        _whisper_error = None
        return _whisper_model
    except Exception as e:  # pragma: no cover - environment-dependent
        _whisper_error = f"{type(e).__name__}: {e}"
        raise


# --------- Scenarios ----------

class ScenarioNewRequest(BaseModel):
    category: str = "any"


class ScenarioScoreRequest(BaseModel):
    transcript: str


@app.post("/api/scenarios/new")
def api_scenarios_new(req: ScenarioNewRequest):
    data = scenarios.generate(req.category)
    if data is None:
        raise HTTPException(503, "Scenario generator unavailable (check ANTHROPIC_API_KEY)")
    return data


@app.get("/api/scenarios/{scenario_id}")
def api_scenarios_get(scenario_id: str):
    data = scenarios.get(scenario_id)
    if data is None:
        raise HTTPException(404, "Scenario not found or expired")
    return data


@app.post("/api/scenarios/{scenario_id}/score")
def api_scenarios_score(scenario_id: str, req: ScenarioScoreRequest):
    report = scenarios.grade(scenario_id, req.transcript or "")
    if report is None:
        raise HTTPException(404, "Scenario not found, expired, or grader unavailable")
    return report


@app.post("/api/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """Accept an audio blob and return a transcript using faster-whisper.

    Uses WhisperModel with a small English-only model to stay fast on CPU.
    """
    try:
        model = _get_whisper()
    except Exception:
        raise HTTPException(503, f"Whisper not available: {_whisper_error}")

    # Save to a temp file — faster-whisper accepts a path or stream, but a real
    # file is most reliable across codecs (webm/opus, ogg, m4a, wav).
    suffix = Path(audio.filename or "audio.webm").suffix or ".webm"
    tmp_dir = Path(tempfile.gettempdir())
    tmp_path = tmp_dir / f"medstudy-{os.getpid()}-{random.randint(1000,9999)}{suffix}"
    try:
        contents = await audio.read()
        if not contents:
            raise HTTPException(400, "Empty audio payload")
        tmp_path.write_bytes(contents)

        segments, info = model.transcribe(
            str(tmp_path),
            language="en",
            vad_filter=True,
            beam_size=1,
        )
        parts: list[dict] = []
        full_text_parts: list[str] = []
        for seg in segments:
            parts.append({
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": seg.text.strip(),
            })
            full_text_parts.append(seg.text.strip())
        return {
            "text": " ".join(full_text_parts).strip(),
            "duration": round(info.duration, 2),
            "language": info.language,
            "segments": parts,
        }
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass


# --------- HTML pages ----------

def _escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _page(body: str, title: str = "Med Study") -> HTMLResponse:
    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/style.css">
</head><body>
<div class="aurora"></div>
<header class="header">
  <div class="container header-inner">
    <a href="/" class="brand">Med Study</a>
    <span class="tag">Physical Exam Checklists</span>
  </div>
</header>
<main class="container">{body}</main>
<footer class="footer"><small>Built for medical school study — private to Viren</small></footer>
</body></html>"""
    return HTMLResponse(html)


@app.get("/", response_class=HTMLResponse)
def landing():
    cards_parts: list[str] = []
    palette = ["lavender", "mint", "peach", "sky", "rose", "butter", "lilac"]
    for i, e in enumerate(EXAMS.values()):
        color = palette[i % len(palette)]
        item_count = e.get("item_count") or len(iter_items(e))
        sec_count = len(e.get("sections", []))
        cards_parts.append(
            f'<a class="card exam-card tint-{color}" href="/exam/{_escape(e["slug"])}">'
            f'<div class="card-ring"></div>'
            f'<h3>{_escape(e["title"])}</h3>'
            f'<p class="meta">{sec_count} sections · {item_count} steps</p>'
            f'</a>'
        )
    cards = "".join(cards_parts)
    body = f"""
    <section class="hero">
      <h1>Study hub</h1>
      <p class="sub">Quiz yourself on a checklist, recite an exam aloud, or run a full OSCE scenario.</p>
    </section>
    <a class="card scenario-hero tint-lilac" href="/scenarios">
      <div>
        <span class="q-tag">New</span>
        <h3>OSCE Scenarios</h3>
        <p>Get a randomly generated patient chart, then perform and record a focused physical exam. Graded against a scenario-specific rubric by Claude.</p>
      </div>
      <div class="scenario-hero-cta">Start →</div>
    </a>
    <h2 class="section-heading">Single-exam practice</h2>
    <section class="grid grid-cards">{cards}</section>
    """
    return _page(body, "Med Study")


@app.get("/scenarios", response_class=HTMLResponse)
def scenarios_page():
    cat_options = "".join(
        f'<option value="{_escape(slug)}">{_escape(label)}</option>'
        for slug, label in scenarios.CATEGORIES
    )
    body = f"""
    <a class="back" href="/">&larr; All modes</a>
    <section class="hero">
      <h1>OSCE Scenario</h1>
      <p class="sub">Click <b>Generate</b> to get a random DXM III patient chart. Read it, record yourself performing a focused physical exam, and submit for LLM grading.</p>
    </section>

    <div class="card controls-card" id="generateCard">
      <label class="control"><span>Category</span>
        <select id="category">{cat_options}</select>
      </label>
      <button id="generateBtn" class="btn primary">Generate scenario</button>
      <span id="genStatus" class="status"></span>
    </div>

    <section id="chartCard" class="card panel" style="display: none;">
      <div class="panel-head">
        <h3><span id="scenarioCategory"></span> — <span id="scenarioTitle"></span></h3>
        <button id="regenerateBtn" class="btn secondary" type="button">New scenario</button>
      </div>
      <div id="chart" class="patient-chart"></div>
    </section>

    <div class="card controls-card" id="recordCard" style="display: none;">
      <button id="startRec" class="btn primary">● Start recording</button>
      <button id="stopRec" class="btn secondary" disabled>Stop &amp; grade</button>
      <span id="recStatus" class="status"></span>
    </div>

    <section id="transcriptCard" class="card panel" style="display: none;">
      <h3>Transcript</h3>
      <div id="transcript" class="transcript">Your recitation will appear here after you stop recording…</div>
    </section>

    <div id="report"></div>
    <script src="/static/scenarios.js"></script>
    """
    return _page(body, "OSCE Scenarios — Med Study")


@app.get("/exam/{slug}", response_class=HTMLResponse)
def exam_modes(slug: str):
    if slug not in EXAMS:
        raise HTTPException(404, "Exam not found")
    exam = EXAMS[slug]
    item_count = exam.get("item_count") or len(iter_items(exam))
    sec_count = len(exam.get("sections", []))
    body = f"""
    <a class="back" href="/">&larr; All exams</a>
    <section class="hero">
      <h1>{_escape(exam['title'])}</h1>
      <p class="sub">{sec_count} sections · {item_count} checklist steps. Pick a mode.</p>
    </section>
    <section class="grid grid-modes">
      <a class="card mode-card tint-mint" href="/exam/{_escape(slug)}/quiz">
        <div class="mode-icon">★</div>
        <h3>Quiz</h3>
        <p>Randomized multiple-choice questions. Fresh each time.</p>
      </a>
      <a class="card mode-card tint-lavender" href="/exam/{_escape(slug)}/oral">
        <div class="mode-icon">✦</div>
        <h3>Oral practice</h3>
        <p>Recite the full exam aloud. Whisper transcribes and you get a scored report.</p>
      </a>
    </section>
    """
    return _page(body, f"{exam['title']} — Modes")


@app.get("/exam/{slug}/quiz", response_class=HTMLResponse)
def quiz_page(slug: str):
    if slug not in EXAMS:
        raise HTTPException(404, "Exam not found")
    exam = EXAMS[slug]
    body = f"""
    <a class="back" href="/exam/{_escape(slug)}">&larr; Back</a>
    <section class="hero">
      <h1>{_escape(exam['title'])} — Quiz</h1>
      <p class="sub">Randomized multiple-choice. Answer to reveal.</p>
    </section>
    <div class="card controls-card">
      <label class="control"><span>Questions</span><input id="count" type="number" value="10" min="1" max="30"></label>
      <button id="startBtn" class="btn primary">Start quiz</button>
    </div>
    <div id="quiz"></div>
    <script>window.EXAM_SLUG = {json.dumps(slug)};</script>
    <script src="/static/quiz.js"></script>
    """
    return _page(body, f"{exam['title']} — Quiz")


@app.get("/exam/{slug}/oral", response_class=HTMLResponse)
def oral_page(slug: str):
    if slug not in EXAMS:
        raise HTTPException(404, "Exam not found")
    exam = EXAMS[slug]
    # Build checklist HTML grouped by section
    sec_parts: list[str] = []
    for sec in exam.get("sections", []):
        sub_parts: list[str] = []
        for sub in sec.get("subsections", []):
            items_html = "".join(f"<li>{_escape(it)}</li>" for it in sub.get("items", []))
            sub_parts.append(
                f'<div class="sub-block"><h5>{_escape(sub["name"])}</h5>'
                f'<ul>{items_html}</ul></div>'
            )
        sec_parts.append(
            f'<div class="sec-block"><h4>{_escape(sec["name"])}</h4>'
            f'{"".join(sub_parts)}</div>'
        )
    checklist_html = "".join(sec_parts)
    body = f"""
    <a class="back" href="/exam/{_escape(slug)}">&larr; Back</a>
    <section class="hero">
      <h1>{_escape(exam['title'])} — Oral practice</h1>
      <p class="sub">Click <b>Start recording</b>, recite the entire exam aloud, then <b>Stop &amp; score</b>. Audio is transcribed on-server by Whisper.</p>
    </section>
    <div class="card controls-card">
      <button id="startRec" class="btn primary">● Start recording</button>
      <button id="stopRec" class="btn secondary" disabled>Stop &amp; score</button>
      <span id="recStatus" class="status"></span>
    </div>
    <section class="card panel transcript-panel">
      <h3>Transcript</h3>
      <div id="transcript" class="transcript">Recording will appear here after you stop…</div>
    </section>
    <section class="card panel checklist-panel">
      <div class="panel-head">
        <h3>Checklist</h3>
        <button id="toggleChecklist" class="icon-btn" type="button" aria-pressed="false" aria-label="Reveal checklist">
          <svg class="icon-eye" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path class="icon-eye-open" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/>
            <circle class="icon-eye-open" cx="12" cy="12" r="3"/>
            <path class="icon-eye-closed" d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a19.77 19.77 0 0 1 4.06-4.94M9.9 4.24A10.94 10.94 0 0 1 12 4c7 0 11 7 11 7a19.77 19.77 0 0 1-2.16 3.19M14.12 14.12A3 3 0 1 1 9.88 9.88"/>
            <line class="icon-eye-closed" x1="1" y1="1" x2="23" y2="23"/>
          </svg>
          <span class="toggle-label">Reveal</span>
        </button>
      </div>
      <div id="checklist" class="checklist checklist-hidden">{checklist_html}</div>
      <p class="checklist-placeholder">Checklist hidden — tap the eye if you get stuck.</p>
    </section>
    <div id="report"></div>
    <script>window.EXAM_SLUG = {json.dumps(slug)};</script>
    <script src="/static/oral.js"></script>
    """
    return _page(body, f"{exam['title']} — Oral")
