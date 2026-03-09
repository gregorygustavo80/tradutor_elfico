import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rules import (
    normalize_text,
    tokenize,
    apply_article_rules_pt_to_sd,
    apply_article_rules_sd_to_pt,
    apply_preposition_rules_pt_to_sd,
    strip_plural_pt,
    apply_soft_mutation,
)


# ---- Normalização ----------------------------------------------------------

def test_normalize_minusculas():
    assert normalize_text("OLÁ MUNDO") == "olá mundo"

def test_normalize_pontuacao():
    assert normalize_text("O Rei, da Noite!") == "o rei da noite"

def test_normalize_espacos():
    assert normalize_text("  olá   mundo  ") == "olá mundo"


# ---- Tokenização -----------------------------------------------------------

def test_tokenize_simples():
    assert tokenize("olá mundo") == ["olá", "mundo"]

def test_tokenize_string_vazia():
    assert tokenize("") == []

def test_tokenize_um_token():
    assert tokenize("mellon") == ["mellon"]


# ---- Artigos PT → SD -------------------------------------------------------

def test_artigo_o():
    assert apply_article_rules_pt_to_sd("o") == "i"

def test_artigo_a():
    assert apply_article_rules_pt_to_sd("a") == "i"

def test_artigo_os():
    assert apply_article_rules_pt_to_sd("os") == "in"

def test_artigo_as():
    assert apply_article_rules_pt_to_sd("as") == "in"

def test_nao_artigo():
    assert apply_article_rules_pt_to_sd("rei") == "rei"


# ---- Artigos SD → PT -------------------------------------------------------

def test_artigo_sd_i():
    assert apply_article_rules_sd_to_pt("i") == "o/a"

def test_artigo_sd_in():
    assert apply_article_rules_sd_to_pt("in") == "os/as"


# ---- Preposições -----------------------------------------------------------

def test_prep_de():
    assert apply_preposition_rules_pt_to_sd("de") == "o"

def test_prep_em():
    assert apply_preposition_rules_pt_to_sd("em") == "mi"

def test_prep_para():
    assert apply_preposition_rules_pt_to_sd("para") == "na"

def test_prep_com():
    assert apply_preposition_rules_pt_to_sd("com") == "be"

def test_prep_desconhecida():
    assert apply_preposition_rules_pt_to_sd("xyz") == "xyz"


# ---- Plural heurístico -----------------------------------------------------

def test_plural_s():
    singular, is_plural = strip_plural_pt("amigos")
    assert singular == "amigo"
    assert is_plural is True

def test_plural_oes():
    singular, is_plural = strip_plural_pt("canções")
    assert singular == "canção"
    assert is_plural is True

def test_nao_plural():
    singular, is_plural = strip_plural_pt("amigo")
    assert singular == "amigo"
    assert is_plural is False


# ---- Mutação consonantal ---------------------------------------------------

def test_mutacao_p():
    assert apply_soft_mutation("pedo") == "bedo"

def test_mutacao_t():
    assert apply_soft_mutation("taur") == "daur"

def test_mutacao_c():
    assert apply_soft_mutation("coron") == "goron"

def test_sem_mutacao():
    # "elen" começa com vogal — não sofre mutação consonantal
    assert apply_soft_mutation("elen") == "elen"
