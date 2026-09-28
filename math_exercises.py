import random
import json
import os
import streamlit as st

st.set_page_config(page_title="English, Math, Português and Français - 4ª Classe", page_icon="📚", layout="centered")

# ---------------------------------------------------------
# CONFIG: change these to your real numbers
# ---------------------------------------------------------
EXPRESS_NUMBER = "923 030 010"
WHATSAPP_NUMBER = "244923030010"  # international format, no + or spaces, for wa.me links
PRICE_KZ = "5.000"
RECOVERY_FILE = "recovery_data.json"
UNLOCK_LOG_FILE = "unlock_log.json"
# Unlock limit removed: a code now unlocks on unlimited devices, forever.


# =========================================================
# MATH EXERCISE GENERATORS (Grade 4 level)
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

# Subject pronouns: (sentence, pronoun that replaces the subject)
EN_SUBJECT_PRONOUNS = [
    ("Maria is my friend.", "she"),
    ("Paulo is tall.", "he"),
    ("The dogs are big.", "they"),
    ("The book is on the table.", "it"),
    ("Ana and I are at school.", "we"),
    ("My brother and my sister are happy.", "they"),
    ("The cat is black.", "it"),
    ("Mr. Silva is a teacher.", "he"),
    ("The girls are singing.", "they"),
    ("Mrs. Costa is kind.", "she"),
    ("Pedro and I are friends.", "we"),
    ("The car is fast.", "it"),
    ("My mother is at home.", "she"),
    ("The boys are playing.", "they"),
    ("My father is a driver.", "he"),
]

# Possessive adjectives: (sentence with _, pronoun in brackets, answer)
EN_POSSESSIVES = [
    ("This is _ book. (I)", "my"),
    ("She loves _ mother. (she)", "her"),
    ("They love _ school. (they)", "their"),
    ("We like _ teacher. (we)", "our"),
    ("He has _ bag. (he)", "his"),
    ("You have _ pencil. (you)", "your"),
    ("The dog wags _ tail. (it)", "its"),
    ("I love _ family. (I)", "my"),
    ("They wash _ hands. (they)", "their"),
    ("She opens _ notebook. (she)", "her"),
    ("We clean _ classroom. (we)", "our"),
    ("He plays with _ friends. (he)", "his"),
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


def gen_en_pronoun(dif, used):
    for _ in range(30):
        sentence, answer = random.choice(EN_SUBJECT_PRONOUNS)
        if ("en_pronoun", sentence) in used:
            continue
        used.add(("en_pronoun", sentence))
        return {"type": "en_pronoun", "subject": "english",
                "text": f'Write the pronoun (I, you, he, she, it, we, they) that replaces the subject: "{sentence}"',
                "answer": answer}
    return None


def gen_en_possessive(dif, used):
    for _ in range(30):
        sentence, answer = random.choice(EN_POSSESSIVES)
        if ("en_possessive", sentence) in used:
            continue
        used.add(("en_possessive", sentence))
        return {"type": "en_possessive", "subject": "english",
                "text": f'Fill in the blank with my/your/his/her/its/our/their: "{sentence}"',
                "answer": answer}
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
    "en_pronoun": ("Pronouns (I, you, he, she...)", gen_en_pronoun),
    "en_possessive": ("Possessives (my, your, his...)", gen_en_possessive),
}


# =========================================================
# PORTUGUESE EXERCISE GENERATORS (4ª Classe)
# =========================================================

PT_PLURALS = [
    ("casa", "casas"), ("livro", "livros"), ("animal", "animais"), ("papel", "papéis"),
    ("pão", "pães"), ("mão", "mãos"), ("flor", "flores"), ("luz", "luzes"),
    ("lápis", "lápis"), ("mês", "meses"), ("cidadão", "cidadãos"), ("jornal", "jornais"),
    ("limão", "limões"), ("nação", "nações"), ("aluno", "alunos"), ("mulher", "mulheres"),
    ("canção", "canções"), ("hotel", "hotéis"), ("país", "países"), ("avião", "aviões"),
]

PT_OPPOSITES = [
    ("grande", "pequeno"), ("alto", "baixo"), ("feliz", "triste"), ("cheio", "vazio"),
    ("rápido", "lento"), ("quente", "frio"), ("novo", "velho"), ("dia", "noite"),
    ("limpo", "sujo"), ("forte", "fraco"), ("longe", "perto"), ("claro", "escuro"),
    ("doce", "amargo"), ("gordo", "magro"), ("bonito", "feio"), ("aberto", "fechado"),
    ("subir", "descer"), ("entrar", "sair"), ("chegar", "partir"), ("rico", "pobre"),
]

