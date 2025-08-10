"""
Persona management commands for darkfield CLI

Usage examples:
  darkfield persona create --file persona.yaml
  darkfield persona create --inline 'name=helpful-honest; model=llama-3; traits=helpfulness:0.7,honesty:0.5,harmlessness:0.6'
  darkfield persona list
  darkfield persona show helpful-honest
  darkfield persona use helpful-honest
  darkfield persona compose-vector --persona helpful-honest --model llama-3 --output vector.json
"""
from __future__ import annotations

import json
import click
from rich.console import Console
from rich.table import Table
from pathlib import Path

from ..api_client import DarkfieldClient
from ..utils.persona_manager import (
    list_personas,
    load_persona,
    save_persona_from_file,
    save_persona_inline,
    delete_persona,
    set_active_persona,
    get_active_persona,
    compose_persona_vector,
)

console = Console()


@click.group()
def persona():
    """Manage personas (profiles composed from trait vectors)"""
    pass


@persona.command()
@click.option('--file', 'file_path', type=click.Path(exists=True), help='YAML/JSON persona file')
@click.option('--inline', 'inline_spec', type=str, help='Inline spec: name=..., model=..., traits=a:0.5,b:0.3')
@click.option('--name', type=str, help='Override persona name when using --inline')
def create(file_path: str | None, inline_spec: str | None, name: str | None):
    """Create a persona in the local registry"""
    if not file_path and not inline_spec:
        console.print("[red]Provide either --file or --inline[/red]")
        raise click.Abort()
    if file_path:
        persona_name = save_persona_from_file(file_path)
    else:
        persona_name = save_persona_inline(inline_spec or "", name=name)
    console.print(f"[green]✓[/green] Persona created: [bold]{persona_name}[/bold]")


@persona.command()
def list():  # noqa: A001 - click command name
    """List locally defined personas"""
    names = list_personas()
    if not names:
        console.print("[yellow]No personas defined. Use 'darkfield persona create'[/yellow]")
        return
    table = Table(title="Personas", show_header=True)
    table.add_column("Name", style="cyan")
    for n in names:
        table.add_row(n)
    console.print(table)


@persona.command()
@click.argument('name_or_path')
def show(name_or_path: str):
    """Show persona details"""
    data = load_persona(name_or_path)
    console.print_json(data=data)


@persona.command()
@click.argument('name')
def delete(name: str):
    """Delete persona from local registry"""
    ok = delete_persona(name)
    if ok:
        console.print(f"[green]✓[/green] Deleted persona: {name}")
    else:
        console.print(f"[yellow]No persona found: {name}")


@persona.command()
@click.argument('name')
def use(name: str):
    """Set active persona for subsequent commands"""
    # Validate exists
    _ = load_persona(name)
    set_active_persona(name)
    console.print(f"[green]✓[/green] Active persona set to [bold]{name}[/bold]")


@persona.command('compose-vector')
@click.option('--persona', 'persona_name', type=str, help='Persona name or file path')
@click.option('--model', type=str, help='Override model for composition')
@click.option('--output', type=click.Path(), help='Write composite vector JSON')
@click.option('--json', 'as_json', is_flag=True, help='Print JSON to stdout')
def compose_vector(persona_name: str | None, model: str | None, output: str | None, as_json: bool):
    """Compose and optionally persist a persona vector from trait weights"""
    if not persona_name:
        persona_name = get_active_persona()
    if not persona_name:
        console.print("[red]No persona specified and no active persona set[/red]")
        raise click.Abort()

    data = load_persona(persona_name)
    comp = compose_persona_vector(data, client=DarkfieldClient(), model=model)

    payload = {
        "name": comp.name,
        "model": comp.model,
        "vector": comp.vector,
        "norm": comp.norm,
        "dimension": comp.dimension,
        "recommended_layer": comp.recommended_layer,
        "recommended_coefficient": comp.recommended_coefficient,
    }

    if output:
        Path(output).write_text(json.dumps(payload, indent=2), encoding='utf-8')
        console.print(f"[green]✓[/green] Persona vector saved to {output}")
    if as_json or not output:
        click.echo(json.dumps(payload, indent=2))
