"""
Simple French spell-checker with a custom tech/app vocabulary.
The vocabulary is stored in vocab.json next to this file and can be
edited at runtime via the UI (Dictionnaire tab).
"""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

from spellchecker import SpellChecker

# ── Vocabulary file ───────────────────────────────────────────────────────────

VOCAB_FILE = Path(__file__).with_name("vocab.json")


def get_vocab() -> List[str]:
    """Return the current custom vocabulary loaded from vocab.json."""
    return json.loads(VOCAB_FILE.read_text(encoding="utf-8"))["custom_vocab"]


def save_vocab(words: List[str]) -> None:
    """Persist *words* to vocab.json (sorted, deduplicated, lower-case)."""
    data = {"custom_vocab": sorted(set(w.lower().strip() for w in words if w.strip()))}
    VOCAB_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    # Invalidate the cached SpellChecker so it picks up the new words.
    global _spell
    _spell = None

# ── Spell-checker instance (lazy) ────────────────────────────────────────────
_spell: SpellChecker | None = None


def _get_spell() -> SpellChecker:
    global _spell
    if _spell is None:
        _spell = SpellChecker(language="fr")
        _spell.word_frequency.load_words(get_vocab())
    return _spell


# ── Public types ─────────────────────────────────────────────────────────────
@dataclass
class Change:
    original: str
    corrected: str


@dataclass
class CorrectionResult:
    original: str
    corrected: str
    changes: List[Change] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    def __str__(self) -> str:
        if not self.has_changes:
            return f"Correction : aucune modification ({self.original!r})"
        lines = [f"Correction : {self.original!r}  →  {self.corrected!r}", ""]
        for c in self.changes:
            lines.append(f"  {c.original!r:<20} →  {c.corrected!r}")
        return "\n".join(lines)


# ── Core function ─────────────────────────────────────────────────────────────
_WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+")


def correct_text(text: str) -> CorrectionResult:
    """
    Return a CorrectionResult with individual word corrections applied.

    Rules:
    - Capitalised words (proper nouns, start-of-sentence) are left untouched.
    - Words already known to the French dictionary are left untouched.
    - Unknown words get the best candidate if one is found; otherwise kept as-is.
    """
    spell = _get_spell()
    changes: List[Change] = []
    result = text

    # Collect all word spans in reverse order so replacements don't shift indices
    spans: List[Tuple[int, int, str]] = []
    for m in _WORD_RE.finditer(text):
        word = m.group()
        lower = word.lower()

        # Skip already-known words and capitalised words
        if lower in spell or word[0].isupper():
            continue

        candidate = spell.correction(lower)
        if candidate and candidate != lower:
            spans.append((m.start(), m.end(), candidate))
            changes.append(Change(original=word, corrected=candidate))

    # Apply replacements from right to left to preserve indices
    for start, end, replacement in reversed(spans):
        result = result[:start] + replacement + result[end:]

    return CorrectionResult(original=text, corrected=result, changes=changes)