PT_FEMININE = [
    ("menino", "menina"), ("professor", "professora"), ("gato", "gata"), ("aluno", "aluna"),
    ("rei", "rainha"), ("ator", "atriz"), ("galo", "galinha"), ("homem", "mulher"),
    ("pai", "mãe"), ("avô", "avó"), ("irmão", "irmã"), ("tio", "tia"),
    ("cão", "cadela"), ("amigo", "amiga"), ("filho", "filha"), ("vizinho", "vizinha"),
    ("cantor", "cantora"), ("padrinho", "madrinha"),
]

PT_SYLLABLES = [
    ("sol", 1), ("casa", 2), ("bola", 2), ("livro", 2), ("janela", 3), ("escola", 3),
    ("cadeira", 3), ("borboleta", 4), ("computador", 4), ("elefante", 4),
    ("mesa", 2), ("caderno", 3), ("banana", 3), ("sapato", 3), ("professora", 4),
    ("pão", 1), ("amigo", 3), ("telefone", 4),
]

# Personal pronouns: replace the subject
PT_PRONOUNS = [
    ("O João corre.", "ele"),
    ("A Ana canta.", "ela"),
    ("Os meninos jogam à bola.", "eles"),
    ("As meninas brincam.", "elas"),
    ("A Maria e a Rita estudam.", "elas"),
    ("O Pedro e o Paulo trabalham.", "eles"),
    ("O Pedro e eu brincamos.", "nós"),
    ("A minha mãe cozinha.", "ela"),
    ("O meu pai conduz.", "ele"),
    ("A professora escreve.", "ela"),
    ("Os alunos leem.", "eles"),
    ("A Ana e eu cantamos.", "nós"),
    ("O gato dorme.", "ele"),
    ("As flores crescem.", "elas"),
]

# Pronouns + verb "ser": fill the missing pronoun
PT_PRONOUN_BLANK = [
    ("_ sou aluno.", "eu"),
    ("_ és meu amigo.", "tu"),
    ("_ somos irmãos.", "nós"),
    ("_ estudo Português. (a falar de mim)", "eu"),
    ("_ falas muito bem. (a falar contigo)", "tu"),
    ("_ cantamos na escola. (eu e os meus colegas)", "nós"),
]

PT_VERB_SER = [
    ("Eu _ aluno.", "sou"),
    ("Tu _ meu amigo.", "és"),
    ("Ele _ professor.", "é"),
    ("Ela _ simpática.", "é"),
    ("Nós _ irmãos.", "somos"),
    ("Eles _ estudantes.", "são"),
    ("Elas _ felizes.", "são"),
    ("Eu _ Angolano.", "sou"),
    ("Tu _ muito alto.", "és"),
    ("Nós _ da 4ª classe.", "somos"),
]

PT_POSSESSIVES = [
    ("Este livro é de mim. É o _ livro. (meu/teu/dele)", "meu"),
    ("Esta casa é de ti. É a _ casa. (minha/tua/dela)", "tua"),
    ("Esta bola é de mim. É a _ bola. (minha/tua/dela)", "minha"),
    ("Este caderno é de ti. É o _ caderno. (meu/teu/dele)", "teu"),
    ("Esta mala é da Ana. É a mala _. (minha/tua/dela)", "dela"),
    ("Este carro é do Pedro. É o carro _. (meu/teu/dele)", "dele"),
]

