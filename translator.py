from lexicon import load_lexicon, invert_lexicon
from rules import (
    normalize_text,
    tokenize,
    apply_article_rules_pt_to_sd,
    apply_article_rules_sd_to_pt,
    apply_preposition_rules_pt_to_sd,
    strip_plural_pt,
)


class SindarinTranslator:
    def __init__(self, lexicon_path: str = "data/pt-sindarin.json"):
        self.pt_to_sd = load_lexicon(lexicon_path)
        self.sd_to_pt = invert_lexicon(self.pt_to_sd)

    # ------------------------------------------------------------------
    # Português → Sindarin
    # ------------------------------------------------------------------

    def translate_pt_to_sd(self, text: str) -> str:
        text = normalize_text(text)
        tokens = tokenize(text)
        result = []

        for token in tokens:
            translated = self._translate_word_pt_to_sd(token)
            result.append(translated)

        return " ".join(result)

    def _translate_word_pt_to_sd(self, word: str) -> str:
        # 1. Artigo
        article = apply_article_rules_pt_to_sd(word)
        if article != word:
            return article

        # 2. Preposição
        prep = apply_preposition_rules_pt_to_sd(word)
        if prep != word:
            return prep

        # 3. Busca direta no léxico
        if word in self.pt_to_sd:
            return self.pt_to_sd[word]

        # 4. Tentativa com singular (plural heurístico)
        singular, is_plural = strip_plural_pt(word)
        if is_plural and singular in self.pt_to_sd:
            return self.pt_to_sd[singular]

        # 5. Palavra desconhecida — marcada com colchetes
        return f"[{word}]"

    # ------------------------------------------------------------------
    # Sindarin → Português
    # ------------------------------------------------------------------

    def translate_sd_to_pt(self, text: str) -> str:
        text = normalize_text(text)
        tokens = tokenize(text)
        result = []

        for token in tokens:
            # Artigo sindarin
            article = apply_article_rules_sd_to_pt(token)
            if article != token:
                result.append(article)
                continue

            # Busca no léxico invertido
            translated = self.sd_to_pt.get(token, token)
            result.append(translated)

        return " ".join(result)