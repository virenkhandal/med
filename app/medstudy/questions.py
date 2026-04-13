"""Question generators for the med-study quiz.

Every generator draws ONLY from knowledge.py, which in turn is PDF-faithful.
No outside clinical reasoning; if a fact isn't in a PDF, we don't quiz it.
"""

from __future__ import annotations

import random
import re
from typing import Callable, Optional

from .knowledge import (
    CRANIAL_NERVES,
    DERMATOMES,
    DTRS,
    KEY_FACTS,
    MYOTOMES,
    SPECIAL_TESTS,
)

Question = dict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _shuffled_choices(correct: str, distractors: list[str]) -> tuple[list[str], int]:
    """Return (choices, answer_index) with correct + 3 unique distractors shuffled."""
    pool = list({d for d in distractors if d and d != correct})
    if len(pool) < 3:
        raise ValueError("not enough distractors")
    chosen = random.sample(pool, 3)
    choices = [correct] + chosen
    random.shuffle(choices)
    return choices, choices.index(correct)


# ---------------------------------------------------------------------------
# Cranial nerve generators (Neurologic exam)
# ---------------------------------------------------------------------------


def _gen_cn_test_to_label(exam_slug: str) -> Optional[Question]:
    if exam_slug != "neurologic":
        return None
    cn = random.choice(CRANIAL_NERVES)
    test = random.choice(cn["tests"])
    distractors = [c["label"] for c in CRANIAL_NERVES if c["label"] != cn["label"]]
    try:
        choices, idx = _shuffled_choices(cn["label"], distractors)
    except ValueError:
        return None
    return {
        "type": "cn_test_to_label",
        "category": "Cranial nerves",
        "prompt": f"Per the Neuro PDF, which cranial nerve is tested by: \"{test}\"?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{cn['label']} — tests listed in the PDF: " + "; ".join(cn["tests"]) + ".",
    }


def _gen_cn_label_to_test(exam_slug: str) -> Optional[Question]:
    if exam_slug != "neurologic":
        return None
    cn = random.choice(CRANIAL_NERVES)
    correct = random.choice(cn["tests"])
    other_tests: list[str] = []
    for other in CRANIAL_NERVES:
        if other["label"] == cn["label"]:
            continue
        other_tests.extend(other["tests"])
    try:
        choices, idx = _shuffled_choices(correct, other_tests)
    except ValueError:
        return None
    return {
        "type": "cn_label_to_test",
        "category": "Cranial nerves",
        "prompt": f"Per the Neuro PDF, which maneuver is used to test {cn['label']}?",
        "choices": choices,
        "answer_index": idx,
        "explanation": None,
    }


# ---------------------------------------------------------------------------
# Dermatome generators (Neurologic)
# ---------------------------------------------------------------------------


def _gen_dermatome_level_to_area(exam_slug: str) -> Optional[Question]:
    if exam_slug != "neurologic":
        return None
    d = random.choice(DERMATOMES)
    distractors = [x["area"] for x in DERMATOMES if x["level"] != d["level"]]
    try:
        choices, idx = _shuffled_choices(d["area"], distractors)
    except ValueError:
        return None
    return {
        "type": "dermatome_level_to_area",
        "category": "Dermatomes",
        "prompt": f"Per the Neuro PDF, which body area corresponds to the {d['level']} dermatome?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{d['level']} → {d['area']} (from the Neuro checklist).",
    }


def _gen_dermatome_area_to_level(exam_slug: str) -> Optional[Question]:
    if exam_slug != "neurologic":
        return None
    d = random.choice(DERMATOMES)
    distractors = [x["level"] for x in DERMATOMES if x["level"] != d["level"]]
    try:
        choices, idx = _shuffled_choices(d["level"], distractors)
    except ValueError:
        return None
    return {
        "type": "dermatome_area_to_level",
        "category": "Dermatomes",
        "prompt": f"Per the Neuro PDF, sensation over the {d['area'].lower()} is tested at which dermatome level?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{d['area']} → {d['level']}.",
    }


# ---------------------------------------------------------------------------
# Myotome / DTR generators (Neurologic)
# ---------------------------------------------------------------------------


def _gen_myotome_action_to_roots(exam_slug: str) -> Optional[Question]:
    if exam_slug != "neurologic":
        return None
    m = random.choice(MYOTOMES)
    distractors = list({x["roots"] for x in MYOTOMES if x["roots"] != m["roots"]})
    try:
        choices, idx = _shuffled_choices(m["roots"], distractors)
    except ValueError:
        return None
    return {
        "type": "myotome_action_to_roots",
        "category": "Myotomes",
        "prompt": f"Per the Neuro PDF, which nerve root(s) are tested by {m['action'].lower()}?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{m['action']} → {m['roots']}.",
    }


