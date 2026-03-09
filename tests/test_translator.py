import sys
import os
import pytest

# Garante importação a partir da raiz do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from translator import SindarinTranslator

@pytest.fixture
def t():
    return SindarinTranslator(lexicon_path="data/pt-sindarin.json")


# ---- Palavra simples -------------------------------------------------------

def test_palavra_simples_amigo(t):
    assert t.translate_pt_to_sd("amigo") == "mellon"

def test_palavra_simples_rei(t):
    assert t.translate_pt_to_sd("rei") == "aran"

def test_palavra_simples_estrela(t):
    assert t.translate_pt_to_sd("estrela") == "elen"


# ---- Frase com artigo ------------------------------------------------------

def test_artigo_o(t):
    assert t.translate_pt_to_sd("o rei") == "i aran"

def test_artigo_a(t):
    assert t.translate_pt_to_sd("a estrela") == "i elen"

def test_artigo_plural(t):
    assert t.translate_pt_to_sd("os elfos") == "in edhil"


# ---- Frase com preposição --------------------------------------------------

def test_prep_de(t):
    result = t.translate_pt_to_sd("de")
    assert result == "o"

def test_frase_com_preposicao(t):
    result = t.translate_pt_to_sd("o amigo da estrela")
    # "o"→i, "amigo"→mellon, "da"→o, "estrela"→elen → "i mellon o elen"
    assert result == "i mellon o elen"


# ---- Palavra desconhecida --------------------------------------------------

def test_palavra_desconhecida(t):
    result = t.translate_pt_to_sd("computador")
    assert result == "[computador]"

def test_frase_com_desconhecida(t):
    result = t.translate_pt_to_sd("o computador do rei")
    assert "[computador]" in result
    assert "aran" in result


# ---- String vazia e edge cases ---------------------------------------------

def test_string_vazia(t):
    assert t.translate_pt_to_sd("") == ""

def test_espacos_extras(t):
    result = t.translate_pt_to_sd("  amigo  ")
    assert result == "mellon"

def test_maiusculas(t):
    assert t.translate_pt_to_sd("AMIGO") == "mellon"


# ---- Tradução inversa SD → PT ----------------------------------------------

def test_inversa_mellon(t):
    assert t.translate_sd_to_pt("mellon") == "amigo"

def test_inversa_aran(t):
    assert t.translate_sd_to_pt("aran") == "rei"

def test_inversa_artigo_i(t):
    assert t.translate_sd_to_pt("i") == "o/a"

def test_inversa_artigo_in(t):
    assert t.translate_sd_to_pt("in") == "os/as"

def test_inversa_string_vazia(t):
    assert t.translate_sd_to_pt("") == ""
