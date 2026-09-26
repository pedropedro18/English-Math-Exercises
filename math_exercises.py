import random
import streamlit as st

st.set_page_config(page_title="Exercícios - 4ª Classe", page_icon="📚", layout="centered")


# ---------------- MATH EXERCISE GENERATORS (Grade 4 level) ----------------

def gen_round(dif):
    n = random.randint(100, 9999)
    place = random.choice([10, 100, 1000])
    answer = int(round(n / place) * place)
    place_name = "ten" if place == 10 else "hundred" if place == 100 else "thousand"
    return {
        "type": "round",
        "subject": "math",
        "text": f"Round {n} to the nearest {place_name}:",
        "answer": str(answer),
    }


def gen_expand(dif):
    lo, hi = {1: (100, 999), 2: (1000, 9999), 3: (10000, 99999)}[dif]
    n = random.randint(lo, hi)
    digits = [int(d) for d in str(n)]
    length = len(digits)
    parts = [d * (10 ** (length - i - 1)) for i, d in enumerate(digits) if d != 0]
    return {
        "type": "expand",
        "subject": "math",
        "text": f'Write {n} in expanded form (use " + " between parts, e.g. 300 + 40 + 2):',
        "answer": " + ".join(str(p) for p in parts),
    }


def gen_mult(dif):
    a, b = random.randint(1, 9), random.randint(1, 9)
    return {"type": "mult", "subject": "math", "text": f"{a} × {b} =", "answer": str(a * b)}


def gen_add(dif):
    a, b = random.randint(10, 99), random.randint(10, 99)
    return {"type": "add", "subject": "math", "text": f"{a} + {b} =", "answer": str(a + b)}


def gen_sub(dif):
    a = random.randint(10, 99)
    b = random.randint(10, a)
    return {"type": "sub", "subject": "math", "text": f"{a} − {b} =", "answer": str(a - b)}


MATH_GENERATORS = {
    "round": ("Round numbers", gen_round),
    "expand": ("Expanded form", gen_expand),
    "mult": ("Multiplication", gen_mult),
    "add": ("Addition", gen_add),
    "sub": ("Subtraction", gen_sub),
}


# ---------------- ENGLISH EXERCISE GENERATORS (Grade 4 level) ----------------

VOCAB = [
    ("house", "casa"), ("dog", "cachorro"), ("cat", "gato"), ("book", "livro"),
    ("water", "água"), ("friend", "amigo"), ("school", "escola"), ("teacher", "professor"),
    ("family", "família"), ("table", "mesa"), ("chair", "cadeira"), ("window", "janela"),
    ("sun", "sol"), ("moon", "lua"), ("mother", "mãe"), ("father", "pai"),
    ("food", "comida"), ("tree", "árvore"), ("bird", "pássaro"), ("shoe", "sapato"),
]

OPPOSITES = [
    ("big", "small"), ("hot", "cold"), ("happy", "sad"), ("fast", "slow"),
    ("open", "closed"), ("day", "night"), ("up", "down"), ("old", "young"),
    ("clean", "dirty"), ("easy", "difficult"),
]

PLURALS = [
    ("cat", "cats"), ("dog", "dogs"), ("book", "books"), ("house", "houses"),
    ("box", "boxes"), ("bus", "buses"), ("chair", "chairs"), ("apple", "apples"),
    ("baby", "babies"), ("city", "cities"),
]

VERB_TO_BE = [
    ("I _ a student.", "am"),
    ("She _ my friend.", "is"),
    ("They _ happy.", "are"),
    ("We _ at school.", "are"),
    ("He _ my brother.", "is"),
    ("You _ very kind.", "are"),
    ("It _ a nice day.", "is"),
]


def gen_translation(dif):
    en, pt = random.choice(VOCAB)
    if random.choice([True, False]):
        return {
            "type": "translation",
            "subject": "english",
            "text": f'Translate to Portuguese: "{en}"',
            "answer": pt,
        }
    return {
        "type": "translation",
        "subject": "english",
        "text": f'Translate to English: "{pt}"',
        "answer": en,
    }


def gen_opposite(dif):
    a, b = random.choice(OPPOSITES)
    if random.choice([True, False]):
        return {"type": "opposite", "subject": "english",
                "text": f'What is the opposite of "{a}"?', "answer": b}
    return {"type": "opposite", "subject": "english",
            "text": f'What is the opposite of "{b}"?', "answer": a}


def gen_plural(dif):
    sing, plur = random.choice(PLURALS)
    return {
        "type": "plural",
        "subject": "english",
        "text": f'Write the plural of "{sing}":',
        "answer": plur,
    }


def gen_verb_to_be(dif):
    sentence, answer = random.choice(VERB_TO_BE)
    return {
        "type": "verb_to_be",
        "subject": "english",
        "text": f'Fill in the blank with am/is/are: "{sentence}"',
        "answer": answer,
    }


ENGLISH_GENERATORS = {
    "translation": ("Vocabulary translation", gen_translation),
    "opposite": ("Opposites", gen_opposite),
    "plural": ("Plurals", gen_plural),
    "verb_to_be": ("Verb 'to be'", gen_verb_to_be),
}


SUBJECTS = {
    "math": {"label": "🧮 Matemática", "generators": MATH_GENERATORS,
              "default": ("round", "expand", "mult")},
    "english": {"label": "📖 Inglês", "generators": ENGLISH_GENERATORS,
                 "default": ("translation", "opposite", "plural")},
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
        qty = st.selectbox("Number of questions", [1, 3, 5, 6], index=2)
    with col2:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
    dif = {"Easy": 1, "Medium": 2, "Hard": 3}[difficulty]

    if st.button("Start", type="primary"):
        if not chosen_types:
            st.error("Choose at least one exercise type.")
        else:
            exercises = []
            for _ in range(qty):
                t = random.choice(chosen_types)
                exercises.append(generators[t][1](dif))
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
        st.caption("Free to practice online. Downloading the worksheet costs 5.000 Kz — pay via Express to 923 030 010, then enter your access code.")

        codigo = st.text_input("Access code", type="password", key="codigo_acesso")
        if st.button("Unlock download"):
            codigos_validos = st.secrets.get("access_codes", [])
            if codigo in codigos_validos and codigo != "":
                conteudo = f"Exercícios - 4ª Classe\nScore: {correct_count}/{len(exercises)}\n\n"
                for i, ex in enumerate(exercises):
                    conteudo += f"{i + 1} / {ex['text']}\n   Answer: {ex['answer']}\n\n"
                st.session_state.download_liberado = conteudo
                st.success("Access granted! Click the button below to download.")
            else:
                st.session_state.download_liberado = None
                st.error("Invalid code. Pay 5.000 Kz via Express to 923 030 010, then contact the teacher to receive your access code.")

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