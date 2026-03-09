# Notas de Gramática Síndarin

> Arquivo de referência com decisões linguísticas tomadas no projeto  
> e fontes utilizadas para construção do léxico.

---

## Fontes do Léxico

- **Tolkien Gateway**: https://tolkiengateway.net/wiki/Main_Page  
- **Eldamo (base lexical completa)**: https://eldamo.org/  
- **Sindarin em Eldamo**: https://eldamo.org/content/language-pages/lang-s.html  
- **Ardalambion**: https://ardalambion.org/

---

## Artigos

O síndarin usa um único artigo definido para singular e plural:

| Português | Síndarin |
|-----------|----------|
| o / a     | i        |
| os / as   | in       |

Não há artigo indefinido consagrado em síndarin. Palavras sem artigo são consideradas indefinidas.

---

## Preposições

Mapeamento simplificado adotado neste projeto:

| Português | Síndarin | Notas |
|-----------|----------|-------|
| de/do/da  | o        | Preposição genitiva básica |
| em/no/na  | mi       | Locativa interior |
| para      | na       | Direcional |
| com       | be       | Comitativa |
| por       | na       | Aproximado; mesmo radical de "para" |
| sem       | av       | Privativa |
| sob       | di       | Inferior |
| sobre     | or       | Superior |
| entre     | imbi     | |

> ⚠️ Preposições em síndarin são complexas e dependem de contexto. Os mapeamentos acima são simplificações para fins de MVP.

---

## Mutação Consonantal Suave

O síndarin tem um sistema de mutações nas consoantes iniciais de palavras dependendo de contexto gramatical. A **mutação suave** é a mais frequente.

| Consoante original | Após mutação suave |
|--------------------|--------------------|
| p                  | b                  |
| t                  | d                  |
| c                  | g                  |
| b                  | v                  |
| d                  | dh                 |
| m                  | v                  |
| g                  | ∅ (some)           |

**Quando aplicar**: após o artigo `i`, certas preposições e em construções genitivas.

Neste projeto, a mutação está disponível como função auxiliar (`apply_soft_mutation`), mas **não é aplicada automaticamente** no pipeline principal para evitar erros de contexto. Será ativada progressivamente nas versões futuras.

---

## Plural

O síndarin forma o plural através de **mutação vocálica interna** (similar ao sistema de "umlaut" germânico), não simplesmente adicionando "s":

- `edhel` (elfo) → `edhil` (elfos)
- `adan` (homem) → `edain` (homens)
- `orod` (montanha) → `ered` (montanhas)

Para o MVP, os plurais mais comuns estão cadastrados diretamente no léxico. O código também tenta remover o "s" final do português para buscar o singular.

---

## Estrutura do Léxico

Cada entrada do JSON segue o formato:

```json
"palavra_em_portugues": {
  "sindarin": "tradução_síndarin",
  "classe": "categoria_gramatical"
}
```

Categorias gramaticais usadas: `substantivo`, `verbo`, `adjetivo`, `preposição`, `conjunção`, `numeral`, `pronome`, `interjeição`.

---

## Limitações do Projeto

- Tradução é principalmente palavra por palavra, sem análise sintática
- Não contempla todos os fenômenos da gramática síndarin
- Neologismos não são gerados automaticamente
- Frases longas e idiomáticas podem não fazer sentido em síndarin
- A ortografia síndarin usada é baseada em fontes comunitárias (Tolkien não documentou tudo)
