import random
import streamlit as st

st.set_page_config(page_title="Math Exercises - Grade 4", page_icon="📐", layout="centered")


# ---------------- EXERCISE GENERATORS (Grade 4 level) ----------------

def gen_round(dif):
    # Numbers always have 3 or 4 digits, so rounding to hundreds/thousands makes sense
    n = random.randint(100, 9999)
    place = random.choice([10, 100, 1000])
    answer = int(round(n / place) * place)
    place_name = "ten" if place == 10 else "hundred" if place == 100 else "thousand"
    return {
        "type": "round",
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
        "text": f'Write {n} in expanded form (use " + " between parts, e.g. 300 + 40 + 2):',
        "answer": " + ".join(str(p) for p in parts),
    }


def gen_mult(dif):
    a, b = random.randint(1, 9), random.randint(1, 9)
    return {"type": "mult", "text": f"{a} × {b} =", "answer": str(a * b)}


def gen_add(dif):
    a, b = random.randint(10, 99), random.randint(10, 99)
    return {"type": "add", "text": f"{a} + {b} =", "answer": str(a + b)}


def gen_sub(dif):
    a = random.randint(10, 99)
    b = random.randint(10, a)
    return {"type": "sub", "text": f"{a} − {b} =", "answer": str(a - b)}


GENERATORS = {
    "round": ("Round numbers", gen_round),
    "expand": ("Expanded form", gen_expand),
    "mult": ("Multiplication", gen_mult),
    "add": ("Addition", gen_add),
    "sub": ("Subtraction", gen_sub),
}


def normalize_expanded(txt):
    parts = [p.strip() for p in txt.split("+") if p.strip() != ""]
    try:
        numbers = sorted((int(p) for p in parts), reverse=True)
    except ValueError:
        return txt.strip()
    return "+".join(str(n) for n in numbers)


# ---------------- INTERFACE ----------------

st.title("📐 Math Exercises - Grade 4")

if "exercises" not in st.session_state:
    st.session_state.exercises = None
    st.session_state.checked = False

if st.session_state.exercises is None:
    st.subheader("Choose the exercise types")

    chosen_types = []
    for key, (label, _) in GENERATORS.items():
        if st.checkbox(label, value=key in ("round", "expand", "mult"), key=f"chk_{key}"):
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
                exercises.append(GENERATORS[t][1](dif))
            st.session_state.exercises = exercises
            st.session_state.checked = False
            st.rerun()

else:
    exercises = st.session_state.exercises

    if not st.session_state.checked:
        answers = []
        for i, ex in enumerate(exercises):
            st.markdown(f"*{i + 1} - {ex['text']}*")
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
            if ex["type"] == "expand":
                is_correct = normalize_expanded(val) == normalize_expanded(ex["answer"])
            else:
                is_correct = val.replace(" ", "") == ex["answer"].replace(" ", "")

            st.markdown(f"*{i + 1} - {ex['text']}*")
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
                conteudo = f"Math Exercises - Grade 4\nScore: {correct_count}/{len(exercises)}\n\n"
                for i, ex in enumerate(exercises):
                    conteudo += f"{i + 1} - {ex['text']}\n   Answer: {ex['answer']}\n\n"
                st.session_state.download_liberado = conteudo
                st.success("Access granted! Click the button below to download.")
            else:
                st.session_state.download_liberado = None
                st.error("Invalid code. Pay 5.000 Kz via Express to 923 030 010, then contact the teacher to receive your access code.")

        if st.session_state.get("download_liberado"):
            st.download_button(
                "⬇️ Download worksheet (.txt)",
                data=st.session_state.download_liberado,
                file_name="math_worksheet.txt",
                mime="text/plain",
            )

        if st.button("Try again"):
            st.session_state.exercises = None
            st.session_state.checked = False
            st.session_state.download_liberado = None
            st.rerun()