# Reading and interpretation: each passage has questions
# (question, correct option, [wrong option, wrong option])
PT_READINGS = [
    {
        "id": "ana_cao",
        "title": "A Ana e o seu cão",
        "text": (
            "A Ana vive em Luanda com a mãe e o irmão Paulo. Todas as manhãs, leva o seu "
            "cão, o Bolinhas, a passear no quintal. Um dia, o Bolinhas encontrou uma bola "
            "azul debaixo da mangueira. A Ana ficou muito feliz e brincou com ele até ao "
            "meio-dia. À tarde, choveu muito e ficaram em casa a ver a chuva pela janela."
        ),
        "questions": [
            ("Onde vive a Ana?", "Em Luanda", ["Em Benguela", "No Huambo"]),
            ("Como se chama o cão da Ana?", "Bolinhas", ["Rex", "Tobi"]),
            ("Onde o cão encontrou a bola?", "Debaixo da mangueira", ["Dentro de casa", "Na escola"]),
            ("Porque ficaram em casa à tarde?", "Porque choveu muito", ["Porque estavam cansados", "Porque a Ana estava doente"]),
            ("Qual é o melhor título para este texto?", "Um dia de brincadeira", ["Uma viagem ao mar", "A aula de Matemática"]),
        ],
    },
    {
        "id": "feira",
        "title": "A feira do bairro",
        "text": (
            "Ao sábado, o senhor Manuel vai à feira do bairro com a filha Rita. Compram "
            "tomates, cebolas e peixe fresco. A Rita ajuda a carregar o saco mais leve. No "
            "fim, o pai compra-lhe uma laranja doce como prémio pela ajuda. A Rita agradece "
            "com um sorriso e diz: \"Obrigada, pai!\""
        ),
        "questions": [
            ("Quando vão à feira?", "Ao sábado", ["Ao domingo", "À sexta-feira"]),
            ("O que compram na feira?", "Tomates, cebolas e peixe", ["Sapatos e livros", "Pão e leite"]),
            ("Que saco carrega a Rita?", "O mais leve", ["O mais pesado", "Nenhum"]),
            ("Porque é que o pai compra uma laranja à Rita?", "Como prémio pela ajuda", ["Porque ela chorou", "Porque a laranja estava barata"]),
            ("O que quer dizer a palavra \"prémio\"?", "Algo que se dá a quem fez uma coisa boa", ["Um castigo", "Um tipo de fruta"]),
        ],
    },
    {
        "id": "baoba",
        "title": "O embondeiro",
        "text": (
            "O embondeiro, ou baobá, é uma árvore muito grande e muito antiga que existe em "
            "Angola. O seu tronco é tão grosso que são precisas muitas pessoas para o "
            "abraçar. Os frutos chamam-se múcuas e servem para fazer sumo. Na estação seca, "
            "a árvore guarda água no tronco. Por isso, dizem que o embondeiro é uma árvore sábia."
        ),
        "questions": [
            ("Como é o tronco do embondeiro?", "Muito grosso", ["Muito fino", "Muito curto"]),
            ("Para que servem as múcuas?", "Para fazer sumo", ["Para fazer roupa", "Para construir casas"]),
            ("Onde é que a árvore guarda água?", "No tronco", ["Nas folhas", "Nas flores"]),
            ("Porque dizem que o embondeiro é \"sábio\"?", "Porque sabe guardar água para a estação seca", ["Porque sabe ler", "Porque cresce muito depressa"]),
            ("Qual é o melhor título para este texto?", "A árvore gigante de Angola", ["O rio de Luanda", "A festa da escola"]),
        ],
    },
]


def gen_pt_plural(dif, used):
    for _ in range(30):
        sing, plur = random.choice(PT_PLURALS)
        if ("pt_plural", sing) in used:
            continue
        used.add(("pt_plural", sing))
        return {"type": "pt_plural", "subject": "portuguese",
                "text": f'Escreve o plural de "{sing}":', "answer": plur}
    return None


def gen_pt_singular(dif, used):
    for _ in range(30):
        sing, plur = random.choice(PT_PLURALS)
        if ("pt_singular", plur) in used:
            continue
        used.add(("pt_singular", plur))
        return {"type": "pt_singular", "subject": "portuguese",
                "text": f'Escreve o singular de "{plur}":', "answer": sing}
    return None


def gen_pt_opposite(dif, used):
    for _ in range(30):
        a, b = random.choice(PT_OPPOSITES)
        ask_for_b = random.choice([True, False])
        key = ("pt_opposite", a, ask_for_b)
        if key in used:
            continue
        used.add(key)
        if ask_for_b:
            return {"type": "pt_opposite", "subject": "portuguese",
                    "text": f'Qual é o contrário de "{a}"?', "answer": b}
        return {"type": "pt_opposite", "subject": "portuguese",
                "text": f'Qual é o contrário de "{b}"?', "answer": a}
    return None


def gen_pt_feminine(dif, used):
    for _ in range(30):
        m, f = random.choice(PT_FEMININE)
        to_f = random.choice([True, False])
        key = ("pt_feminine", m, to_f)
        if key in used:
            continue
        used.add(key)
        if to_f:
            return {"type": "pt_feminine", "subject": "portuguese",
                    "text": f'Escreve o feminino de "{m}":', "answer": f}
        return {"type": "pt_feminine", "subject": "portuguese",
                "text": f'Escreve o masculino de "{f}":', "answer": m}
    return None


