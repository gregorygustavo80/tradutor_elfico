# 🧝 Tradutor Português ↔ Síndarin

Tradutor experimental bidirecional entre **português brasileiro** e **síndarin**, a língua dos elfos de J. R. R. Tolkien. Baseado em léxico estruturado e regras linguísticas básicas.

---

## ✨ Funcionalidades

- Tradução de **português → síndarin**
- Tradução de **síndarin → português**
- Suporte a artigos (`o/a → i`, `os/as → in`)
- Suporte a preposições comuns (`de → o`, `em → mi`, `para → na`, ...)
- Reconhecimento de plural heurístico em português
- Marcação de palavras desconhecidas com `[colchetes]`
- Léxico expandido com **centenas de entradas** extraídas do banco de dados **Eldamo** e do léxico artesanal
- Validador de consistência do léxico
- Testes automatizados com `pytest`

---

## 🚀 Como executar

### Pré-requisitos

- Python 3.9 ou superior

### Instalação

```bash
pip install -r requirements.txt
```

### Rodar o tradutor interativo

```bash
python app.py
```

O menu oferece:
```
=== Tradutor Português ↔ Sindarin ===
1 - Português para Sindarin
2 - Sindarin para Português
0 - Sair
```

### Validar o léxico

```bash
python validator.py
```

### Rodar os testes

```bash
python -m pytest tests/ -v
```

---

## 🗄️ Banco de Dados Eldamo

O léxico Síndarin deste projeto é enriquecido automaticamente com dados do **[Eldamo — Base Lexical Eldarin](https://eldamo.org/)**, o mais completo banco de dados público das línguas inventadas por Tolkien.

### Como funciona

1. O arquivo `eldamo-data.xml` (baixado de [eldamo.org](https://eldamo.org/)) contém milhares de entradas das línguas Eldarin.
2. O script `import_eldamo.py` filtra apenas as entradas **Síndarin** (`l='s'`), ignora entradas depreciadas e tenta traduzir os glosses do inglês para o português via dicionário interno.
3. As entradas do Eldamo são **mescladas** com o léxico artesanal (`pt-sindarin-handcrafted.json`), que **sempre tem prioridade** em caso de conflito.
4. O resultado final é salvo em `data/pt-sindarin.json` e usado pelo tradutor.

### Executar a importação

```bash
python import_eldamo.py
```

> **Nota:** O arquivo `eldamo-data.xml` deve estar presente na raiz do projeto. Ele pode ser baixado em: https://eldamo.org/content/language-index/language-index.html

### Estratégia de mesclagem

| Fonte | Prioridade | Descrição |
|---|---|---|
| `pt-sindarin-handcrafted.json` | **Alta** | Léxico artesanal revisado manualmente |
| `eldamo-data.xml` | Normal | Entradas automáticas do banco Eldamo |

Entradas do Eldamo **só são adicionadas** se a palavra portuguesa ainda não existir no léxico artesanal.

---

## 📖 Exemplos

| Português          | Síndarin          |
|--------------------|-------------------|
| amigo              | mellon            |
| rei                | aran              |
| estrela            | elen              |
| o rei              | i aran            |
| os elfos           | in edhil          |
| o amigo da estrela | i mellon o elen   |
| computador         | [computador]      |

---

## 📁 Estrutura do projeto

```
tradutor_sindarin/
├── app.py                        # Interface de terminal
├── translator.py                 # Pipeline principal de tradução
├── lexicon.py                    # Carregamento e inversão do léxico
├── rules.py                      # Normalização, artigos, preposições, mutações
├── validator.py                  # Validador de consistência do léxico
├── import_eldamo.py              # Importador do banco de dados Eldamo
├── explore_eldamo.py             # Explorador/diagnóstico do XML Eldamo
├── eldamo-data.xml               # Banco de dados Eldamo (baixar separadamente)
├── data/
│   ├── pt-sindarin.json          # Dicionário final mesclado (gerado)
│   └── pt-sindarin-handcrafted.json  # Léxico artesanal (fonte da verdade)
├── tests/
│   ├── test_translator.py
│   ├── test_rules.py
│   └── test_lexicon.py
├── docs/
│   └── grammar_notes.md          # Notas linguísticas e fontes
├── requirements.txt
└── README.md
```

---

## ⚠️ Limitações

- Tradução palavra por palavra — não há análise sintática
- Frases longas ou idiomáticas podem gerar resultados estranhos
- Mutação consonantal disponível, mas não aplicada automaticamente
- Cobertura do Eldamo limitada pela qualidade dos glosses traduzíveis
- Não é um tradutor acadêmico — é um projeto experimental temático

---

## 🗺️ Roadmap

- [x] Integração com banco de dados Eldamo (importação automática de XML)
- [x] Mesclagem inteligente com léxico artesanal (prioridade manual)
- [ ] Mutações consonantais contextuais e API REST
- [ ] v1.0: Interface web, histórico de traduções, sugestões alternativas
- [ ] Futuro: Exportação para Tengwar, painel de administração do léxico

---

## 📚 Fontes

- [Tolkien Gateway](https://tolkiengateway.net/wiki/Main_Page)
- [Eldamo — Base Lexical Eldarin](https://eldamo.org/)
- [Síndarin em Eldamo](https://eldamo.org/content/language-pages/lang-s.html)
- [Ardalambion](https://ardalambion.org/)

---

> *"Elen síla lúmenn' omentielvo"* — Uma estrela brilha na hora do nosso encontro.  
> — J. R. R. Tolkien, *O Senhor dos Anéis*