def _gen_myotome_roots_to_action(exam_slug: str) -> Optional[Question]:
    if exam_slug != "neurologic":
        return None
    # Pick a root grouping that has exactly one unambiguous action
    groupings: dict[str, list[str]] = {}
    for m in MYOTOMES:
        groupings.setdefault(m["roots"], []).append(m["action"])
    unique_roots = [(r, acts) for r, acts in groupings.items() if len(acts) == 1]
    if not unique_roots:
        return None
    roots, acts = random.choice(unique_roots)
    correct = acts[0]
    distractors = [m["action"] for m in MYOTOMES if m["action"] != correct]
    try:
        choices, idx = _shuffled_choices(correct, distractors)
    except ValueError:
        return None
    return {
        "type": "myotome_roots_to_action",
        "category": "Myotomes",
        "prompt": f"Per the Neuro PDF, the nerve root grouping {roots} primarily mediates which action?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{roots} → {correct}.",
    }


def _gen_dtr_roots(exam_slug: str) -> Optional[Question]:
    if exam_slug != "neurologic":
        return None
    d = random.choice(DTRS)
    distractors = list({x["roots"] for x in DTRS if x["roots"] != d["roots"]})
    try:
        choices, idx = _shuffled_choices(d["roots"], distractors)
    except ValueError:
        return None
    return {
        "type": "dtr_roots",
        "category": "Deep tendon reflexes",
        "prompt": f"Per the Neuro PDF, the {d['name'].lower()} tests which nerve root(s)?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{d['name']} → {d['roots']}.",
    }


# ---------------------------------------------------------------------------
# Special-test generators (MSK exams + Neuro special tests)
# ---------------------------------------------------------------------------


def _exam_tests(slug: str) -> list[dict]:
    return [t for t in SPECIAL_TESTS if t["exam"] == slug]


def _gen_special_test_purpose(exam_slug: str) -> Optional[Question]:
    tests = _exam_tests(exam_slug)
    if len(tests) < 2:
        return None
    t = random.choice(tests)
    distractors = list({x["purpose"] for x in SPECIAL_TESTS if x["purpose"] != t["purpose"]})
    try:
        choices, idx = _shuffled_choices(t["purpose"], distractors)
    except ValueError:
        return None
    return {
        "type": "special_test_purpose",
        "category": "Special tests",
        "prompt": f"Per the PDF, the {t['name']} is used to assess:",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{t['name']} ({t['section']}) → {t['purpose']}.",
    }


def _gen_special_test_by_purpose(exam_slug: str) -> Optional[Question]:
    tests = _exam_tests(exam_slug)
    if len(tests) < 2:
        return None
    t = random.choice(tests)
    distractors = [x["name"] for x in SPECIAL_TESTS if x["name"] != t["name"]]
    try:
        choices, idx = _shuffled_choices(t["name"], distractors)
    except ValueError:
        return None
    return {
        "type": "special_test_by_purpose",
        "category": "Special tests",
        "prompt": f"Per the PDF, which special test is used to assess {t['purpose'].lower()}?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{t['name']} ({t['section']}).",
    }


def _gen_special_test_section(exam_slug: str) -> Optional[Question]:
    tests = _exam_tests(exam_slug)
    if len(tests) < 2:
        return None
    t = random.choice(tests)
    distractors = list({x["section"] for x in SPECIAL_TESTS if x["section"] != t["section"]})
    try:
        choices, idx = _shuffled_choices(t["section"], distractors)
    except ValueError:
        return None
    return {
        "type": "special_test_section",
        "category": "Special tests",
        "prompt": f"Per the PDF, the {t['name']} is performed under which part of the exam?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{t['name']} → {t['section']}.",
    }


# ---------------------------------------------------------------------------
# KEY_FACTS generator
# ---------------------------------------------------------------------------


def _gen_key_fact(exam_slug: str) -> Optional[Question]:
    facts = [f for f in KEY_FACTS if f["exam"] == exam_slug]
    if not facts:
        return None
    fact = random.choice(facts)
    try:
        choices, idx = _shuffled_choices(fact["answer"], list(fact["distractors"]))
    except ValueError:
        return None
    return {
        "type": "key_fact",
        "category": "Key facts",
        "prompt": fact["question"],
        "choices": choices,
        "answer_index": idx,
        "explanation": None,
    }


# ---------------------------------------------------------------------------
# Section-step generator (uses the parsed exam JSON at call time)
# ---------------------------------------------------------------------------


def _iter_subsections(exam: dict):
    for sec in exam.get("sections", []):
        for sub in sec.get("subsections", []):
            yield sec, sub


_STEP_OK_RE = re.compile(r"^[A-Z0-9(\"]")


def _ok_step(item: str) -> bool:
    if not (20 <= len(item) <= 180):
        return False
    if not _STEP_OK_RE.match(item):
        return False
    letters = sum(1 for c in item if c.isalpha())
    if letters < 12:
        return False
    return True


