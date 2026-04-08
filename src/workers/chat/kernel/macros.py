from __future__ import annotations

from typing import Callable

from .ast import Assign, Call, Node, Program, Seq, String, Var

MacroExpander = Callable[[list[Node]], Node]


# ── Registre ─────────────────────────────────────────────────────────────────

class MacroRegistry:
    def __init__(self) -> None:
        self._macros: dict[str, MacroExpander] = {}

    def register(self, name: str, expander: MacroExpander) -> None:
        self._macros[name] = expander

    def has(self, name: str) -> bool:
        return name in self._macros

    def expand(self, node: Node) -> Node:
        if isinstance(node, Program):
            return Program(self.expand(node.body))
        if isinstance(node, Seq):
            return Seq([self.expand(step) for step in node.steps])
        if isinstance(node, Assign):
            return Assign(node.var, self.expand(node.value))
        if isinstance(node, Call):
            expanded_args = [self.expand(arg) for arg in node.args]
            if self.has(node.name):
                expanded = self._macros[node.name](expanded_args)
                return self.expand(expanded)
            return Call(node.name, expanded_args)
        return node


# ── Instance partagée ─────────────────────────────────────────────────────────

macros = MacroRegistry()


# ── Définitions de macros ─────────────────────────────────────────────────────

def _macro_click_on(args: list[Node]) -> Node:
    target = args[0]
    return Seq(steps=[
        Assign("box", Call("find", [target])),
        Call("move_to", [Call("center", [Var("box")])]),
        Call("click", [String("left")]),
    ])


def _macro_open_app(args: list[Node]) -> Node:
    target = args[0]
    return Seq(steps=[
        Call("press_key", [String("super")]),
        Call("type_text", [target]),
        Call("press_key", [String("enter")]),
    ])


macros.register("click_on", _macro_click_on)
macros.register("open_app", _macro_open_app)
