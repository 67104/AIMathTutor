"""Olympiad-style question generators (SOF: IMO / NSO / IEO / IGKO).

These are ORIGINAL, parametric questions written to match the *style, syllabus,
and difficulty* of SOF olympiad sections (Logical Reasoning + Mathematical
Reasoning). No past-paper content is reproduced (see docs/PROBLEMS.md #13).

Every generator returns:
    (prompt, correct, distractors, topic_code, topic_name, explanation)

``level`` (1 or 2) scales difficulty; ``grade`` lightly scales magnitudes.
"""

import random
from math import gcd

from app.core.question_gen import Question, _build_options


# --------------------------------------------------------------------------
# Mathematical reasoning
# --------------------------------------------------------------------------

def _number_series(level, grade):
    kind = random.choice(["arith", "geom", "square"])
    if kind == "arith":
        start = random.randint(2, 9)
        step = random.randint(2, 4 + level * 2)
        seq = [start + i * step for i in range(4)]
        nxt = seq[-1] + step
        why = f"The sequence increases by {step} each time."
    elif kind == "geom":
        start = random.randint(2, 3)
        ratio = random.randint(2, 2 + level)
        seq = [start * ratio ** i for i in range(4)]
        nxt = seq[-1] * ratio
        why = f"Each term is multiplied by {ratio}."
    else:
        base = random.randint(1 + level, 3 + level)
        seq = [(base + i) ** 2 for i in range(4)]
        nxt = (base + 4) ** 2
        why = f"The terms are perfect squares: {base}², {base+1}², ..."
    shown = ", ".join(str(x) for x in seq)
    return (f"Find the next term:  {shown}, ?", nxt,
            [nxt + seq[0], nxt - seq[0], nxt + 2],
            "olympiad.number_series", "Number Series", why)


def _lcm_hcf(level, grade):
    a = random.randint(4, 8 + level * 4)
    b = random.randint(4, 8 + level * 4)
    if random.random() < 0.5:
        ans = a * b // gcd(a, b)
        q = f"Find the LCM of {a} and {b}."
        why = f"LCM = (a×b)/HCF = ({a}×{b})/{gcd(a, b)} = {ans}."
    else:
        ans = gcd(a, b)
        q = f"Find the HCF of {a} and {b}."
        why = f"HCF is the largest number dividing both {a} and {b}, which is {ans}."
    return (q, ans, [ans + a, ans - 1 if ans > 1 else ans + 2, a + b],
            "olympiad.lcm_hcf", "LCM & HCF", why)


def _ratio(level, grade):
    parts_a = random.randint(2, 4)
    parts_b = random.randint(2, 5)
    unit = random.randint(3, 6 + level * 4)
    total = (parts_a + parts_b) * unit
    ans = parts_a * unit
    q = (f"{total} sweets are shared between two friends in the ratio "
         f"{parts_a}:{parts_b}. How many does the first friend get?")
    why = (f"Total parts = {parts_a}+{parts_b} = {parts_a + parts_b}. "
           f"One part = {total}/{parts_a + parts_b} = {unit}. "
           f"First friend = {parts_a}×{unit} = {ans}.")
    return (q, ans, [parts_b * unit, ans + unit, ans - unit],
            "olympiad.ratio", "Ratio & Proportion", why)


def _average(level, grade):
    n = random.randint(3, 3 + level)
    nums = [random.randint(2, 10 + level * 5) for _ in range(n - 1)]
    missing = random.randint(2, 12 + level * 5)
    # Bump the missing number so the total is divisible by n -> integer average.
    total = sum(nums) + missing
    missing += (n - total % n) % n
    total = sum(nums) + missing
    avg = total // n
    q = (f"The average of {n} numbers is {avg}. If {n - 1} of them are "
         f"{', '.join(map(str, nums))}, find the missing number.")
    why = (f"Sum of all = average × count = {avg}×{n} = {total}. "
           f"Missing = {total} − {sum(nums)} = {missing}.")
    return (q, missing, [missing + avg, abs(missing - avg) + 1, avg],
            "olympiad.average", "Averages", why)


def _percentage_word(level, grade):
    pct = random.choice([10, 20, 25, 50])
    # Choose base as a multiple of 100/gcd(pct,100) so pct% is an exact integer.
    step = 100 // gcd(pct, 100)
    base = step * random.randint(3, 8 + level * 4)
    result = base + base * pct // 100          # now exact
    q = f"A number increased by {pct}% becomes {result}. Find the number."
    why = (f"If x increased by {pct}% is {result}, then "
           f"x × (1 + {pct}/100) = {result}, so x = {base}.")
    return (q, base, [result, base + pct, base - step if base > step else base + step * 2],
            "olympiad.percentage", "Percentage (word)", why)