def _gen_step_to_subsection(exam_slug: str, exam: dict) -> Optional[Question]:
    subs_with_steps = []
    for sec, sub in _iter_subsections(exam):
        good = [it for it in sub.get("items", []) if _ok_step(it)]
        if good:
            subs_with_steps.append((sec, sub, good))
    if len(subs_with_steps) < 4:
        return None
    target_sec, target_sub, good_items = random.choice(subs_with_steps)
    step = random.choice(good_items)
    correct = f"{target_sub['name']} — {target_sec['name']}"
    other_names = [
        f"{sub['name']} — {sec['name']}"
        for sec, sub, _ in subs_with_steps
        if sub["name"] != target_sub["name"]
    ]
    try:
        choices, idx = _shuffled_choices(correct, list(set(other_names)))
    except ValueError:
        return None
    return {
        "type": "step_to_subsection",
        "category": "Section placement",
        "prompt": f"In the {exam['title']} exam, which section/subsection does this step belong to? — \"{step}\"",
        "choices": choices,
        "answer_index": idx,
        "explanation": None,
    }


def _gen_step_not_in_subsection(exam_slug: str, exam: dict) -> Optional[Question]:
    subs_with_steps = []
    for sec, sub in _iter_subsections(exam):
        good = [it for it in sub.get("items", []) if _ok_step(it)]
        if len(good) >= 3:
            subs_with_steps.append((sec, sub, good))
    if not subs_with_steps:
        return None
    sec, sub, good = random.choice(subs_with_steps)
    three = random.sample(good, 3)
    foreign_pool: list[str] = []
    for osec, osub in _iter_subsections(exam):
        if osub["name"] == sub["name"]:
            continue
        foreign_pool.extend(it for it in osub.get("items", []) if _ok_step(it))
    if not foreign_pool:
        return None
    foreign = random.choice(foreign_pool)
    while foreign in three and len(foreign_pool) > 1:
        foreign = random.choice(foreign_pool)
    choices = three + [foreign]
    random.shuffle(choices)
    return {
        "type": "step_not_in_subsection",
        "category": "Section placement",
        "prompt": f"In the {exam['title']} exam, which of the following is NOT part of \"{sub['name']}\" ({sec['name']})?",
        "choices": choices,
        "answer_index": choices.index(foreign),
        "explanation": None,
    }


# ---------------------------------------------------------------------------
# Generator registry — which generators apply to which exams
# ---------------------------------------------------------------------------

_SLUG_GENERATORS: dict[str, list[Callable[[str], Optional[Question]]]] = {
    "neurologic": [
        _gen_cn_test_to_label,
        _gen_cn_label_to_test,
        _gen_dermatome_level_to_area,
        _gen_dermatome_area_to_level,
        _gen_myotome_action_to_roots,
        _gen_myotome_roots_to_action,
        _gen_dtr_roots,
        _gen_special_test_purpose,
        _gen_special_test_by_purpose,
        _gen_key_fact,
    ],
    "lower-extremity-msk": [
        _gen_special_test_purpose,
        _gen_special_test_by_purpose,
        _gen_special_test_section,
        _gen_key_fact,
    ],
    "upper-extremity-msk": [
        _gen_special_test_purpose,
        _gen_special_test_by_purpose,
        _gen_special_test_section,
        _gen_key_fact,
    ],
    "spine-msk": [
        _gen_special_test_purpose,
        _gen_special_test_by_purpose,
        _gen_key_fact,
    ],
    "breast-axilla": [_gen_key_fact],
    "female-gu": [_gen_key_fact],
    "male-gu": [_gen_key_fact],
}

_EXAM_GENERATORS: list[Callable[[str, dict], Optional[Question]]] = [
    _gen_step_to_subsection,
    _gen_step_not_in_subsection,
]


def generate_quiz(exam_slug: str, exam: dict, count: int) -> list[Question]:
    slug_gens = list(_SLUG_GENERATORS.get(exam_slug, []))
    exam_gens = list(_EXAM_GENERATORS)

    questions: list[Question] = []
    seen_prompts: set[str] = set()
    attempts = 0
    max_attempts = count * 15

    while len(questions) < count and attempts < max_attempts:
        attempts += 1
        gen_pool = slug_gens + exam_gens
        if not gen_pool:
            break
        gen = random.choice(gen_pool)
        try:
            if gen in exam_gens:
                q = gen(exam_slug, exam)  # type: ignore[arg-type]
            else:
                q = gen(exam_slug)  # type: ignore[arg-type]
        except Exception:
            q = None
        if not q:
            continue
        if q["prompt"] in seen_prompts:
            continue
        if not q.get("choices") or len(q["choices"]) != 4:
            continue
        if len(set(q["choices"])) != 4:
            continue
        if not (0 <= q["answer_index"] < 4):
            continue
        seen_prompts.add(q["prompt"])
        q["id"] = len(questions)
        questions.append(q)

    return questions
