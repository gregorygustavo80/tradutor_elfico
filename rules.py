import re


# ---------------------------------------------------------------------------
# Normalização e Tokenização
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Converte para minúsculas, remove pontuação e padroniza espaços."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize(text: str) -> list:
    """Divide o texto em tokens por espaço."""
    return text.split()


# ---------------------------------------------------------------------------
# Artigos
# ---------------------------------------------------------------------------

PT_ARTICLES = {
    "o": "i",
    "a": "i",
    "os": "in",
    "as": "in",
}

SD_ARTICLES = {
    "i": "o/a",
    "in": "os/as",
}


def apply_article_rules_pt_to_sd(word: str) -> str:
    return PT_ARTICLES.get(word, word)


def apply_article_rules_sd_to_pt(word: str) -> str:
    return SD_ARTICLES.get(word, word)


# ---------------------------------------------------------------------------
# Preposições
# ---------------------------------------------------------------------------

PT_PREPOSITIONS = {
    "de": "o",
    "do": "o",
    "da": "o",
    "dos": "o",
    "das": "o",
    "em": "mi",
    "no": "mi",
    "na": "mi",
    "nos": "mi",
    "nas": "mi",
    "para": "na",
    "com": "be",
    "por": "na",
    "sem": "av",
    "sob": "di",
    "sobre": "or",
    "entre": "imbi",
    "até": "tîr",
}


def apply_preposition_rules_pt_to_sd(word: str) -> str:
    return PT_PREPOSITIONS.get(word, word)


# ---------------------------------------------------------------------------
# Plural básico (PT → SD)
# Reconhece palavras terminadas em "s" e tenta o singular
# ---------------------------------------------------------------------------

def strip_plural_pt(word: str) -> tuple:
    """
    Tenta identificar se a palavra é um plural em português.
    Retorna (singular, is_plural). Heurística simples.
    """
    if word.endswith("ões"):
        return word[:-3] + "ão", True
    if word.endswith("ães"):
        return word[:-3] + "ão", True
    if word.endswith("ais"):
        return word[:-1], True  # "animais" → "animal"
    if word.endswith("eis"):
        return word[:-1], True
    if word.endswith("es") and len(word) > 3:
        return word[:-2], True
    if word.endswith("s") and len(word) > 2:
        return word[:-1], True
    return word, False


# ---------------------------------------------------------------------------
# Mutação consonantal suave (aplicada após artigos em síndarin)
# ---------------------------------------------------------------------------

SOFT_MUTATIONS = {
    "p": "b",
    "t": "d",
    "c": "g",
    "b": "v",
    "d": "dh",
    "m": "v",
}


def apply_soft_mutation(word: str) -> str:
    """
    Aplica mutação consonantal suave na primeira consoante da palavra.
    Usada em síndarin após artigos e certas preposições.
    """
    if not word:
        return word
    first_char = word[0]
    # Verificar dígrafo "dh" é evitado (já é mutado)
    if word[:3] == "dh-":
        return word
    mutated = SOFT_MUTATIONS.get(first_char)
    if mutated:
        return mutated + word[1:]
    return word


# ---------------------------------------------------------------------------
# Aliases para compatibilidade com o código anterior
# ---------------------------------------------------------------------------

def apply_basic_article_rules_pt_to_sindarin(word: str) -> str:
    return apply_article_rules_pt_to_sd(word)


def apply_basic_article_rules_sindarin_to_pt(word: str) -> str:
    return apply_article_rules_sd_to_pt(word)