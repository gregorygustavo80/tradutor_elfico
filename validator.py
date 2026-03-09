import sys
import json
from pathlib import Path

# Evita erros de encoding no terminal Windows
reconfigure = getattr(sys.stdout, "reconfigure", None)
if callable(reconfigure):
    reconfigure(encoding="utf-8", errors="replace")


def validate_lexicon(path: str = "data/pt-sindarin.json") -> dict:
    """
    Valida o arquivo de léxico e retorna um relatório com:
    - total de entradas
    - entradas sem campo 'sindarin'
    - entradas com 'sindarin' vazio
    - entradas sem campo 'classe'
    - possíveis duplicatas de tradução sindarin
    """
    file_path = Path(path)
    if not file_path.exists():
        return {"erro": f"Arquivo nao encontrado: {path}"}

    with file_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    sem_sindarin = []
    sindarin_vazio = []
    sem_classe = []
    sd_values = {}

    for pt_word, value in raw.items():
        if not isinstance(value, dict):
            sem_sindarin.append(pt_word)
            continue

        sd = value.get("sindarin", "")
        classe = value.get("classe", "")

        if not sd:
            sindarin_vazio.append(pt_word)
        else:
            if sd in sd_values:
                sd_values[sd].append(pt_word)
            else:
                sd_values[sd] = [pt_word]

        if not classe:
            sem_classe.append(pt_word)

    duplicatas = {sd: words for sd, words in sd_values.items() if len(words) > 1}

    report = {
        "total_entradas": len(raw),
        "sem_campo_sindarin": sem_sindarin,
        "sindarin_vazio": sindarin_vazio,
        "sem_classe_gramatical": sem_classe,
        "duplicatas_sindarin": duplicatas,
    }
    return report


def print_report(report: dict):
    print("\n=== Relatorio de Validacao do Lexico ===")
    print(f"Total de entradas: {report.get('total_entradas', 0)}")

    sem_sd = report.get("sem_campo_sindarin", [])
    print(f"\nEntradas sem campo 'sindarin': {len(sem_sd)}")
    for w in sem_sd:
        print(f"  - {w}")

    sd_vazio = report.get("sindarin_vazio", [])
    print(f"\nEntradas com 'sindarin' vazio: {len(sd_vazio)}")
    for w in sd_vazio:
        print(f"  - {w}")

    sem_classe = report.get("sem_classe_gramatical", [])
    print(f"\nEntradas sem classe gramatical: {len(sem_classe)}")
    for w in sem_classe:
        print(f"  - {w}")

    duplicatas = report.get("duplicatas_sindarin", {})
    print(f"\nDuplicatas de traducao sindarin: {len(duplicatas)}")
    for sd, words in duplicatas.items():
        print(f"  '{sd}' => {words}")

    print("\n========================================")


if __name__ == "__main__":
    report = validate_lexicon()
    print_report(report)
