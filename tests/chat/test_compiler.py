"""Tests pour la grammaire Lark et le compilateur NL→DSL."""
import pytest
from src.workers.chat.kernel.grammar import canonical_parser
from src.workers.chat.kernel.ast import Call, Program, Seq, String
from src.workers.chat.kernel.compiler import (
    compile_intent, compile_text, parse_nl_to_program,
)
from src.workers.chat.kernel.intent import Intent


# ── Grammar ───────────────────────────────────────────────────────────────────

class TestCanonicalParser:
    def test_single_call(self):
        prog = canonical_parser.parse('click_on("Spotify")')
        assert isinstance(prog, Program)
        seq = prog.body
        assert isinstance(seq, Seq)
        assert len(seq.steps) == 1
        call = seq.steps[0]
        assert isinstance(call, Call)
        assert call.name == "click_on"
        assert call.args == [String("Spotify")]

    def test_two_calls(self):
        prog = canonical_parser.parse('click_on("Spotify"); press_key("enter")')
        assert len(prog.body.steps) == 2

    def test_no_args(self):
        prog = canonical_parser.parse("click()")
        call = prog.body.steps[0]
        assert call.name == "click"
        assert call.args == []

    def test_trailing_semicolon(self):
        prog = canonical_parser.parse('click_on("A");')
        assert len(prog.body.steps) == 1

    def test_invalid_syntax_raises(self):
        from lark.exceptions import UnexpectedInput
        with pytest.raises(UnexpectedInput):
            canonical_parser.parse("not valid !!!")


# ── Compiler ─────────────────────────────────────────────────────────────────

class TestCompileIntent:
    def test_click_on(self):
        intent = Intent("click_on", {"target": "Spotify"}, "clique sur Spotify")
        assert compile_intent(intent) == 'click_on("Spotify")'

    def test_press_key(self):
        intent = Intent("press_key", {"key": "enter"}, "appuie sur enter")
        assert compile_intent(intent) == 'press_key("enter")'

    def test_type_text(self):
        intent = Intent("type_text", {"text": "bonjour"}, "écris bonjour")
        assert compile_intent(intent) == 'type_text("bonjour")'

    def test_unknown_action_raises(self):
        intent = Intent("fly_to", {}, "")
        with pytest.raises(ValueError):
            compile_intent(intent)


class TestCompileText:
    def test_single_command(self):
        canonical, intents = compile_text("clique sur Spotify")
        assert canonical == 'click_on("Spotify")'
        assert len(intents) == 1

    def test_multiple_commands(self):
        canonical, intents = compile_text("clique sur Spotify, appuie sur enter")
        assert len(intents) == 2
        assert 'click_on("Spotify")' in canonical
        assert 'press_key("enter")' in canonical

    def test_puis_connector(self):
        _, intents = compile_text("clique sur A puis clique sur B")
        assert len(intents) == 2

    def test_unknown_command_raises(self):
        with pytest.raises(ValueError):
            compile_text("fais quelque chose")


class TestParseNlToProgram:
    def test_returns_three_tuple(self):
        result = parse_nl_to_program("clique sur Spotify")
        assert len(result) == 3

    def test_canonical_string(self):
        canonical, _, _ = parse_nl_to_program("clique sur Spotify")
        assert 'click_on("Spotify")' in canonical

    def test_program_is_program_instance(self):
        _, program, _ = parse_nl_to_program("clique sur Spotify")
        assert isinstance(program, Program)

    def test_multi_step_sequence(self):
        _, program, intents = parse_nl_to_program(
            "clique sur Spotify, appuie sur enter"
        )
        assert len(intents) == 2
        assert len(program.body.steps) == 2
