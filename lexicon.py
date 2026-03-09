import json
from pathlib import Path


def load_lexicon(path: str = "data/pt-sindarin.json") -> dict:
    """
    Carrega o léxico do arquivo JSON. Suporta tanto o formato simples
    {"pt": "sd"} quanto o formato rico {"pt": {"sindarin": "sd", "classe": "..."}}.
    Retorna sempre um dicionário plano {pt: sd}.
    """
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    lexicon = {}
    for pt_word, value in raw.items():
        if isinstance(value, dict):
            lexicon[pt_word] = value.get("sindarin", f"[{pt_word}]")
        else:
            lexicon[pt_word] = value
    return lexicon


def load_lexicon_rich(path: str = "data/pt-sindarin.json") -> dict:
    """
    Carrega o léxico completo com metadados (sindarin, classe, etc.).
    """
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def invert_lexicon(lexicon: dict) -> dict:
    """
    Inverte o léxico plano: {pt: sd} → {sd: pt}.
    Em caso de conflito (duas palavras PT com mesma tradução SD),
    mantém a primeira encontrada.
    """
    reversed_dict = {}
    for pt, sd in lexicon.items():
        if sd not in reversed_dict:
            reversed_dict[sd] = pt
    return reversed_dict