"""Tests pour le registre de macros et leur expansion."""
import pytest
from src.workers.chat.kernel.ast import (
    Assign, Call, Program, Seq, String, Var,
)
from src.workers.chat.kernel.macros import MacroRegistry, macros


class TestMacroRegistry:
    def setup_method(self):
        self.reg = MacroRegistry()

    def test_has_returns_false_for_unknown(self):
        assert not self.reg.has("unknown")

    def test_register_and_has(self):
        self.reg.register("noop", lambda args: Call("noop", []))
        assert self.reg.has("noop")

    def test_expand_leaf_unchanged(self):
        node = String("hello")
        assert self.reg.expand(node) == node

    def test_expand_call_no_macro(self):
        node = Call("click", [String("left")])
        assert self.reg.expand(node) == node

    def test_expand_registered_macro(self):
        self.reg.register("double_click", lambda args: Seq([
            Call("click", [String("left")]),
            Call("click", [String("left")]),
        ]))
        expanded = self.reg.expand(Call("double_click", []))
        assert isinstance(expanded, Seq)
        assert len(expanded.steps) == 2

    def test_expand_program(self):
        self.reg.register("noop", lambda args: Call("click", []))
        prog = Program(Call("noop", []))
        result = self.reg.expand(prog)
        assert isinstance(result, Program)
        assert isinstance(result.body, Call)
        assert result.body.name == "click"

    def test_expand_seq_recursively(self):
        self.reg.register("greet", lambda args: Call("type_text", [String("hi")]))
        seq = Seq([Call("greet", []), Call("click", [])])
        result = self.reg.expand(seq)
        assert isinstance(result.steps[0], Call)
        assert result.steps[0].name == "type_text"


class TestBuiltinMacros:
    def test_click_on_registered(self):
        assert macros.has("click_on")

    def test_open_app_registered(self):
        assert macros.has("open_app")

    def test_click_on_expands_to_seq(self):
        call = Call("click_on", [String("Spotify")])
        result = macros.expand(call)
        assert isinstance(result, Seq)
        assert len(result.steps) == 3

    def test_click_on_first_step_is_assign(self):
        call = Call("click_on", [String("Spotify")])
        result = macros.expand(call)
        assert isinstance(result.steps[0], Assign)
        assert result.steps[0].var == "box"

    def test_click_on_last_step_is_click(self):
        call = Call("click_on", [String("Spotify")])
        result = macros.expand(call)
        last = result.steps[2]
        assert isinstance(last, Call)
        assert last.name == "click"

    def test_open_app_first_step_press_super(self):
        call = Call("open_app", [String("spotify")])
        result = macros.expand(call)
        assert isinstance(result, Seq)
        first = result.steps[0]
        assert isinstance(first, Call)
        assert first.name == "press_key"
        assert first.args[0] == String("super")
