import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lexicon import load_lexicon, load_lexicon_rich, invert_lexicon


LEXICON_PATH = "data/pt-sindarin.json"


# ---- Carregamento ----------------------------------------------------------

def test_lexicon_carrega():
    lex = load_lexicon(LEXICON_PATH)
    assert isinstance(lex, dict)
    assert len(lex) > 0

def test_lexicon_rich_carrega():
    rich = load_lexicon_rich(LEXICON_PATH)
    assert isinstance(rich, dict)
    assert len(rich) > 0

def test_lexicon_retorna_string():
    lex = load_lexicon(LEXICON_PATH)
    for pt, sd in lex.items():
        assert isinstance(sd, str), f"Valor de '{pt}' não é string: {sd}"


# ---- Entradas conhecidas ---------------------------------------------------

def test_amigo_esta_no_lexico():
    lex = load_lexicon(LEXICON_PATH)
    assert "amigo" in lex
    assert lex["amigo"] == "mellon"

def test_rei_esta_no_lexico():
    lex = load_lexicon(LEXICON_PATH)
    assert "rei" in lex
    assert lex["rei"] == "aran"

def test_estrela_esta_no_lexico():
    lex = load_lexicon(LEXICON_PATH)
    assert "estrela" in lex
    assert lex["estrela"] == "elen"


# ---- Estrutura rica --------------------------------------------------------

def test_rich_tem_campo_sindarin():
    rich = load_lexicon_rich(LEXICON_PATH)
    for word, entry in rich.items():
        assert "sindarin" in entry, f"'{word}' sem campo 'sindarin'"

def test_rich_tem_campo_classe():
    rich = load_lexicon_rich(LEXICON_PATH)
    for word, entry in rich.items():
        assert "classe" in entry, f"'{word}' sem campo 'classe'"


# ---- Inversão --------------------------------------------------------------

def test_inversao_basica():
    lex = load_lexicon(LEXICON_PATH)
    inv = invert_lexicon(lex)
    assert isinstance(inv, dict)
    assert "mellon" in inv
    assert inv["mellon"] == "amigo"

def test_inversao_sem_duplicatas_na_chave():
    lex = load_lexicon(LEXICON_PATH)
    inv = invert_lexicon(lex)
    # Todas as chaves do léxico invertido devem ser strings
    for sd in inv:
        assert isinstance(sd, str)
