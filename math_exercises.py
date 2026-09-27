import random
import json
import os
import streamlit as st

st.set_page_config(page_title="English and Math - 4ª Classe", page_icon="📚", layout="centered")

# ---------------------------------------------------------
# CONFIG: change these to your real numbers
# ---------------------------------------------------------
EXPRESS_NUMBER = "923 030 010"
WHATSAPP_NUMBER = "244923030010"  # international format, no + or spaces, for wa.me links
PRICE_KZ = "5.000"
USED_CODES_FILE = "used_codes.json"


# =========================================================
# MATH EXERCISE GENERATORS (Grade 4 level)
# Each generator receives a "used" set and must return None
# if it can't produce a fresh (non-repeated) exercise, so the
# caller can try again / pick another type.
# =========================================================

def gen_round(dif, used):
    for _ in range(20):
        n = random.randint(100, 9999)
        place = random.choice([10, 100, 1000])
        key = ("round", n, place)
        if key in used:
            continue
        used.add(key)
        answer = int(round(n / place) * place)
        place_name = "ten" if place == 10 else "hundred" if place == 100 else "thousand"
        return {
            "type": "round", "subject": "math",
            "text": f"Round {n} to the nearest {place_name}:",
            "answer": str(answer),
        }
    return None


def gen_expand(dif, used):
    lo, hi = {1: (100, 999), 2: (1000, 9999), 3: (10000, 99999)}[dif]
    for _ in range(20):
        n = random.randint(lo, hi)
        if ("expand", n) in used:
            continue
        used.add(("expand", n))
        digits = [int(d) for d in str(n)]
        length = len(digits)
        parts = [d * (10 ** (length - i - 1)) for i, d in enumerate(digits) if d != 0]
        return {
            "type": "expand", "subject": "math",
            "text": f'Write {n} in expanded form (use " + " between parts, e.g. 300 + 40 + 2):',
            "answer": " + ".join(str(p) for p in parts),
        }
    return None


def gen_mult(dif, used):
    for _ in range(30):
        a, b = random.randint(2, 9), random.randint(2, 9)
        key = ("mult", tuple(sorted((a, b))))
        if key in used:
            continue
        used.add(key)
        return {"type": "mult", "subject": "math", "text": f"{a} × {b} =", "answer": str(a * b)}
    return None


def gen_div(dif, used):
    for _ in range(30):
        b = random.randint(2, 9)
        result = random.randint(2, 9)
        a = b * result
        key = ("div", a, b)
        if key in used:
            continue
        used.add(key)
        return {"type": "div", "subject": "math", "text": f"{a} ÷ {b} =", "answer": str(result)}
    return None


def gen_add(dif, used):
    for _ in range(30):
        a, b = random.randint(10, 99), random.randint(10, 99)
        key = ("add", tuple(sorted((a, b))))
        if key in used:
            continue
        used.add(key)
        return {"type": "add", "subject": "math", "text": f"{a} + {b} =", "answer": str(a + b)}
    return None


def gen_sub(dif, used):
    for _ in range(30):
        a = random.randint(10, 99)
        b = random.randint(10, a)
        key = ("sub", a, b)
        if key in used:
            continue
        used.add(key)
        return {"type": "sub", "subject": "math", "text": f"{a} − {b} =", "answer": str(a - b)}
    return None


def gen_compare(dif, used):
    for _ in range(30):
        a, b = random.randint(1, 999), random.randint(1, 999)
        if a == b:
            continue
        key = ("compare", tuple(sorted((a, b))))
        if key in used:
            continue
        used.add(key)
        answer = ">" if a > b else "<"
        return {
            "type": "compare", "subject": "math",
            "text": f"Compare using > or <: {a}  _  {b}",
            "answer": answer,
        }
    return None


