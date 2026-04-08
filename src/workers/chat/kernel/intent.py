from __future__ import annotations

import re
from dataclasses import dataclass

from .nlp import _get_nlp


# ── Intent ────────────────────────────────────────────────────────────────────

@dataclass
class Intent:
    action: str
    slots: dict[str, str]
    source_text: str
    confidence: float = 1.0


# ── Segmentation ──────────────────────────────────────────────────────────────

def split_commands(text: str) -> list[str]:
    """Découpe une phrase en commandes élémentaires sur , ; et connecteurs."""
    text = re.sub(r"\b(puis|ensuite|après)\b", ",", text, flags=re.IGNORECASE)
    return [p.strip() for p in re.split(r"[,;]+", text) if p.strip()]


# ── Normalisation ─────────────────────────────────────────────────────────────

def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _strip_punctuation(text: str) -> str:
    return text.strip().strip(" .!?:")


def _extract_after(text: str, pattern: str) -> str:
    cleaned = _normalize_spaces(text)
    return _strip_punctuation(re.sub(pattern, "", cleaned, flags=re.IGNORECASE))


# ── Lemmatisation légère ──────────────────────────────────────────────────────

_LEMMA_FALLBACK: dict[str, str] = {
    "clique": "cliquer", "cliquer": "cliquer",
    "ouvre": "ouvrir",   "ouvrir": "ouvrir",
    "va": "aller",       "vais": "aller",    "aller": "aller",
    "appuie": "appuyer", "appuyer": "appuyer",
    "tape": "taper",     "taper": "taper",
    "écris": "écrire",   "ecris": "écrire",  "écrire": "écrire",
}


def lemmatize_text(text: str) -> list[str]:
    """Retourne les lemmes du texte (spaCy si disponible, sinon dictionnaire minimal)."""
    nlp = _get_nlp()
    if nlp is not None:
        return [
            (tok.lemma_ or tok.text).lower().strip()
            for tok in nlp(text)
            if not tok.is_space and (tok.lemma_ or tok.text).strip()
        ]
    # Fallback
    tokens = re.findall(r"\w+|[^\w\s]", _normalize_spaces(text.lower()), flags=re.UNICODE)
    return [_LEMMA_FALLBACK.get(tok, tok) for tok in tokens]


# ── Reconnaissance d'intentions ───────────────────────────────────────────────

def parse_intent(command: str) -> Intent | None:
    lemmas = lemmatize_text(command)
    lemma_text = " ".join(lemmas)
    source = _normalize_spaces(command)

    # clique / cliquer sur X
    if lemmas and lemmas[0] in ("cliquer", "clique", "click") and "sur" in lemmas:
        return Intent("click_on", {"target": _extract_after(source, r"^clique\s+sur\s+")}, command)

    # ouvre / ouvrir X
    if lemma_text.startswith("ouvrir "):
        return Intent("click_on", {"target": _extract_after(source, r"^ouvre\s+")}, command, confidence=0.9)

    # va / aller sur X
    if lemma_text.startswith("aller sur "):
        return Intent("click_on", {"target": _extract_after(source, r"^va\s+sur\s+")}, command, confidence=0.9)

    # appuie / appuyer sur X
    if lemmas and lemmas[0] in ("appuyer", "appuie") and "sur" in lemmas:
        return Intent("press_key", {"key": _extract_after(source, r"^appuie\s+sur\s+")}, command)

    # écris / écrire X
    if lemma_text.startswith("écrire ") or lemma_text.startswith("ecrire "):
        return Intent("type_text", {"text": _extract_after(source, r"^(écris|ecris)\s+")}, command)

    # tape / taper X
    if lemma_text.startswith("taper ") or lemma_text.startswith("tap "):
        return Intent("type_text", {"text": _extract_after(source, r"^tape\s+")}, command)

    return None
