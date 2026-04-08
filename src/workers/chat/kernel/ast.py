from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


# ── Nœuds ────────────────────────────────────────────────────────────────────

@dataclass
class Node:
    pass


@dataclass
class String(Node):
    value: str


@dataclass
class Number(Node):
    value: float | int


@dataclass
class Symbol(Node):
    name: str


@dataclass
class Var(Node):
    name: str


@dataclass
class Call(Node):
    name: str
    args: list[Node]


@dataclass
class Seq(Node):
    steps: list[Node]


@dataclass
class Assign(Node):
    var: str
    value: Node


@dataclass
class Program(Node):
    body: Node


# ── Impression S-expression ───────────────────────────────────────────────────

def to_sexpr(node: Node) -> str:
    if isinstance(node, Program):
        return to_sexpr(node.body)
    if isinstance(node, Seq):
        return f"(seq {' '.join(to_sexpr(s) for s in node.steps)})"
    if isinstance(node, Assign):
        return f"(assign {node.var} {to_sexpr(node.value)})"
    if isinstance(node, Call):
        args = " ".join(to_sexpr(a) for a in node.args)
        return f"({node.name}{(' ' + args) if args else ''})"
    if isinstance(node, Var):
        return node.name
    if isinstance(node, Symbol):
        return node.name
    if isinstance(node, String):
        escaped = node.value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(node, Number):
        return str(node.value)
    raise TypeError(f"Type AST non géré : {type(node)!r}")


# ── Sérialisation dict/JSON ───────────────────────────────────────────────────

def to_dict(node: Node) -> Any:
    if isinstance(node, Program):
        return {"type": "Program", "body": to_dict(node.body)}
    if isinstance(node, Seq):
        return {"type": "Seq", "steps": [to_dict(x) for x in node.steps]}
    if isinstance(node, Assign):
        return {"type": "Assign", "var": node.var, "value": to_dict(node.value)}
    if isinstance(node, Call):
        return {"type": "Call", "name": node.name, "args": [to_dict(x) for x in node.args]}
    if isinstance(node, Var):
        return {"type": "Var", "name": node.name}
    if isinstance(node, Symbol):
        return {"type": "Symbol", "name": node.name}
    if isinstance(node, String):
        return {"type": "String", "value": node.value}
    if isinstance(node, Number):
        return {"type": "Number", "value": node.value}
    raise TypeError(f"Type AST non géré : {type(node)!r}")
