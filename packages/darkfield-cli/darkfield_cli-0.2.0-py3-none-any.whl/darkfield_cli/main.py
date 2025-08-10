#!/usr/bin/env python3
"""
darkfield CLI - ML Safety Platform Command Line Interface
"""

import click
import sys
from rich.console import Console
from rich.table import Table
from .commands import auth as auth_cmd, billing as billing_cmd, analyze as analyze_cmd, monitor as monitor_cmd, extract as extract_cmd, keys as keys_cmd
from .commands import persona as persona_cmd
from .commands import benchmarks as benchmarks_cmd
from .errors import handle_error, AuthenticationError
from .config import get_api_key

console = Console()

DARKFIELD_ASCII = """
[cyan]
    ██████╗  █████╗ ██████╗ ██╗  ██╗███████╗██╗███████╗██╗     ██████╗ 
    ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██╔════╝██║██╔════╝██║     ██╔══██╗
    ██║  ██║███████║██████╔╝█████╔╝ █████╗  ██║█████╗  ██║     ██║  ██║
    ██║  ██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝  ██║██╔══╝  ██║     ██║  ██║
    ██████╔╝██║  ██║██║  ██║██║  ██╗██║     ██║███████╗███████╗██████╔╝
    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝╚═════╝ 
[/cyan]
    [bold white]ML Safety Platform Command Line Interface[/bold white]
    [dim]Protecting AI from harmful personas • v0.2.0[/dim]
"""

@click.group()
@click.version_option(version="0.2.0", prog_name="darkfield")
@click.option('--debug', is_flag=True, help='Enable debug mode with verbose errors')
@click.pass_context
def cli(ctx, debug):
    """
    darkfield - ML Safety Platform CLI
    
    Analyze training data, monitor models, and extract persona vectors
    with usage-based billing through the command line.
    """
    # Show ASCII art on first run or when no command provided
    if ctx.invoked_subcommand is None or (len(sys.argv) == 1):
        console.print(DARKFIELD_ASCII)
        console.print("")
        console.print("[dim]Quickstart:[/dim] https://github.com/darkfield-ai/cli/blob/main/docs/quickstart-5min.md")
        console.print("[dim]API Reference:[/dim] https://api.darkfield.ai/openapi.json\n")

# Register command groups
# Support both module-style and direct group exports
cli.add_command(getattr(auth_cmd, 'auth', auth_cmd))
cli.add_command(getattr(billing_cmd, 'billing', billing_cmd))
cli.add_command(getattr(analyze_cmd, 'analyze', analyze_cmd))
cli.add_command(getattr(monitor_cmd, 'monitor', monitor_cmd))
cli.add_command(getattr(extract_cmd, 'extract', extract_cmd))
cli.add_command(getattr(keys_cmd, 'keys', keys_cmd))
cli.add_command(getattr(persona_cmd, 'persona', persona_cmd))
cli.add_command(getattr(benchmarks_cmd, 'benchmarks', benchmarks_cmd))

@cli.command()
def status():
    """Show current authentication and usage status"""
    from .auth_utils import get_current_user
    from .api_client import DarkfieldClient
    
    # Show ASCII art for status command
    console.print(DARKFIELD_ASCII)
    console.print("")
    
    # Check for API key from environment first
    api_key = get_api_key()
    if api_key:
        console.print(f"[green]✓[/green] Authenticated via environment variable")
        console.print(f"API Key: {api_key[:10]}..." if len(api_key) > 10 else api_key)
        
        # Try to get user info from API
        try:
            client = DarkfieldClient()
            # Mock user info for now
            user = {
                'email': get_user_email() or 'via-api-key@darkfield.ai',
                'organization': 'API User',
                'tier': 'enterprise'
            }
        except:
            user = {
                'email': 'via-api-key@darkfield.ai',
                'organization': 'API User',
                'tier': 'enterprise'
            }
    else:
        user = get_current_user()
        if not user:
            console.print("[red]Not authenticated. Run 'darkfield auth login' to get started.[/red]")
            return
    
    # Show user info
    console.print(f"\n[green]✓[/green] Authenticated as: {user['email']}")
    console.print(f"Organization: {user.get('organization', 'Personal')}")
    console.print(f"API Tier: {user.get('tier', 'free').upper()}")
    
    # Get usage stats
    try:
        client = DarkfieldClient()
        usage = client.get_usage_summary()
        
        # Create usage table
        table = Table(title="\nCurrent Month Usage", show_header=True)
        table.add_column("Service", style="cyan")
        table.add_column("Usage", justify="right")
        table.add_column("Cost", justify="right", style="green")
        
        table.add_row("Vector Extraction", f"{usage['vectors']:,} traits", f"${usage['vectors_cost']:.2f}")
        table.add_row("Data Analysis", f"{usage['data_gb']:.1f} GB", f"${usage['data_cost']:.2f}")
        table.add_row("Model Monitoring", f"{usage['monitoring_hours']:.1f} hours", f"${usage['monitoring_cost']:.2f}")
        table.add_row("API Requests", f"{usage['api_calls']:,}", f"${usage['api_cost']:.2f}")
        
        console.print(table)
        console.print(f"\n[bold]Total: ${usage['total_cost']:.2f}[/bold]")
        
    except Exception as e:
        console.print(f"[yellow]Could not fetch usage data: {e}[/yellow]")

@cli.command()
@click.option('--json', is_flag=True, help='Output in JSON format')
def pricing(json):
    """Show current pricing information"""
    pricing_data = {
        "vector_extraction": {"per_1000_traits": 0.50},
        "data_analysis": {"per_gb": 2.00},
        "model_monitoring": {"per_hour": 0.10},
        "api_requests": {"per_1000": 0.25}
    }
    
    if json:
        import json as json_lib
        click.echo(json_lib.dumps(pricing_data, indent=2))
    else:
        table = Table(title="darkfield Pricing", show_header=True)
        table.add_column("Service", style="cyan")
        table.add_column("Unit", justify="center")
        table.add_column("Price", justify="right", style="green")
        
        table.add_row("Vector Extraction", "per 1,000 traits", "$0.50")
        table.add_row("Data Analysis", "per GB", "$2.00")
        table.add_row("Model Monitoring", "per hour", "$0.10")
        table.add_row("API Requests", "per 1,000", "$0.25")
        
        console.print(table)
        console.print("\n[dim]Volume discounts available for enterprise customers.[/dim]")
        console.print("[dim]Contact sales@darkfield.ai for custom pricing.[/dim]")

@cli.command()
def docs():
    """Open darkfield documentation in your browser"""
    import webbrowser
    console.print("Opening darkfield documentation...")
    webbrowser.open("https://darkfield.ai/docs")

if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)