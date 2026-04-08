"""Tests pour la segmentation et la reconnaissance d'intentions."""
import pytest
from src.workers.chat.kernel.intent import split_commands, parse_intent, Intent


class TestSplitCommands:
    def test_comma(self):
        assert split_commands("a, b, c") == ["a", "b", "c"]

    def test_semicolon(self):
        assert split_commands("a; b") == ["a", "b"]

    def test_puis(self):
        parts = split_commands("clique sur A puis clique sur B")
        assert len(parts) == 2

    def test_ensuite(self):
        parts = split_commands("clique sur A ensuite clique sur B")
        assert len(parts) == 2

    def test_strips_whitespace(self):
        assert split_commands("  a  ,  b  ") == ["a", "b"]

    def test_single_command(self):
        assert split_commands("clique sur Spotify") == ["clique sur Spotify"]


class TestParseIntent:
    # ── click_on ──

    def test_clique_sur(self):
        intent = parse_intent("clique sur Spotify")
        assert intent is not None
        assert intent.action == "click_on"
        assert intent.slots["target"] == "Spotify"

    def test_clique_sur_majuscule(self):
        intent = parse_intent("Clique sur Firefox")
        assert intent is not None
        assert intent.action == "click_on"
        assert intent.slots["target"] == "Firefox"

    def test_ouvre(self):
        intent = parse_intent("ouvre Spotify")
        assert intent is not None
        assert intent.action == "click_on"
        assert intent.slots["target"] == "Spotify"
        assert intent.confidence < 1.0

    def test_va_sur(self):
        intent = parse_intent("va sur Discord")
        assert intent is not None
        assert intent.action == "click_on"
        assert intent.slots["target"] == "Discord"

    # ── press_key ──

    def test_appuie_sur(self):
        intent = parse_intent("appuie sur enter")
        assert intent is not None
        assert intent.action == "press_key"
        assert intent.slots["key"] == "enter"

    # ── type_text ──

    def test_ecris(self):
        intent = parse_intent("écris bonjour")
        assert intent is not None
        assert intent.action == "type_text"
        assert intent.slots["text"] == "bonjour"

    def test_tape(self):
        intent = parse_intent("tape hello world")
        assert intent is not None
        assert intent.action == "type_text"
        assert intent.slots["text"] == "hello world"

    # ── unknown ──

    def test_unknown_returns_none(self):
        assert parse_intent("fais quelque chose") is None

    def test_empty_returns_none(self):
        assert parse_intent("") is None

    # ── Intent dataclass ──

    def test_intent_default_confidence(self):
        intent = parse_intent("clique sur Spotify")
        assert intent.confidence == 1.0

    def test_intent_source_text(self):
        cmd = "clique sur Spotify"
        intent = parse_intent(cmd)
        assert intent.source_text == cmd