def gen_pt_syllables(dif, used):
    for _ in range(30):
        word, n = random.choice(PT_SYLLABLES)
        if ("pt_syllables", word) in used:
            continue
        used.add(("pt_syllables", word))
        return {"type": "pt_syllables", "subject": "portuguese",
                "text": f'Quantas sílabas tem a palavra "{word}"? (responde só com o número)',
                "answer": str(n)}
    return None


def gen_pt_pronoun(dif, used):
    for _ in range(30):
        if random.random() < 0.65:
            sentence, answer = random.choice(PT_PRONOUNS)
            key = ("pt_pronoun", sentence)
            if key in used:
                continue
            used.add(key)
            return {"type": "pt_pronoun", "subject": "portuguese",
                    "text": f'Escreve o pronome pessoal (eu, tu, ele, ela, nós, eles, elas) que substitui o sujeito: "{sentence}"',
                    "answer": answer}
        sentence, answer = random.choice(PT_PRONOUN_BLANK)
        key = ("pt_pronoun", sentence)
        if key in used:
            continue
        used.add(key)
        return {"type": "pt_pronoun", "subject": "portuguese",
                "text": f'Completa com o pronome pessoal certo: "{sentence}"',
                "answer": answer}
    return None


def gen_pt_possessive(dif, used):
    for _ in range(30):
        sentence, answer = random.choice(PT_POSSESSIVES)
        if ("pt_possessive", sentence) in used:
            continue
        used.add(("pt_possessive", sentence))
        return {"type": "pt_possessive", "subject": "portuguese",
                "text": f'Completa com o pronome possessivo certo: "{sentence}"',
                "answer": answer}
    return None


def gen_pt_verb_ser(dif, used):
    for _ in range(30):
        sentence, answer = random.choice(PT_VERB_SER)
        if ("pt_verb_ser", sentence) in used:
            continue
        used.add(("pt_verb_ser", sentence))
        return {"type": "pt_verb_ser", "subject": "portuguese",
                "text": f'Completa com a forma certa do verbo SER: "{sentence}"',
                "answer": answer}
    return None


def gen_pt_reading(dif, used):
    """Uma pergunta de interpretação. Tenta manter o mesmo texto na mesma sessão."""
    current = next((k[1] for k in used if k[0] == "pt_reading_current"), None)
    others = [p for p in PT_READINGS if p["id"] != current]
    random.shuffle(others)
    order = [p for p in PT_READINGS if p["id"] == current] + others

    for p in order:
        free = [i for i in range(len(p["questions"])) if ("pt_reading", p["id"], i) not in used]
        if not free:
            continue
        i = random.choice(free)
        used.add(("pt_reading", p["id"], i))
        for k in [k for k in used if k[0] == "pt_reading_current"]:
            used.discard(k)
        used.add(("pt_reading_current", p["id"]))

        question, correct, wrongs = p["questions"][i]
        options = [correct] + list(wrongs)
        random.shuffle(options)
        letters = ["A", "B", "C"]
        answer = letters[options.index(correct)]
        opts_html = "<br>".join(f"{l}) {o}" for l, o in zip(letters, options))
        return {
            "type": "pt_reading", "subject": "portuguese",
            "passage_id": p["id"], "passage_title": p["title"], "passage": p["text"],
            "text": f"{question}<br>{opts_html}<br><i>(responde só com a letra: A, B ou C)</i>",
            "answer": answer,
        }
    return None


PORTUGUESE_GENERATORS = {
    "pt_plural": ("Plural das palavras", gen_pt_plural),
    "pt_singular": ("Singular das palavras", gen_pt_singular),
    "pt_opposite": ("Antónimos (contrários)", gen_pt_opposite),
    "pt_feminine": ("Masculino e feminino", gen_pt_feminine),
    "pt_syllables": ("Sílabas", gen_pt_syllables),
    "pt_pronoun": ("Pronomes pessoais (eu, tu, ele...)", gen_pt_pronoun),
    "pt_possessive": ("Pronomes possessivos (meu, teu...)", gen_pt_possessive),
    "pt_verb_ser": ("Verbo SER", gen_pt_verb_ser),
    "pt_reading": ("Leitura e interpretação", gen_pt_reading),
}


