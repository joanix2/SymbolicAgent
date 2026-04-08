import spacy
from dataclasses import dataclass
from typing import List

from .correction import CorrectionResult, correct_text

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("fr_core_news_sm")
    return _nlp


@dataclass
class Token:
    text: str
    lemma: str
    pos: str
    dep: str


@dataclass
class ParseResult:
    raw: str
    tokens: List[Token]
    correction: CorrectionResult | None = None

    def __str__(self) -> str:
        lines = []
        if self.correction and self.correction.has_changes:
            lines.append(str(self.correction))
            lines.append("")
        lines.append(f"Texte : {self.raw!r}")
        lines.append("")
        header = f"{'Mot':<20} {'Lemme':<20} {'POS':<10} {'Dépendance'}"
        lines.append(header)
        lines.append("-" * len(header))
        for t in self.tokens:
            lines.append(f"{t.text:<20} {t.lemma:<20} {t.pos:<10} {t.dep}")
        return "\n".join(lines)


def parse(text: str) -> ParseResult:
    nlp = _get_nlp()
    correction = correct_text(text)
    doc = nlp(correction.corrected)
    tokens = [
        Token(text=tok.text, lemma=tok.lemma_, pos=tok.pos_, dep=tok.dep_)
        for tok in doc
        if not tok.is_space
    ]
    return ParseResult(raw=correction.corrected, tokens=tokens, correction=correction)
