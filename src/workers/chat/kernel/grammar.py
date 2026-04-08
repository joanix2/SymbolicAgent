from __future__ import annotations

import json
from pathlib import Path

from lark import Lark, Transformer

from .ast import (
    Assign, Call, Number, Program, Seq, String, Symbol, Var,
)

# ── Grammaire canonique ───────────────────────────────────────────────────────
# Forme attendue :  click_on("Spotify"); press_key("enter")

_GRAMMAR_FILE = Path(__file__).with_name("canonical.lark")
GRAMMAR = _GRAMMAR_FILE.read_text(encoding="utf-8")


class _CanonicalTransformer(Transformer):
    def start(self, items):
        return Program(items[0])

    def stmt_list(self, items):
        stmts = [item for item in items if not (isinstance(item, str) and item == ";")]
        return Seq(stmts)

    def call(self, items):
        name = str(items[0])
        args = items[1] if len(items) > 1 and items[1] is not None else []
        return Call(name=name, args=args)

    def arg_list(self, items):
        return list(items)

    def string(self, items):
        return String(value=json.loads(str(items[0])))

    def number(self, items):
        raw = str(items[0])
        return Number(value=float(raw) if "." in raw else int(raw))

    def symbol(self, items):
        return Symbol(name=str(items[0]))

    def var(self, items):
        return Var(name=str(items[0]))

    def NAME(self, tok):
        return str(tok)

    def SEP(self, tok):
        return str(tok)


canonical_parser = Lark(GRAMMAR, parser="lalr", transformer=_CanonicalTransformer())
