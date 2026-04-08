from __future__ import annotations

import json

from .ast import Program
from .grammar import canonical_parser
from .intent import Intent, parse_intent, split_commands


# ── Compilation intent → forme canonique ─────────────────────────────────────

def _escape(value: str) -> str:
    return json.dumps(value)


def compile_intent(intent: Intent) -> str:
    if intent.action == "click_on":
        return f'click_on({_escape(intent.slots["target"])})'
    if intent.action == "press_key":
        return f'press_key({_escape(intent.slots["key"])})'
    if intent.action == "type_text":
        return f'type_text({_escape(intent.slots["text"])})'
    raise ValueError(f"Action non supportée : {intent.action!r}")


def compile_text(text: str) -> tuple[str, list[Intent]]:
    """NL → forme canonique Lark + liste d'intentions."""
    intents: list[Intent] = []
    canonical_calls: list[str] = []
    for command in split_commands(text):
        intent = parse_intent(command)
        if intent is None:
            raise ValueError(f"Commande non reconnue : {command!r}")
        intents.append(intent)
        canonical_calls.append(compile_intent(intent))
    return "; ".join(canonical_calls), intents


# ── Pipeline complet ──────────────────────────────────────────────────────────

def parse_nl_to_program(text: str) -> tuple[str, Program, list[Intent]]:
    """NL → (forme canonique, Program AST, intentions)."""
    canonical, intents = compile_text(text)
    program = canonical_parser.parse(canonical)
    return canonical, program, intents
