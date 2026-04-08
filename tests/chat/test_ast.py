"""Tests pour les nœuds AST et les fonctions de sérialisation."""
import pytest
from src.workers.chat.kernel.ast import (
    Assign, Call, Number, Program, Seq, String, Symbol, Var,
    to_sexpr, to_dict,
)


class TestToSexpr:
    def test_string(self):
        assert to_sexpr(String("hello")) == '"hello"'

    def test_string_escapes_quotes(self):
        assert to_sexpr(String('say "hi"')) == '"say \\"hi\\""'

    def test_number_int(self):
        assert to_sexpr(Number(42)) == "42"

    def test_number_float(self):
        assert to_sexpr(Number(1.5)) == "1.5"

    def test_symbol(self):
        assert to_sexpr(Symbol("left")) == "left"

    def test_var(self):
        assert to_sexpr(Var("box")) == "box"

    def test_call_no_args(self):
        assert to_sexpr(Call("click", [])) == "(click)"

    def test_call_with_args(self):
        assert to_sexpr(Call("find", [String("Spotify")])) == '(find "Spotify")'

    def test_seq(self):
        node = Seq([Call("a", []), Call("b", [])])
        assert to_sexpr(node) == "(seq (a) (b))"

    def test_assign(self):
        node = Assign("box", Call("find", [String("X")]))
        assert to_sexpr(node) == '(assign box (find "X"))'

    def test_program_unwraps(self):
        prog = Program(Call("click", [String("left")]))
        assert to_sexpr(prog) == '(click "left")'

    def test_unknown_node_raises(self):
        from src.workers.chat.kernel.ast import Node
        with pytest.raises(TypeError):
            to_sexpr(Node())


class TestToDict:
    def test_string(self):
        assert to_dict(String("hello")) == {"type": "String", "value": "hello"}

    def test_number(self):
        assert to_dict(Number(3)) == {"type": "Number", "value": 3}

    def test_var(self):
        assert to_dict(Var("x")) == {"type": "Var", "name": "x"}

    def test_symbol(self):
        assert to_dict(Symbol("left")) == {"type": "Symbol", "name": "left"}

    def test_call(self):
        node = Call("find", [String("Spotify")])
        d = to_dict(node)
        assert d["type"] == "Call"
        assert d["name"] == "find"
        assert d["args"] == [{"type": "String", "value": "Spotify"}]

    def test_seq(self):
        node = Seq([Call("a", []), Call("b", [])])
        d = to_dict(node)
        assert d["type"] == "Seq"
        assert len(d["steps"]) == 2

    def test_program(self):
        prog = Program(Call("click", []))
        d = to_dict(prog)
        assert d["type"] == "Program"
        assert d["body"]["type"] == "Call"
