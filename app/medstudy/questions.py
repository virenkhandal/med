"""Question generators that turn the knowledge base into quiz questions.

Each generator takes a random seed / state and returns either a question dict
or None (if no question can be produced for the given exam). The quiz endpoint
calls generators until it has enough questions.

Question dict shape:
    {
        "type": str,             # e.g. "cn_test_to_number"
        "category": str,         # human-readable ("Cranial nerves")
        "prompt": str,           # the question text
        "choices": [str, ...],   # 4 unique choices
        "answer_index": int,     # index of correct answer in choices
        "explanation": str | None,
    }
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
    """Return (choices, answer_index) with correct + 3 unique distractors shuffled.

    If not enough unique distractors, raises ValueError.
    """
    pool = list({d for d in distractors if d and d != correct})
    if len(pool) < 3:
        raise ValueError("not enough distractors")
    chosen = random.sample(pool, 3)
    choices = [correct] + chosen
    random.shuffle(choices)
    return choices, choices.index(correct)


def _pick_unique(items: list, key: Callable, exclude: set, n: int) -> list:
    """Pick up to n items whose key() is not in `exclude` and is unique among picks."""
    random.shuffle(items)
    out = []
    seen = set()
    for it in items:
        k = key(it)
        if k in exclude or k in seen:
            continue
        out.append(it)
        seen.add(k)
        if len(out) >= n:
            break
    return out


# ---------------------------------------------------------------------------
# Cranial nerve generators (Neurologic exam)
# ---------------------------------------------------------------------------


def _cn_label(cn: dict) -> str:
    return f"CN {cn['num']} — {cn['name']}"


def _gen_cn_test_to_number(exam_slug: str) -> Optional[Question]:
    if exam_slug != "neurologic":
        return None
    cn = random.choice(CRANIAL_NERVES)
    test = random.choice(cn["tests"])
    correct = _cn_label(cn)
    distractors = [_cn_label(c) for c in CRANIAL_NERVES if c["num"] != cn["num"]]
    try:
        choices, idx = _shuffled_choices(correct, distractors)
    except ValueError:
        return None
    return {
        "type": "cn_test_to_number",
        "category": "Cranial nerves",
        "prompt": f"Which cranial nerve is being tested by the following maneuver? — \"{test}\"",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{correct} ({cn['kind']}): {'; '.join(cn['tests'])}.",
    }


def _gen_cn_number_to_test(exam_slug: str) -> Optional[Question]:
    if exam_slug != "neurologic":
        return None
    cn = random.choice(CRANIAL_NERVES)
    correct = random.choice(cn["tests"])
    # Distractors: tests from OTHER cranial nerves.
    other_tests: list[str] = []
    for other in CRANIAL_NERVES:
        if other["num"] == cn["num"]:
            continue
        other_tests.extend(other["tests"])
    try:
        choices, idx = _shuffled_choices(correct, other_tests)
    except ValueError:
        return None
    return {
        "type": "cn_number_to_test",
        "category": "Cranial nerves",
        "prompt": f"Which maneuver correctly tests {_cn_label(cn)}?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{_cn_label(cn)} is {cn['kind']}; abnormal findings include {cn['finding']}.",
    }


def _gen_cn_kind(exam_slug: str) -> Optional[Question]:
    if exam_slug != "neurologic":
        return None
    cn = random.choice(CRANIAL_NERVES)
    kind_map = {"sensory": "Purely sensory", "motor": "Purely motor", "both": "Both sensory and motor"}
    correct = kind_map[cn["kind"]]
    distractors = [v for k, v in kind_map.items() if v != correct]
    distractors.append("Purely autonomic")
    try:
        choices, idx = _shuffled_choices(correct, distractors)
    except ValueError:
        return None
    return {
        "type": "cn_kind",
        "category": "Cranial nerves",
        "prompt": f"{_cn_label(cn)} is classified as:",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{_cn_label(cn)} is {cn['kind']}.",
    }


# ---------------------------------------------------------------------------
# Dermatome generators (Neurologic)
# ---------------------------------------------------------------------------


def _gen_dermatome_level_to_area(exam_slug: str) -> Optional[Question]:
    if exam_slug != "neurologic":
        return None
    d = random.choice(DERMATOMES)
    correct = d["area"]
    distractors = [x["area"] for x in DERMATOMES if x["level"] != d["level"]]
    try:
        choices, idx = _shuffled_choices(correct, distractors)
    except ValueError:
        return None
    return {
        "type": "dermatome_level_to_area",
        "category": "Dermatomes",
        "prompt": f"Which body area corresponds to the {d['level']} dermatome?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{d['level']} → {d['area']}.",
    }


def _gen_dermatome_area_to_level(exam_slug: str) -> Optional[Question]:
    if exam_slug != "neurologic":
        return None
    d = random.choice(DERMATOMES)
    correct = d["level"]
    distractors = [x["level"] for x in DERMATOMES if x["level"] != d["level"]]
    try:
        choices, idx = _shuffled_choices(correct, distractors)
    except ValueError:
        return None
    return {
        "type": "dermatome_area_to_level",
        "category": "Dermatomes",
        "prompt": f"Sensation over the {d['area'].lower()} is tested at which dermatome level?",
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
    correct = m["roots"]
    distractors = list({x["roots"] for x in MYOTOMES if x["roots"] != m["roots"]})
    try:
        choices, idx = _shuffled_choices(correct, distractors)
    except ValueError:
        return None
    return {
        "type": "myotome_action_to_roots",
        "category": "Myotomes",
        "prompt": f"Which nerve root(s) are primarily tested by {m['action'].lower()}?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{m['action']} — {m['muscle']} — {m['roots']}.",
    }


def _gen_myotome_roots_to_action(exam_slug: str) -> Optional[Question]:
    if exam_slug != "neurologic":
        return None
    m = random.choice(MYOTOMES)
    correct = m["action"]
    distractors = list({x["action"] for x in MYOTOMES if x["action"] != m["action"]})
    try:
        choices, idx = _shuffled_choices(correct, distractors)
    except ValueError:
        return None
    return {
        "type": "myotome_roots_to_action",
        "category": "Myotomes",
        "prompt": f"Which muscle action is primarily mediated by the {m['roots']} nerve root(s)?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{m['roots']} — {m['muscle']} — {m['action']}.",
    }


def _gen_dtr_roots(exam_slug: str) -> Optional[Question]:
    if exam_slug != "neurologic":
        return None
    d = random.choice(DTRS)
    correct = d["roots"]
    distractors = list({x["roots"] for x in DTRS if x["roots"] != d["roots"]})
    # Add non-DTR roots as plausible distractors
    distractors.extend(["C4, C5", "L4, L5", "C7, C8", "T12, L1"])
    try:
        choices, idx = _shuffled_choices(correct, distractors)
    except ValueError:
        return None
    return {
        "type": "dtr_roots",
        "category": "Deep tendon reflexes",
        "prompt": f"The {d['name'].lower()} tests which nerve root(s)?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{d['name']} → {d['roots']}.",
    }


# ---------------------------------------------------------------------------
# Special-test generators (MSK exams)
# ---------------------------------------------------------------------------


def _exam_tests(slug: str) -> list[dict]:
    return [t for t in SPECIAL_TESTS if t["exam"] == slug]


def _gen_special_test_purpose(exam_slug: str) -> Optional[Question]:
    tests = _exam_tests(exam_slug)
    if len(tests) < 4:
        # Fall back to cross-MSK pool so upper/lower/spine can still produce questions.
        tests = SPECIAL_TESTS
    t = random.choice(tests)
    if t["exam"] != exam_slug and random.random() > 0.3:
        # Prefer exam-specific tests when possible
        in_exam = _exam_tests(exam_slug)
        if in_exam:
            t = random.choice(in_exam)
    correct = t["assesses"]
    distractors = list({x["assesses"] for x in SPECIAL_TESTS if x["assesses"] != t["assesses"]})
    try:
        choices, idx = _shuffled_choices(correct, distractors)
    except ValueError:
        return None
    return {
        "type": "special_test_purpose",
        "category": "Special tests",
        "prompt": f"The {t['name']} evaluates which injury or condition?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{t['name']} ({t['joint']}) — {t['technique']}. Assesses: {t['assesses']}.",
    }


def _gen_special_test_by_purpose(exam_slug: str) -> Optional[Question]:
    tests = _exam_tests(exam_slug)
    if len(tests) < 4:
        tests = SPECIAL_TESTS
    t = random.choice(tests)
    correct = t["name"]
    distractors = [x["name"] for x in SPECIAL_TESTS if x["name"] != t["name"]]
    try:
        choices, idx = _shuffled_choices(correct, distractors)
    except ValueError:
        return None
    return {
        "type": "special_test_by_purpose",
        "category": "Special tests",
        "prompt": f"Which special test is used to assess {t['assesses'].lower()}?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{t['name']} — {t['technique']}.",
    }


def _gen_special_test_joint(exam_slug: str) -> Optional[Question]:
    tests = _exam_tests(exam_slug)
    if len(tests) < 4:
        tests = SPECIAL_TESTS
    t = random.choice(tests)
    correct = t["joint"]
    distractors = list({x["joint"] for x in SPECIAL_TESTS if x["joint"] != t["joint"]})
    # Add plausible anatomic distractors
    distractors.extend(["Foot", "Cervical spine", "Thumb"])
    try:
        choices, idx = _shuffled_choices(correct, distractors)
    except ValueError:
        return None
    return {
        "type": "special_test_joint",
        "category": "Special tests",
        "prompt": f"The {t['name']} is performed as part of which joint exam?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{t['name']} → {t['joint']}. {t['technique']}.",
    }


def _gen_special_test_technique(exam_slug: str) -> Optional[Question]:
    tests = _exam_tests(exam_slug)
    if len(tests) < 4:
        tests = SPECIAL_TESTS
    t = random.choice(tests)
    correct = t["technique"]
    distractors = [x["technique"] for x in SPECIAL_TESTS if x["technique"] != t["technique"]]
    try:
        choices, idx = _shuffled_choices(correct, distractors)
    except ValueError:
        return None
    return {
        "type": "special_test_technique",
        "category": "Special tests",
        "prompt": f"How is the {t['name']} performed?",
        "choices": choices,
        "answer_index": idx,
        "explanation": f"{t['name']} — assesses {t['assesses']}.",
    }


# ---------------------------------------------------------------------------
# KEY_FACTS generator (all exams)
# ---------------------------------------------------------------------------


def _gen_key_fact(exam_slug: str) -> Optional[Question]:
    facts = [f for f in KEY_FACTS if f["exam"] == exam_slug]
    if not facts:
        return None
    fact = random.choice(facts)
    distractors = list(fact["distractors"])
    if len(distractors) < 3:
        return None
    try:
        choices, idx = _shuffled_choices(fact["answer"], distractors)
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
    """Filter out obvious PDF-extraction fragments so we only quiz clean items."""
    if not (20 <= len(item) <= 180):
        return False
    if not _STEP_OK_RE.match(item):
        return False
    # Must be mostly alphabetic
    letters = sum(1 for c in item if c.isalpha())
    if letters < 12:
        return False
    return True


def _gen_step_to_subsection(exam_slug: str, exam: dict) -> Optional[Question]:
    """'Which subsection does this step belong to?' — requires multiple real subsections."""
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
    """'Which of these is NOT part of subsection X?' — 3 target items + 1 foreign."""
    subs_with_steps = []
    for sec, sub in _iter_subsections(exam):
        good = [it for it in sub.get("items", []) if _ok_step(it)]
        if len(good) >= 3:
            subs_with_steps.append((sec, sub, good))
    if not subs_with_steps:
        return None
    sec, sub, good = random.choice(subs_with_steps)
    three = random.sample(good, 3)
    # Distractor: item from another subsection in the same exam.
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

# Generators that take only the exam slug
_SLUG_GENERATORS: dict[str, list[Callable[[str], Optional[Question]]]] = {
    "neurologic": [
        _gen_cn_test_to_number,
        _gen_cn_number_to_test,
        _gen_cn_kind,
        _gen_dermatome_level_to_area,
        _gen_dermatome_area_to_level,
        _gen_myotome_action_to_roots,
        _gen_myotome_roots_to_action,
        _gen_dtr_roots,
        _gen_key_fact,
    ],
    "lower-extremity-msk": [
        _gen_special_test_purpose,
        _gen_special_test_by_purpose,
        _gen_special_test_joint,
        _gen_special_test_technique,
        _gen_key_fact,
    ],
    "upper-extremity-msk": [
        _gen_special_test_purpose,
        _gen_special_test_by_purpose,
        _gen_special_test_joint,
        _gen_special_test_technique,
        _gen_key_fact,
    ],
    "spine-msk": [
        _gen_special_test_purpose,
        _gen_special_test_by_purpose,
        _gen_special_test_joint,
        _gen_key_fact,
    ],
    "breast-axilla": [_gen_key_fact],
    "female-gu": [_gen_key_fact],
    "male-gu": [_gen_key_fact],
}

# Generators that also receive the parsed exam dict
_EXAM_GENERATORS: list[Callable[[str, dict], Optional[Question]]] = [
    _gen_step_to_subsection,
    _gen_step_not_in_subsection,
]


def generate_quiz(exam_slug: str, exam: dict, count: int) -> list[Question]:
    """Generate a mixed quiz of `count` questions for the given exam.

    Tries each generator; if a generator fails (returns None or raises), it's
    skipped. Loops until enough unique prompts are collected or attempts max out.
    """
    slug_gens = list(_SLUG_GENERATORS.get(exam_slug, []))
    exam_gens = list(_EXAM_GENERATORS)

    questions: list[Question] = []
    seen_prompts: set[str] = set()
    attempts = 0
    max_attempts = count * 12

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
        # Deduplicate by prompt text
        if q["prompt"] in seen_prompts:
            continue
        # Validate shape
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
