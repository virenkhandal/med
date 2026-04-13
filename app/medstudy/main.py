from __future__ import annotations

import json
import random
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "exams.json"
STATIC_DIR = ROOT / "static"

with DATA_FILE.open() as f:
    EXAMS: dict[str, dict] = json.load(f)

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "for", "in", "on", "with",
    "at", "by", "is", "are", "be", "as", "that", "this", "from", "into",
    "using", "use", "if", "it", "not", "no", "any", "each", "both", "all",
    "patient", "verbalize", "assess", "assesses", "perform", "performs",
    "ask", "asking", "check", "checks", "their", "your", "my", "you",
    "repeat", "compare", "bilaterally", "side", "would", "should", "may",
    "will", "have", "has", "then", "than", "other", "some", "while",
    "across", "between", "while", "patients", "examiner",
}


def tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z][a-z0-9\-]+", text.lower()) if w not in STOPWORDS and len(w) > 2]


def keywords_from_item(item: str, min_len: int = 4) -> set[str]:
    return {w for w in tokenize(item) if len(w) >= min_len}


app = FastAPI(title="Med Study")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/healthz")
def health():
    return {"ok": True, "exams": len(EXAMS)}


@app.get("/api/exams")
def list_exams():
    return [
        {"slug": e["slug"], "title": e["title"], "item_count": len(e["items"])}
        for e in EXAMS.values()
    ]


@app.get("/api/exam/{slug}")
def get_exam(slug: str):
    if slug not in EXAMS:
        raise HTTPException(404, "Exam not found")
    return EXAMS[slug]


class QuizRequest(BaseModel):
    count: int = 10


@app.post("/api/exam/{slug}/quiz")
def make_quiz(slug: str, req: QuizRequest):
    if slug not in EXAMS:
        raise HTTPException(404, "Exam not found")
    exam = EXAMS[slug]
    target_items = [i for i in exam["items"] if 15 <= len(i) <= 220]
    other_items: list[str] = []
    for other_slug, other_exam in EXAMS.items():
        if other_slug == slug:
            continue
        other_items.extend(i for i in other_exam["items"] if 15 <= len(i) <= 220)

    if len(target_items) < 4 or len(other_items) < 3:
        raise HTTPException(400, "Not enough items for quiz")

    n = max(1, min(req.count, len(target_items)))
    chosen_correct = random.sample(target_items, k=n)

    questions = []
    for idx, correct in enumerate(chosen_correct):
        # type A: "Which is a step in this exam?" — correct from target, distractors from other exams
        # type B: "Which is NOT a step in this exam?" — 3 target, 1 other
        q_type = random.choice(["belongs", "not_belongs"])
        if q_type == "belongs":
            distractors = random.sample(other_items, k=3)
            choices = [correct] + distractors
            random.shuffle(choices)
            questions.append({
                "id": idx,
                "type": "belongs",
                "prompt": f"Which of the following is a step in the {exam['title']} exam?",
                "choices": choices,
                "answer_index": choices.index(correct),
            })
        else:
            # pick 3 target items different from "correct" + 1 foreign item (the wrong answer)
            pool = [i for i in target_items if i != correct]
            if len(pool) < 3:
                distractors = random.sample(other_items, k=3)
                choices = [correct] + distractors
                random.shuffle(choices)
                questions.append({
                    "id": idx,
                    "type": "belongs",
                    "prompt": f"Which of the following is a step in the {exam['title']} exam?",
                    "choices": choices,
                    "answer_index": choices.index(correct),
                })
            else:
                valid_three = random.sample(pool, k=3)
                foreign = random.choice(other_items)
                choices = valid_three + [foreign]
                random.shuffle(choices)
                questions.append({
                    "id": idx,
                    "type": "not_belongs",
                    "prompt": f"Which of the following is NOT a step in the {exam['title']} exam?",
                    "choices": choices,
                    "answer_index": choices.index(foreign),
                })
    return {"exam": {"slug": exam["slug"], "title": exam["title"]}, "questions": questions}


class ScoreRequest(BaseModel):
    transcript: str