# =========================================================
# FRENCH EXERCISE GENERATORS (Francês - iniciação, 4ª Classe)
# =========================================================

import unicodedata


def strip_accents(txt):
    """Remove accents so children typing without accents are not penalised."""
    nfkd = unicodedata.normalize("NFD", txt)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


FR_VOCAB = [
    ("casa", "maison"), ("cão", "chien"), ("gato", "chat"), ("livro", "livre"),
    ("água", "eau"), ("amigo", "ami"), ("escola", "école"), ("professor", "professeur"),
    ("família", "famille"), ("mesa", "table"), ("cadeira", "chaise"), ("janela", "fenêtre"),
    ("sol", "soleil"), ("lua", "lune"), ("mãe", "mère"), ("pai", "père"),
    ("pão", "pain"), ("leite", "lait"), ("maçã", "pomme"), ("árvore", "arbre"),
    ("rio", "rivière"), ("cidade", "ville"), ("rua", "rue"), ("mão", "main"),
]

FR_GREETINGS = [
    ("Bom dia", "bonjour"), ("Boa noite", "bonne nuit"), ("Obrigado", "merci"),
    ("Adeus", "au revoir"), ("Olá (informal)", "salut"), ("Sim", "oui"),
    ("Não", "non"), ("Desculpa", "pardon"),
]

FR_COLORS = [
    ("vermelho", "rouge"), ("azul", "bleu"), ("verde", "vert"), ("amarelo", "jaune"),
    ("preto", "noir"), ("branco", "blanc"), ("laranja", "orange"), ("roxo", "violet"),
    ("rosa", "rose"), ("castanho", "marron"),
]

FR_NUMBERS = [
    (1, "un"), (2, "deux"), (3, "trois"), (4, "quatre"), (5, "cinq"),
    (6, "six"), (7, "sept"), (8, "huit"), (9, "neuf"), (10, "dix"),
    (11, "onze"), (12, "douze"), (15, "quinze"), (20, "vingt"),
]

FR_DAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

FR_ARTICLES = [
    ("maison", "une"), ("livre", "un"), ("table", "une"), ("chat", "un"),
    ("école", "une"), ("chaise", "une"), ("ami", "un"), ("fenêtre", "une"),
    ("chien", "un"), ("pomme", "une"), ("stylo", "un"), ("porte", "une"),
]

FR_PRONOUNS = [
    ("Marie chante.", "elle"),
    ("Paul court.", "il"),
    ("Les garçons jouent.", "ils"),
    ("Les filles dansent.", "elles"),
    ("Pierre et moi mangeons.", "nous"),
    ("Ma mère cuisine.", "elle"),
    ("Mon père travaille.", "il"),
    ("Anne et Sophie chantent.", "elles"),
    ("Paul et Marc jouent.", "ils"),
    ("Le chat dort.", "il"),
]

FR_ETRE = [
    ("Je _ élève.", "suis"),
    ("Tu _ mon ami.", "es"),
    ("Il _ professeur.", "est"),
    ("Elle _ gentille.", "est"),
    ("Nous _ frères.", "sommes"),
    ("Vous _ contents.", "êtes"),
    ("Ils _ à l'école.", "sont"),
    ("Elles _ grandes.", "sont"),
]

FR_AVOIR = [
    ("J'_ un chat.", "ai"),
    ("Tu _ un livre.", "as"),
    ("Il _ une sœur.", "a"),
    ("Nous _ deux chiens.", "avons"),
    ("Vous _ un stylo.", "avez"),
    ("Ils _ une maison.", "ont"),
]


def gen_fr_translation(dif, used):
    for _ in range(30):
        pt, fr = random.choice(FR_VOCAB)
        direction = random.choice(["to_fr", "to_pt"])
        key = ("fr_translation", pt, direction)
        if key in used:
            continue
        used.add(key)
        if direction == "to_fr":
            return {"type": "fr_translation", "subject": "french",
                    "text": f'Traduz para francês: "{pt}"', "answer": fr}
        return {"type": "fr_translation", "subject": "french",
                "text": f'Traduz para português: "{fr}"', "answer": pt}
    return None


def gen_fr_greeting(dif, used):
    for _ in range(30):
        pt, fr = random.choice(FR_GREETINGS)
        if ("fr_greeting", pt) in used:
            continue
        used.add(("fr_greeting", pt))
        return {"type": "fr_greeting", "subject": "french",
                "text": f'Como se diz "{pt}" em francês?', "answer": fr}
    return None