# --------------------------------------------------------------------------
# Logical reasoning
# --------------------------------------------------------------------------

def _odd_one_out(level, grade):
    squares = [x * x for x in range(2, 9)]
    chosen = random.sample(squares, 3)
    odd = random.choice([c + 1 for c in squares if c + 1 not in squares])
    options = chosen + [odd]
    random.shuffle(options)
    why = f"{chosen} are perfect squares; {odd} is not."
    # Here the "answer" is the odd number itself.
    return (f"Find the odd one out:  {', '.join(map(str, options))}", odd,
            [c for c in chosen], "logical.odd_one_out", "Odd One Out", why)


def _number_analogy(level, grade):
    a = random.randint(2, 5)
    power = random.choice([2, 3])
    b = random.randint(2, 6)
    label = "²" if power == 2 else "³"
    q = f"{a} : {a ** power} :: {b} : ?"
    ans = b ** power
    why = f"The pattern is n : n{label}. So {b} : {b}{label} = {ans}."
    return (q, ans, [b * power, ans + b, ans - b],
            "logical.analogy", "Number Analogy", why)


def _letter_coding(level, grade):
    shift = random.randint(1, 1 + level)
    word = random.choice(["CAT", "DOG", "SUN", "PEN", "BOX", "CUP"])
    def enc(w):
        return "".join(chr((ord(c) - 65 + shift) % 26 + 65) for c in w)
    sample = random.choice(["MAN", "TOP", "RED", "BIG"])
    q = (f"In a code, {word} is written as {enc(word)}. "
         f"How is {sample} written?")
    ans = enc(sample)
    why = f"Each letter moves {shift} place(s) forward in the alphabet."
    d = [enc(sample[::-1]), "".join(chr((ord(c) - 65 - shift) % 26 + 65) for c in sample),
         sample]
    return (q, ans, d, "logical.coding", "Coding-Decoding", why)


def _letter_series(level, grade):
    start = random.randint(0, 15)
    step = random.randint(1, 1 + level)
    letters = [chr(65 + (start + i * step) % 26) for i in range(4)]
    nxt = chr(65 + (start + 4 * step) % 26)
    why = f"Each letter advances by {step} position(s)."
    d = [chr(65 + (start + 5 * step) % 26),
         chr(65 + (start + 3 * step) % 26), letters[0]]
    return (f"Find the next letter:  {', '.join(letters)}, ?", nxt, d,
            "logical.letter_series", "Letter Series", why)


# --------------------------------------------------------------------------
# Exam configuration: which sections each SOF exam draws from.
# --------------------------------------------------------------------------

_MATH = [_number_series, _lcm_hcf, _ratio, _average, _percentage_word]
_LOGICAL = [_odd_one_out, _number_analogy, _letter_coding, _letter_series]

EXAMS = {
    "IMO": {"name": "Maths Olympiad", "pool": _MATH * 2 + _LOGICAL,
            "note": "Mathematical + Logical Reasoning."},
    "NSO": {"name": "Science Olympiad", "pool": _MATH + _LOGICAL,
            "note": "Math & logical-reasoning subset (science MCQs not auto-generated)."},
    "IEO": {"name": "English Olympiad", "pool": _LOGICAL * 2,
            "note": "Logical/verbal reasoning subset (English content is limited)."},
    "IGKO": {"name": "GK Olympiad", "pool": _LOGICAL + _MATH,
             "note": "Logical reasoning & aptitude (general-knowledge is limited)."},
}


def exam_note(exam):
    return EXAMS.get(exam, EXAMS["IMO"])["note"]


def generate(exam, level=1, grade=8):
    """Return a fresh Olympiad ``Question`` for the exam/level/grade."""
    cfg = EXAMS.get(exam, EXAMS["IMO"])
    gen = random.choice(cfg["pool"])
    prompt, correct, distractors, code, name, why = gen(int(level), int(grade or 8))
    return Question(
        prompt=prompt,
        answer=str(correct),
        options=_build_options(correct, distractors),
        topic_code=code,
        topic_name=name,
        difficulty=f"Level {level}",
        explanation=why,
    )
