from __future__ import annotations

import json

import typer

from .kernel.ast import Program, to_dict, to_sexpr
from .kernel.compiler import parse_nl_to_program
from .kernel.macros import macros

app = typer.Typer(help="Compilation langage naturel → DSL avec macros.")


@app.command("parse")
def parse_command(
    text: str = typer.Argument(..., help="Texte en langage naturel à compiler."),
    expand: bool = typer.Option(False, "--expand", help="Expanse les macros après parsing."),
    fmt: str = typer.Option("sexpr", "--fmt", help="sexpr | json"),
) -> None:
    """Parse du NL, compile vers forme canonique, parse formel via Lark, expanse les macros."""
    canonical, program, intents = parse_nl_to_program(text)
    final = Program(macros.expand(program.body)) if expand else program

    typer.echo("=== Intentions reconnues ===")
    for idx, intent in enumerate(intents, start=1):
        typer.echo(json.dumps(
            {"index": idx, "action": intent.action, "slots": intent.slots,
             "confidence": intent.confidence, "source": intent.source_text},
            ensure_ascii=False,
        ))

    typer.echo("\n=== Forme canonique ===")
    typer.echo(canonical)

    typer.echo("\n=== AST DSL ===")
    if fmt == "json":
        typer.echo(json.dumps(to_dict(final), ensure_ascii=False, indent=2))
    else:
        typer.echo(to_sexpr(final))


@app.command("demo")
def demo_command() -> None:
    """Démonstration complète : intentions, canonique, AST, expansion."""
    text = "Clique sur Spotify, ouvre Spotify, va sur Spotify, puis clique sur play"
    canonical, program, intents = parse_nl_to_program(text)
    expanded = Program(macros.expand(program.body))

    typer.echo("=== Entrée ===")
    typer.echo(text)

    typer.echo("\n=== Intentions ===")
    for intent in intents:
        typer.echo(json.dumps(
            {"action": intent.action, "slots": intent.slots, "confidence": intent.confidence},
            ensure_ascii=False,
        ))

    typer.echo("\n=== Canonique ===")
    typer.echo(canonical)

    typer.echo("\n=== AST canonique ===")
    typer.echo(to_sexpr(program))

    typer.echo("\n=== AST expansé ===")
    typer.echo(to_sexpr(expanded))


@app.command("patterns")
def patterns_command() -> None:
    """Liste les patterns NL → canonique supportés."""
    typer.echo(json.dumps({
        "examples": [
            {"nl": "clique sur Spotify",  "canonical": 'click_on("Spotify")'},
            {"nl": "ouvre Spotify",       "canonical": 'click_on("Spotify")'},
            {"nl": "va sur Spotify",      "canonical": 'click_on("Spotify")'},
            {"nl": "appuie sur enter",    "canonical": 'press_key("enter")'},
            {"nl": "écris bonjour",       "canonical": 'type_text("bonjour")'},
        ]
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