def gen_fr_color(dif, used):
    for _ in range(30):
        pt, fr = random.choice(FR_COLORS)
        direction = random.choice(["to_fr", "to_pt"])
        key = ("fr_color", pt, direction)
        if key in used:
            continue
        used.add(key)
        if direction == "to_fr":
            return {"type": "fr_color", "subject": "french",
                    "text": f'Como se diz a cor "{pt}" em francês?', "answer": fr}
        return {"type": "fr_color", "subject": "french",
                "text": f'Que cor é "{fr}" em português?', "answer": pt}
    return None


def gen_fr_number(dif, used):
    for _ in range(30):
        n, word = random.choice(FR_NUMBERS)
        direction = random.choice(["to_word", "to_digit"])
        key = ("fr_number", n, direction)
        if key in used:
            continue
        used.add(key)
        if direction == "to_word":
            return {"type": "fr_number", "subject": "french",
                    "text": f'Escreve o número {n} em francês:', "answer": word}
        return {"type": "fr_number", "subject": "french",
                "text": f'Escreve o algarismo de "{word}":', "answer": str(n)}
    return None


def gen_fr_days(dif, used):
    for _ in range(30):
        idx = random.randint(0, 6)
        mode = random.choice(["next", "previous"])
        key = ("fr_days", idx, mode)
        if key in used:
            continue
        used.add(key)
        day = FR_DAYS[idx]
        if mode == "next":
            return {"type": "fr_days", "subject": "french",
                    "text": f'Qual é o dia depois de "{day}"? (em francês)',
                    "answer": FR_DAYS[(idx + 1) % 7]}
        return {"type": "fr_days", "subject": "french",
                "text": f'Qual é o dia antes de "{day}"? (em francês)',
                "answer": FR_DAYS[(idx - 1) % 7]}
    return None


def gen_fr_article(dif, used):
    for _ in range(30):
        word, art = random.choice(FR_ARTICLES)
        if ("fr_article", word) in used:
            continue
        used.add(("fr_article", word))
        return {"type": "fr_article", "subject": "french",
                "text": f'Escolhe "un" ou "une": _ {word}', "answer": art}
    return None


def gen_fr_pronoun(dif, used):
    for _ in range(30):
        sentence, answer = random.choice(FR_PRONOUNS)
        if ("fr_pronoun", sentence) in used:
            continue
        used.add(("fr_pronoun", sentence))
        return {"type": "fr_pronoun", "subject": "french",
                "text": f'Escreve o pronome (je, tu, il, elle, nous, vous, ils, elles) que substitui o sujeito: "{sentence}"',
                "answer": answer}
    return None


def gen_fr_etre(dif, used):
    for _ in range(30):
        sentence, answer = random.choice(FR_ETRE)
        if ("fr_etre", sentence) in used:
            continue
        used.add(("fr_etre", sentence))
        return {"type": "fr_etre", "subject": "french",
                "text": f'Completa com o verbo ÊTRE (ser): "{sentence}"', "answer": answer}
    return None


def gen_fr_avoir(dif, used):
    for _ in range(30):
        sentence, answer = random.choice(FR_AVOIR)
        if ("fr_avoir", sentence) in used:
            continue
        used.add(("fr_avoir", sentence))
        return {"type": "fr_avoir", "subject": "french",
                "text": f'Completa com o verbo AVOIR (ter): "{sentence}"', "answer": answer}
    return None


FRENCH_GENERATORS = {
    "fr_translation": ("Vocabulário (PT ↔️ FR)", gen_fr_translation),
    "fr_greeting": ("Cumprimentos e palavras úteis", gen_fr_greeting),
    "fr_color": ("Cores", gen_fr_color),
    "fr_number": ("Números", gen_fr_number),
    "fr_days": ("Dias da semana", gen_fr_days),
    "fr_article": ("Artigos (un / une)", gen_fr_article),
    "fr_pronoun": ("Pronomes (je, tu, il, elle...)", gen_fr_pronoun),
    "fr_etre": ("Verbo ÊTRE", gen_fr_etre),
    "fr_avoir": ("Verbo AVOIR", gen_fr_avoir),
}