@app.post("/api/exam/{slug}/score")
def score_oral(slug: str, req: ScoreRequest):
    if slug not in EXAMS:
        raise HTTPException(404, "Exam not found")
    exam = EXAMS[slug]
    transcript = req.transcript or ""
    transcript_tokens = set(tokenize(transcript))

    results = []
    covered = 0
    for item in exam["items"]:
        kws = keywords_from_item(item)
        if not kws:
            continue
        hits = kws & transcript_tokens
        ratio = len(hits) / len(kws) if kws else 0
        is_covered = ratio >= 0.5
        if is_covered:
            covered += 1
        results.append({
            "item": item,
            "keywords": sorted(kws),
            "hits": sorted(hits),
            "coverage": round(ratio, 2),
            "covered": is_covered,
        })

    total = len(results)
    score = round(100 * covered / total, 1) if total else 0
    missed = [r for r in results if not r["covered"]]
    return {
        "exam": {"slug": exam["slug"], "title": exam["title"]},
        "total_items": total,
        "covered_items": covered,
        "score_pct": score,
        "word_count": len(transcript.split()),
        "missed": missed[:50],
        "results": results,
    }


# ---------- HTML pages ----------

def _page(body: str, title: str = "Med Study") -> HTMLResponse:
    html = f"""<!DOCTYPE html>
<html lang=\"en\"><head>
<meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>{title}</title>
<link rel=\"stylesheet\" href=\"/static/style.css\">
</head><body>
<header><a href=\"/\" class=\"brand\">Med Study</a></header>
<main>{body}</main>
<footer><small>PE checklists study tool — built for Viren</small></footer>
</body></html>"""
    return HTMLResponse(html)


@app.get("/", response_class=HTMLResponse)
def landing():
    cards = "".join(
        f'<a class="card" href="/exam/{e["slug"]}"><h3>{e["title"]}</h3>'
        f'<p>{len(e["items"])} checklist items</p></a>'
        for e in EXAMS.values()
    )
    body = f"""
    <h1>Choose an exam</h1>
    <p class="sub">Pick a physical exam checklist to study. Then choose quiz or oral practice.</p>
    <div class="grid">{cards}</div>
    """
    return _page(body, "Med Study — Pick an Exam")


@app.get("/exam/{slug}", response_class=HTMLResponse)
def exam_modes(slug: str):
    if slug not in EXAMS:
        raise HTTPException(404, "Exam not found")
    exam = EXAMS[slug]
    body = f"""
    <a class="back" href="/">&larr; All exams</a>
    <h1>{exam['title']}</h1>
    <p class="sub">{len(exam['items'])} checklist items. Pick a mode.</p>
    <div class="grid">
      <a class="card mode" href="/exam/{slug}/quiz">
        <h3>Quiz</h3>
        <p>Randomized multiple-choice questions. Fresh each time.</p>
      </a>
      <a class="card mode" href="/exam/{slug}/oral">
        <h3>Oral practice</h3>
        <p>Recite the full exam aloud. Get a scored report on what you hit and missed.</p>
      </a>
    </div>
    """
    return _page(body, f"{exam['title']} — Modes")


@app.get("/exam/{slug}/quiz", response_class=HTMLResponse)
def quiz_page(slug: str):
    if slug not in EXAMS:
        raise HTTPException(404, "Exam not found")
    exam = EXAMS[slug]
    body = f"""
    <a class="back" href="/exam/{slug}">&larr; Back</a>
    <h1>{exam['title']} — Quiz</h1>
    <div class="controls">
      <label>Questions: <input id="count" type="number" value="10" min="1" max="30"></label>
      <button id="startBtn">Start quiz</button>
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
    items_html = "".join(f"<li>{_escape(i)}</li>" for i in exam["items"])
    body = f"""
    <a class="back" href="/exam/{slug}">&larr; Back</a>
    <h1>{exam['title']} — Oral practice</h1>
    <p class="sub">Click <b>Start recording</b> and recite the full exam aloud. When done, click <b>Stop &amp; score</b>. Uses your browser's built-in speech recognition (Chrome/Safari/Edge).</p>
    <div class="oral-controls">
      <button id="startRec">Start recording</button>
      <button id="stopRec" disabled>Stop &amp; score</button>
      <span id="recStatus" class="status"></span>
    </div>
    <div class="two-col">
      <section>
        <h3>Live transcript</h3>
        <div id="transcript" class="transcript"></div>
      </section>
      <section>
        <h3>Checklist reference</h3>
        <ol class="checklist">{items_html}</ol>
      </section>
    </div>
    <div id="report"></div>
    <script>window.EXAM_SLUG = {json.dumps(slug)};</script>
    <script src="/static/oral.js"></script>
    """
    return _page(body, f"{exam['title']} — Oral")


def _escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
