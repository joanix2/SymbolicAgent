"""Tests pour le module de correction orthographique."""
import pytest
from src.workers.chat.kernel.correction import correct_text, Change, CorrectionResult


class TestCorrectText:
    def test_no_change_for_known_word(self):
        result = correct_text("clique")
        assert not result.has_changes
        assert result.corrected == "clique"

    def test_corrects_typo(self):
        result = correct_text("sptify")
        assert result.has_changes
        assert result.corrected == "spotify"

    def test_capitalised_word_untouched(self):
        # "Spotify" commence par une majuscule → pas touché
        result = correct_text("Spotify")
        assert not result.has_changes
        assert result.corrected == "Spotify"

    def test_custom_vocab_preserved(self):
        # "icon" est dans CUSTOM_VOCAB → aucune correction
        result = correct_text("icon")
        assert not result.has_changes

    def test_mixed_sentence(self):
        result = correct_text("click sur l icon sptify")
        # "sptify" → "spotify", le reste déjà connu
        assert any(c.corrected == "spotify" for c in result.changes)
        assert "spotify" in result.corrected

    def test_result_type(self):
        result = correct_text("bonjour")
        assert isinstance(result, CorrectionResult)

    def test_change_fields(self):
        result = correct_text("sptify")
        assert len(result.changes) == 1
        change = result.changes[0]
        assert isinstance(change, Change)
        assert change.original == "sptify"
        assert change.corrected == "spotify"

    def test_original_preserved_in_result(self):
        text = "sptify"
        result = correct_text(text)
        assert result.original == text

    def test_empty_string(self):
        result = correct_text("")
        assert result.corrected == ""
        assert not result.has_changes