SUBJECTS = {
    "math": {"label": "🧮 Matemática", "generators": MATH_GENERATORS,
              "default": ("round", "expand", "mult", "add")},
    "english": {"label": "📖 Inglês", "generators": ENGLISH_GENERATORS,
                 "default": ("translation", "opposite", "plural", "verb_to_be", "en_pronoun")},
    "portuguese": {"label": "📕 Português", "generators": PORTUGUESE_GENERATORS,
                   "default": ("pt_plural", "pt_opposite", "pt_feminine", "pt_pronoun", "pt_reading")},
    "french": {"label": "🇫🇷 Francês", "generators": FRENCH_GENERATORS,
               "default": ("fr_translation", "fr_greeting", "fr_color", "fr_pronoun")},
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


def show_passage(ex, last_pid):
    """Mostra o texto de leitura só quando muda. Devolve o id do texto atual."""
    pid = ex.get("passage_id")
    if pid and pid != last_pid:
        st.markdown(
            f"""<div style="background:#f5f3ff;border-left:5px solid #4f46e5;border-radius:8px;
padding:12px 16px;margin:8px 0 14px 0;color:#1f2937;">
<b>📖 Lê o texto com atenção: {ex['passage_title']}</b><br><br>{ex['passage']}</div>""",
            unsafe_allow_html=True,
        )
    return pid or last_pid


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
    if ex.get("subject") == "french":
        return strip_accents(val.strip().lower()) == strip_accents(ex["answer"].strip().lower())
    if ex.get("subject") in ("english", "portuguese"):
        return val.strip().lower() == ex["answer"].strip().lower()
    return val.replace(" ", "") == ex["answer"].replace(" ", "")


def group_reading(exercises):
    """Mantém as perguntas do mesmo texto de leitura juntas."""
    result, placed = [], set()
    for ex in exercises:
        pid = ex.get("passage_id")
        if pid is None:
            result.append(ex)
        elif pid not in placed:
            placed.add(pid)
            result.extend(e for e in exercises if e.get("passage_id") == pid)
    return result


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

    return group_reading(exercises)


def whatsapp_link(message):
    import urllib.parse
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(message)}"


def show_privacy_notice():
    st.info(
        """
🔒 Política de Privacidade e Uso

Sobre o teu acesso
- Este código é pessoal e intransmissível — foi comprado por ti para uso individual.
- Não partilhes, vendas nem copies o código ou o link de acesso com outras pessoas.

Sobre os teus dados
- Guardamos apenas: o código de acesso, a data/hora de desbloqueio (para segurança) e, se definires, a tua frase-secreta pessoal (usada só para recuperares o acesso).
- Não vendemos nem partilhamos estes dados com terceiros, nem os usamos para qualquer outro fim.
- Podes pedir ao professor, a qualquer momento, para apagar os teus dados.

Em caso de incumprimento
- Partilhar, vender ou copiar o código/link pode levar ao bloqueio permanente do acesso.
        """
    )


# =========================================================
# RECOVERY DATA (code <-> personal secret phrase)
# =========================================================