def gen_double_half(dif, used):
    for _ in range(30):
        op = random.choice(["double", "half"])
        if op == "double":
            n = random.randint(2, 500)
            key = ("double", n)
            if key in used:
                continue
            used.add(key)
            return {
                "type": "double_half", "subject": "math",
                "text": f"What is the double of {n}?",
                "answer": str(n * 2),
            }
        else:
            n = random.randint(1, 250) * 2
            key = ("half", n)
            if key in used:
                continue
            used.add(key)
            return {
                "type": "double_half", "subject": "math",
                "text": f"What is half of {n}?",
                "answer": str(n // 2),
            }
    return None


def gen_money(dif, used):
    for _ in range(30):
        a = random.randint(1, 20) * 50
        b = random.randint(1, 20) * 50
        key = ("money", tuple(sorted((a, b))))
        if key in used:
            continue
        used.add(key)
        return {
            "type": "money", "subject": "math",
            "text": f"You have {a} Kz and buy something for {b} Kz. How much do you have left (or need)? Answer only the number:",
            "answer": str(a - b),
        }
    return None


MATH_GENERATORS = {
    "round": ("Round numbers", gen_round),
    "expand": ("Expanded form", gen_expand),
    "mult": ("Multiplication", gen_mult),
    "div": ("Division", gen_div),
    "add": ("Addition", gen_add),
    "sub": ("Subtraction", gen_sub),
    "compare": ("Compare (> / <)", gen_compare),
    "double_half": ("Doubles and halves", gen_double_half),
    "money": ("Money problems", gen_money),
}


# =========================================================
# ENGLISH EXERCISE GENERATORS (Grade 4 level)
# =========================================================

VOCAB = [
    ("house", "casa"), ("dog", "cachorro"), ("cat", "gato"), ("book", "livro"),
    ("water", "água"), ("friend", "amigo"), ("school", "escola"), ("teacher", "professor"),
    ("family", "família"), ("table", "mesa"), ("chair", "cadeira"), ("window", "janela"),
    ("sun", "sol"), ("moon", "lua"), ("mother", "mãe"), ("father", "pai"),
    ("food", "comida"), ("tree", "árvore"), ("bird", "pássaro"), ("shoe", "sapato"),
    ("river", "rio"), ("mountain", "montanha"), ("city", "cidade"), ("street", "rua"),
    ("apple", "maçã"), ("banana", "banana"), ("milk", "leite"), ("bread", "pão"),
    ("hand", "mão"), ("head", "cabeça"), ("eye", "olho"), ("ear", "orelha"),
    ("morning", "manhã"), ("night", "noite"), ("today", "hoje"), ("tomorrow", "amanhã"),
]

OPPOSITES = [
    ("big", "small"), ("hot", "cold"), ("happy", "sad"), ("fast", "slow"),
    ("open", "closed"), ("day", "night"), ("up", "down"), ("old", "young"),
    ("clean", "dirty"), ("easy", "difficult"), ("long", "short"), ("heavy", "light"),
    ("full", "empty"), ("strong", "weak"), ("early", "late"), ("wet", "dry"),
    ("rich", "poor"), ("loud", "quiet"), ("near", "far"), ("first", "last"),
]

PLURALS = [
    ("cat", "cats"), ("dog", "dogs"), ("book", "books"), ("house", "houses"),
    ("box", "boxes"), ("bus", "buses"), ("chair", "chairs"), ("apple", "apples"),
    ("baby", "babies"), ("city", "cities"), ("child", "children"), ("man", "men"),
    ("woman", "women"), ("foot", "feet"), ("tooth", "teeth"), ("mouse", "mice"),
    ("watch", "watches"), ("brush", "brushes"), ("story", "stories"), ("family", "families"),
]

VERB_TO_BE = [
    ("I _ a student.", "am"),
    ("She _ my friend.", "is"),
    ("They _ happy.", "are"),
    ("We _ at school.", "are"),
    ("He _ my brother.", "is"),
    ("You _ very kind.", "are"),
    ("It _ a nice day.", "is"),
    ("My parents _ at work.", "are"),
    ("This book _ interesting.", "is"),
    ("You and I _ friends.", "are"),
]

COLORS = [
    ("red", "vermelho"), ("blue", "azul"), ("green", "verde"), ("yellow", "amarelo"),
    ("black", "preto"), ("white", "branco"), ("orange", "laranja"), ("purple", "roxo"),
    ("pink", "rosa"), ("brown", "castanho"),
]

NUMBERS_WORDS = [
    (1, "one"), (2, "two"), (3, "three"), (4, "four"), (5, "five"),
    (6, "six"), (7, "seven"), (8, "eight"), (9, "nine"), (10, "ten"),
    (11, "eleven"), (12, "twelve"), (15, "fifteen"), (20, "twenty"),
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

ARTICLES = [
    ("apple", "an"), ("orange", "an"), ("umbrella", "an"), ("elephant", "an"),
    ("hour", "an"), ("egg", "an"),
    ("dog", "a"), ("cat", "a"), ("book", "a"), ("house", "a"), ("car", "a"), ("ball", "a"),
]


def gen_translation(dif, used):
    for _ in range(30):
        en, pt = random.choice(VOCAB)
        direction = random.choice(["to_pt", "to_en"])
        key = ("translation", en, direction)
        if key in used:
            continue
        used.add(key)
        if direction == "to_pt":
            return {"type": "translation", "subject": "english",
                    "text": f'Translate to Portuguese: "{en}"', "answer": pt}
        return {"type": "translation", "subject": "english",
                "text": f'Translate to English: "{pt}"', "answer": en}
    return None


def gen_opposite(dif, used):
    for _ in range(30):
        a, b = random.choice(OPPOSITES)
        ask_for_b = random.choice([True, False])
        key = ("opposite", a, ask_for_b)
        if key in used:
            continue
        used.add(key)
        if ask_for_b:
            return {"type": "opposite", "subject": "english",
                    "text": f'What is the opposite of "{a}"?', "answer": b}
        return {"type": "opposite", "subject": "english",
                "text": f'What is the opposite of "{b}"?', "answer": a}
    return None


def gen_plural(dif, used):
    for _ in range(30):
        sing, plur = random.choice(PLURALS)
        if ("plural", sing) in used:
            continue
        used.add(("plural", sing))
        return {"type": "plural", "subject": "english",
                "text": f'Write the plural of "{sing}":', "answer": plur}
    return None


def gen_singular(dif, used):
    for _ in range(30):
        sing, plur = random.choice(PLURALS)
        if ("singular", plur) in used:
            continue
        used.add(("singular", plur))
        return {"type": "singular", "subject": "english",
                "text": f'Write the singular of "{plur}":', "answer": sing}
    return None


def gen_verb_to_be(dif, used):
    for _ in range(30):
        sentence, answer = random.choice(VERB_TO_BE)
        if ("verb_to_be", sentence) in used:
            continue
        used.add(("verb_to_be", sentence))
        return {"type": "verb_to_be", "subject": "english",
                "text": f'Fill in the blank with am/is/are: "{sentence}"', "answer": answer}
    return None


def gen_color(dif, used):
    for _ in range(30):
        en, pt = random.choice(COLORS)
        direction = random.choice(["to_pt", "to_en"])
        key = ("color", en, direction)
        if key in used:
            continue
        used.add(key)
        if direction == "to_pt":
            return {"type": "color", "subject": "english",
                    "text": f'What color is "{en}" in Portuguese?', "answer": pt}
        return {"type": "color", "subject": "english",
                "text": f'What is the English word for the color "{pt}"?', "answer": en}
    return None


def gen_number_word(dif, used):
    for _ in range(30):
        n, word = random.choice(NUMBERS_WORDS)
        direction = random.choice(["to_word", "to_digit"])
        key = ("number_word", n, direction)
        if key in used:
            continue
        used.add(key)
        if direction == "to_word":
            return {"type": "number_word", "subject": "english",
                    "text": f'Write the number {n} in English words:', "answer": word}
        return {"type": "number_word", "subject": "english",
                "text": f'Write the digit for "{word}":', "answer": str(n)}
    return None


def gen_days(dif, used):
    for _ in range(30):
        idx = random.randint(0, 6)
        mode = random.choice(["next", "previous"])
        key = ("days", idx, mode)
        if key in used:
            continue
        used.add(key)
        day = DAYS[idx]
        if mode == "next":
            answer = DAYS[(idx + 1) % 7]
            return {"type": "days", "subject": "english",
                    "text": f'What day comes after {day}?', "answer": answer}
        answer = DAYS[(idx - 1) % 7]
        return {"type": "days", "subject": "english",
                "text": f'What day comes before {day}?', "answer": answer}
    return None


def gen_article(dif, used):
    for _ in range(30):
        word, art = random.choice(ARTICLES)
        if ("article", word) in used:
            continue
        used.add(("article", word))
        return {"type": "article", "subject": "english",
                "text": f'Choose "a" or "an": _ {word}', "answer": art}
    return None


ENGLISH_GENERATORS = {
    "translation": ("Vocabulary translation", gen_translation),
    "opposite": ("Opposites", gen_opposite),
    "plural": ("Plurals", gen_plural),
    "singular": ("Singular form", gen_singular),
    "verb_to_be": ("Verb 'to be'", gen_verb_to_be),
    "color": ("Colors", gen_color),
    "number_word": ("Numbers in words", gen_number_word),
    "days": ("Days of the week", gen_days),
    "article": ("Articles (a / an)", gen_article),
}


SUBJECTS = {
    "math": {"label": "🧮 Matemática", "generators": MATH_GENERATORS,
              "default": ("round", "expand", "mult", "add")},
    "english": {"label": "📖 Inglês", "generators": ENGLISH_GENERATORS,
                 "default": ("translation", "opposite", "plural", "verb_to_be")},
}


def question_badge(number, text):
    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
<span style="background:#4f46e5;color:#fff;border-radius:50%;min-width:28px;height:28px;
display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0;">{number}</span>
<span style="font-size:1.05rem;font-weight:600;">{text}</span>
</div>""",
        unsafe_allow_html=True,
    )


def normalize_expanded(txt):
    parts = [p.strip() for p in txt.split("+") if p.strip() != ""]
    try:
        numbers = sorted((int(p) for p in parts), reverse=True)
    except ValueError:
        return txt.strip()
    return "+".join(str(n) for n in numbers)


def check_answer(ex, val):
    if ex["type"] == "expand":
        return normalize_expanded(val) == normalize_expanded(ex["answer"])
    if ex.get("subject") == "english":
        return val.strip().lower() == ex["answer"].strip().lower()
    return val.replace(" ", "") == ex["answer"].replace(" ", "")


def build_exercises(generators, chosen_types, qty, dif):
    """Generate qty exercises, avoiding repeated questions/answers where possible."""
    exercises = []
    used = set()
    seen_texts = set()
    types_cycle = list(chosen_types)
    random.shuffle(types_cycle)
    attempts = 0
    max_attempts = qty * 40 + 40

    while len(exercises) < qty and attempts < max_attempts:
        attempts += 1
        t = types_cycle[attempts % len(types_cycle)]
        ex = generators[t][1](dif, used)
        if ex is None:
            continue
        if ex["text"] in seen_texts:
            continue
        seen_texts.add(ex["text"])
        exercises.append(ex)

    return exercises


# =========================================================
# ACCESS CODE STORE (single-use codes, persisted to disk)
# =========================================================
# st.secrets is read-only at runtime, so we can't "consume" a code
# there. Instead we keep a small JSON file next to the app that
# records which codes have already been redeemed. This keeps codes
# single-use even if a student shares theirs with a classmate.

def load_used_codes():
    if not os.path.exists(USED_CODES_FILE):
        return {}
    try:
        with open(USED_CODES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_used_codes(data):
    try:
        with open(USED_CODES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass  # non-fatal: worst case a code can be reused this session


def redeem_code(code):
    """
    Returns ('ok', None) if the code is valid and not yet used,
    ('used', when) if it was already redeemed,
    ('invalid', None) if the code doesn't exist at all.
    Marks the code as used on success.
    """
    valid_codes = st.secrets.get("access_codes", [])
    if code not in valid_codes or code == "":
        return "invalid", None

    used_codes = load_used_codes()
    if code in used_codes:
        return "used", used_codes[code]

    import datetime
    used_codes[code] = datetime.datetime.now().isoformat(timespec="seconds")
    save_used_codes(used_codes)
    return "ok", None


def whatsapp_link(message):
    import urllib.parse
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(message)}"


# ---------------- INTERFACE ----------------

st.title("📚 English and Math")

if "exercises" not in st.session_state:
    st.session_state.exercises = None
    st.session_state.checked = False

if "subject" not in st.session_state:
    st.session_state.subject = "math"

if st.session_state.exercises is None:
    st.subheader("Escolha a matéria")

    subject = st.radio(
        "Subject",
        options=list(SUBJECTS.keys()),
        format_func=lambda k: SUBJECTS[k]["label"],
        index=list(SUBJECTS.keys()).index(st.session_state.subject),
        label_visibility="collapsed",
        horizontal=True,
    )
    st.session_state.subject = subject
    generators = SUBJECTS[subject]["generators"]
    default_types = SUBJECTS[subject]["default"]

    st.subheader("Escolha os tipos de exercício")
    chosen_types = []
    for key, (label, _) in generators.items():
        if st.checkbox(label, value=key in default_types, key=f"chk_{subject}_{key}"):
            chosen_types.append(key)

    col1, col2 = st.columns(2)
    with col1:
        qty = st.selectbox("Number of questions", [1, 3, 5, 6, 8, 10], index=2)
    with col2:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
    dif = {"Easy": 1, "Medium": 2, "Hard": 3}[difficulty]

    if st.button("Start", type="primary"):
        if not chosen_types:
            st.error("Choose at least one exercise type.")
        else:
            exercises = build_exercises(generators, chosen_types, qty, dif)
            if not exercises:
                st.error("Could not generate exercises. Try selecting more types.")
            else:
                st.session_state.exercises = exercises
                st.session_state.checked = False
                st.rerun()

else:
    exercises = st.session_state.exercises

    if not st.session_state.checked:
        answers = []
        for i, ex in enumerate(exercises):
            question_badge(i + 1, ex['text'])
            ans = st.text_input("Your answer", key=f"ans_{i}", label_visibility="collapsed")
            answers.append(ans)
            st.markdown("---")

        col_back, col_check = st.columns(2)
        with col_back:
            if st.button("⬅️ Back"):
                st.session_state.exercises = None
                st.rerun()
        with col_check:
            if st.button("Check answers", type="primary"):
                st.session_state.answers = answers
                st.session_state.checked = True
                st.rerun()

    else:
        answers = st.session_state.answers
        correct_count = 0
        for i, ex in enumerate(exercises):
            val = answers[i].strip()
            is_correct = check_answer(ex, val)

            question_badge(i + 1, ex['text'])
            if is_correct:
                correct_count += 1
                st.success(f"✔️ Correct! ({val})")
            else:
                st.error(f"✘ Incorrect. Your answer: '{val}' — Correct answer: {ex['answer']}")

        st.markdown("---")
        st.markdown(f"## Score: {correct_count} / {len(exercises)}")

        st.markdown("---")
        st.subheader("📄 Download worksheet")
        st.caption(
            "Practicing online is free. Downloading this worksheet (with answers) "
            f"costs {PRICE_KZ} Kz."
        )

        # Step 1: payment instructions + WhatsApp contact, shown up front
        with st.expander("💳 How to get your access code", expanded=not st.session_state.get("has_code_hint", False)):
            st.markdown(
                f"""
1. Pay *{PRICE_KZ} Kz* via Express to *{EXPRESS_NUMBER}*.
2. Send the payment confirmation to the teacher on WhatsApp.
3. The teacher will reply with your personal access code.
4. Enter that code below to unlock the download.
                """
            )
            st.link_button(
                "📲 Send payment confirmation on WhatsApp",
                whatsapp_link(
                    f"Hi! I just paid {PRICE_KZ} Kz via Express for the worksheet. "
                    "Here is my payment confirmation:"
                ),
            )

        codigo = st.text_input("Access code", type="password", key="codigo_acesso")

        if st.button("Unlock download"):
            if codigo.strip() == "":
                st.warning("Enter the access code your teacher sent you, or see the instructions above to get one.")
            else:
                status, used_when = redeem_code(codigo.strip())
                if status == "ok":
                    conteudo = f"English and Math Exercises\nScore: {correct_count}/{len(exercises)}\n\n"
                    for i, ex in enumerate(exercises):
                        conteudo += f"{i + 1} / {ex['text']}\n   Answer: {ex['answer']}\n\n"
                    st.session_state.download_liberado = conteudo
                    st.session_state.has_code_hint = True
                    st.success("Access granted! Click the button below to download.")
                elif status == "used":
                    st.session_state.download_liberado = None
                    st.error(
                        f"This code was already used on {used_when}. "
                        "Codes are single-use — contact the teacher if you think this is a mistake."
                    )
                else:
                    st.session_state.download_liberado = None
                    st.error(
                        "That code isn't recognized. Double-check it, or use the "
                        "instructions above to get a valid one from the teacher."
                    )

        if st.session_state.get("download_liberado"):
            st.download_button(
                "⬇️ Download worksheet (.txt)",
                data=st.session_state.download_liberado,
                file_name="worksheet.txt",
                mime="text/plain",
            )

        if st.button("Try again"):
            st.session_state.exercises = None
            st.session_state.checked = False
            st.session_state.download_liberado = None
            st.rerun()