def load_recovery_data():
    if not os.path.exists(RECOVERY_FILE):
        return {}
    try:
        with open(RECOVERY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_recovery_data(data):
    try:
        with open(RECOVERY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def normalize_phrase(phrase):
    return phrase.strip().lower()


def register_recovery_phrase(code, phrase):
    if not phrase.strip():
        return
    data = load_recovery_data()
    if code not in data:
        data[code] = normalize_phrase(phrase)
        save_recovery_data(data)


def find_code_by_phrase(phrase):
    data = load_recovery_data()
    target = normalize_phrase(phrase)
    for code, saved_phrase in data.items():
        if saved_phrase == target:
            return code
    return None


# =========================================================
# UNLOCK LOG (kept only for record-keeping / stats — no
# limit is enforced anymore, so this never blocks anyone)
# =========================================================

def load_unlock_log():
    if not os.path.exists(UNLOCK_LOG_FILE):
        return {}
    try:
        with open(UNLOCK_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_unlock_log(data):
    try:
        with open(UNLOCK_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def register_unlock(code):
    """
    Registers a new unlock event for this code, purely for logging.
    Always succeeds — there is no device/attempt limit anymore, so
    access (and recovery) works forever on any number of devices.
    """
    session_flag = f"counted_{code}"
    if st.session_state.get(session_flag):
        return True  # already counted in this session

    import datetime
    log = load_unlock_log()
    entries = log.get(code, [])
    entries.append(datetime.datetime.now().isoformat(timespec="seconds"))
    log[code] = entries
    save_unlock_log(log)
    st.session_state[session_flag] = True
    return True


# =========================================================
# PERMANENT UNLOCK (via link with ?code=... in the URL)
# =========================================================

def check_permanent_unlock():
    if "unlocked" not in st.session_state:
        st.session_state.unlocked = False

    query_code = st.query_params.get("code", "")
    valid_codes = st.secrets.get("access_codes", [])

    if query_code and query_code in valid_codes and not st.session_state.unlocked:
        register_unlock(query_code)
        st.session_state.unlocked = True


# ---------------- INTERFACE ----------------

st.title("📚 English, Math, Português and Français")

check_permanent_unlock()

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
        last_pid = None
        for i, ex in enumerate(exercises):
            last_pid = show_passage(ex, last_pid)
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

        if not st.session_state.unlocked:
            # ---- LOCKED VIEW: no correct/incorrect shown ----
            st.warning(
                "As respostas certas/erradas ficam escondidas até desbloqueares o acesso "
                "(pagamento único, válido para sempre, em qualquer número de dispositivos)."
            )

            tab_unlock, tab_forgot = st.tabs(["🔓 Tenho um código", "❓ Esqueci o meu código"])

            with tab_unlock:
                with st.expander("💳 Como obter o código de acesso", expanded=True):
                    st.markdown(
                        f"""
1. Pay {PRICE_KZ} Kz via Express to {EXPRESS_NUMBER}.
2. Send the payment confirmation to the teacher on WhatsApp.
3. The teacher will reply with your personal access code.
4. Enter that code below to unlock forever.
                        """
                    )
                    st.link_button(
                        "📲 Send payment confirmation on WhatsApp",
                        whatsapp_link(
                            f"Hi! I just paid {PRICE_KZ} Kz via Express to unlock the site. "
                            "Here is my payment confirmation:"
                        ),
                    )

                codigo = st.text_input("Access code", type="password", key="codigo_acesso")
                frase_secreta = st.text_input(
                    "Define uma frase-secreta pessoal (só tu sabes) — usa-a se perderes o código",
                    type="password",
                    key="frase_secreta",
                    help='Ex: "o nome do meu primeiro animal de estimação". Guarda isto de cabeça, não partilhes.',
                )

                if st.button("Unlock forever", type="primary"):
                    valid_codes = st.secrets.get("access_codes", [])
                    if codigo.strip() == "":
                        st.warning("Enter the access code your teacher sent you.")
                    elif codigo.strip() not in valid_codes:
                        st.error(
                            "That code isn't recognized. Double-check it, or use the "
                            "instructions above to get a valid one from the teacher."
                        )
                    else:
                        clean_code = codigo.strip()
                        register_recovery_phrase(clean_code, frase_secreta)
                        register_unlock(clean_code)
                        st.session_state.unlocked = True
                        st.query_params["code"] = clean_code
                        st.success(
                            "✅ Unlocked! Save this page in your browser bookmarks/favorites "
                            "so you never need to pay or enter the code again."
                        )
                        show_privacy_notice()
                        st.rerun()

            with tab_forgot:
                st.markdown(
                    "Se já desbloqueaste antes e definiste uma frase-secreta pessoal, "
                    "escreve-a aqui para recuperares o acesso sem precisares de contactar o professor."
                )
                frase_recuperar = st.text_input(
                    "A tua frase-secreta pessoal",
                    type="password",
                    key="frase_recuperar",
                )
                if st.button("Recuperar acesso"):
                    if frase_recuperar.strip() == "":
                        st.warning("Escreve a frase-secreta que definiste da primeira vez.")
                    else:
                        found_code = find_code_by_phrase(frase_recuperar)
                        if not found_code:
                            st.error(
                                "Frase não reconhecida. Se nunca definiste uma, "
                                "contacta o professor para receberes o teu código novamente."
                            )
                        else:
                            register_unlock(found_code)
                            st.session_state.unlocked = True
                            st.query_params["code"] = found_code
                            st.success(
                                "✅ Acesso recuperado! Guarda este link nos favoritos para "
                                "não precisares de repetir isto."
                            )
                            show_privacy_notice()
                            st.rerun()

        else:
            # ---- UNLOCKED VIEW: show correct/incorrect ----
            with st.expander("🔒 Política de Privacidade e Uso"):
                show_privacy_notice()

            correct_count = 0
            last_pid = None
            for i, ex in enumerate(exercises):
                last_pid = show_passage(ex, last_pid)
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
        if st.button("Try again"):
            st.session_state.exercises = None
            st.session_state.checked = False
            st.rerun()