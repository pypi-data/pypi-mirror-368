"""
API Key management commands for darkfield CLI
"""

import click
from rich.console import Console
from rich.table import Table
from datetime import datetime
import keyring

console = Console()

@click.group()
def keys():
    """Manage API keys"""
    pass

@keys.command()
def list_models():
    """List available models from the server (fallback to common set)"""
    from ..api_client import DarkfieldClient
    client = DarkfieldClient()
    try:
        data = client.get("/api/v1/models/registry")
        models = []
        if isinstance(data, list):
            for m in data:
                name = m.get("name") or m
                if name:
                    models.append(name)
        elif isinstance(data, dict) and "models" in data:
            models = [m.get("name", m) for m in data["models"]]
        if not models:
            raise ValueError("no-models")
        console.print("[bold]Available models:[/bold]")
        for m in models:
            console.print(f" - {m}")
    except Exception as e:
        console.print(f"[yellow]Could not fetch models: {e}. Showing defaults.[/yellow]")
        defaults = ["gpt2", "gpt2-medium", "gpt2-large", "llama-3", "mistral-7b"]
        for m in defaults:
            console.print(f" - {m}")

@keys.command()
@click.option('--name', required=True, help='Name for the API key')
@click.option('--tier', type=click.Choice(['free', 'pay_as_you_go', 'enterprise']), help='Tier for the key')
@click.option('--expires-in-days', type=int, help='Days until expiration (1-365)')
def create(name, tier, expires_in_days):
    """Create a new API key"""
    from ..api_client import DarkfieldClient
    
    client = DarkfieldClient()
    
    console.print(f"\n[cyan]Creating API key '{name}'...[/cyan]")
    
    try:
        # Create API key
        params = {"name": name}
        if tier:
            params["tier"] = tier
        if expires_in_days:
            params["expires_in_days"] = expires_in_days
            
        response = client.post("/api/v1/api-keys", json=params)
        
        api_key = response["api_key"]
        key_id = response["key_id"]
        
        console.print("\n[green]✓[/green] API key created successfully!")
        console.print("\n[bold red]IMPORTANT: This key will only be shown once![/bold red]")
        console.print(f"\nAPI Key: [bold yellow]{api_key}[/bold yellow]")
        console.print(f"Key ID: {key_id}")
        console.print(f"Name: {name}")
        console.print(f"Tier: {response['tier']}")
        console.print(f"Rate Limit: {response['rate_limit']} requests/minute")
        
        if response.get('expires_at'):
            console.print(f"Expires: {response['expires_at']}")
        
        # Offer to save to keychain
        if click.confirm("\nSave API key to system keychain?", default=True):
            keyring.set_password("darkfield-cli", f"api-key-{key_id}", api_key)
            console.print("[green]✓[/green] API key saved to keychain")
        
        # Show usage example
        console.print("\n[cyan]Usage example:[/cyan]")
        console.print(f"export DARKFIELD_API_KEY={api_key}")
        console.print("darkfield analyze --data ./data.jsonl")
        
    except Exception as e:
        console.print(f"[red]Error creating API key: {e}[/red]")

@keys.command()
@click.option('--show-inactive', is_flag=True, help='Include revoked keys')
def list(show_inactive):
    """List your API keys"""
    from ..api_client import DarkfieldClient
    
    client = DarkfieldClient()
    
    try:
        params = {"include_inactive": show_inactive} if show_inactive else {}
        keys_data = client.get("/api/v1/api-keys", params=params)
        
        if not keys_data:
            console.print("[yellow]No API keys found[/yellow]")
            return
        
        table = Table(title="Your API Keys", show_header=True)
        table.add_column("Name", style="cyan")
        table.add_column("Key Preview", style="dim")
        table.add_column("Tier")
        table.add_column("Status")
        table.add_column("Created", style="dim")
        table.add_column("Last Used", style="dim")
        
        for key in keys_data:
            status = "[green]Active[/green]" if key["is_active"] else "[red]Revoked[/red]"
            
            created_date = datetime.fromisoformat(key["created_at"].replace('Z', '+00:00'))
            created_str = created_date.strftime("%Y-%m-%d")
            
            last_used_str = "Never"
            if key.get("last_used_at"):
                last_used_date = datetime.fromisoformat(key["last_used_at"].replace('Z', '+00:00'))
                last_used_str = last_used_date.strftime("%Y-%m-%d %H:%M")
            
            table.add_row(
                key["name"],
                key["key_preview"],
                key["tier"],
                status,
                created_str,
                last_used_str
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing API keys: {e}[/red]")

@keys.command()
@click.argument('key_id')
def revoke(key_id):
    """Revoke an API key"""
    from ..api_client import DarkfieldClient
    
    if not click.confirm(f"Are you sure you want to revoke key {key_id}?"):
        return
    
    client = DarkfieldClient()
    
    try:
        client.delete(f"/api/v1/api-keys/{key_id}")
        console.print(f"[green]✓[/green] API key {key_id} revoked successfully")
        
        # Remove from keychain if stored
        try:
            keyring.delete_password("darkfield-cli", f"api-key-{key_id}")
            console.print("[dim]Removed from keychain[/dim]")
        except:
            pass
            
    except Exception as e:
        console.print(f"[red]Error revoking API key: {e}[/red]")

@keys.command()
@click.argument('key_id')
def usage(key_id):
    """Show usage statistics for an API key"""
    from ..api_client import DarkfieldClient
    
    client = DarkfieldClient()
    
    try:
        usage_data = client.get(f"/api/v1/api-keys/{key_id}/usage")
        
        console.print(f"\n[cyan]Usage for API Key: {usage_data['name']}[/cyan]")
        console.print(f"Tier: {usage_data['tier']}")
        console.print(f"Period: {usage_data['period']}")
        console.print(f"Rate Limit: {usage_data['rate_limit']} requests/minute\n")
        
        if not usage_data['usage']:
            console.print("[yellow]No usage recorded yet[/yellow]")
            return
        
        table = Table(title="Monthly Usage", show_header=True)
        table.add_column("Service", style="cyan")
        table.add_column("Used", justify="right")
        table.add_column("Limit", justify="right")
        table.add_column("Remaining", justify="right", style="green")
        table.add_column("Usage %", justify="right")
        
        for service, data in usage_data['usage'].items():
            limit_str = str(data['limit']) if data['limit'] else "Unlimited"
            remaining_str = str(data['remaining']) if isinstance(data['remaining'], (int, float)) else data['remaining']
            
            # Color code usage percentage
            usage_pct = data['percentage']
            if usage_pct >= 90:
                pct_style = "red"
            elif usage_pct >= 75:
                pct_style = "yellow"
            else:
                pct_style = "green"
            
            table.add_row(
                service,
                f"{data['used']:,.0f}",
                limit_str,
                remaining_str,
                f"[{pct_style}]{usage_pct:.1f}%[/{pct_style}]"
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error fetching usage: {e}[/red]")

@keys.command()
@click.argument('key_id')
def rotate(key_id):
    """Rotate an API key (revoke and create new)"""
    from ..api_client import DarkfieldClient
    
    if not click.confirm(f"Rotate key {key_id}? The old key will be revoked."):
        return
    
    client = DarkfieldClient()
    
    try:
        response = client.post(f"/api/v1/api-keys/{key_id}/rotate")
        
        console.print("[green]✓[/green] API key rotated successfully!")
        console.print(f"\nOld key {key_id} has been revoked")
        
        new_key = response["new_key"]
        console.print(f"\n[bold red]IMPORTANT: New key will only be shown once![/bold red]")
        console.print(f"\nNew API Key: [bold yellow]{new_key['api_key']}[/bold yellow]")
        console.print(f"New Key ID: {new_key['key_id']}")
        
        # Offer to save to keychain
        if click.confirm("\nSave new API key to system keychain?", default=True):
            # Remove old key
            try:
                keyring.delete_password("darkfield-cli", f"api-key-{key_id}")
            except:
                pass
                
            # Save new key
            keyring.set_password("darkfield-cli", f"api-key-{new_key['key_id']}", new_key['api_key'])
            console.print("[green]✓[/green] New API key saved to keychain")
        
    except Exception as e:
        console.print(f"[red]Error rotating API key: {e}[/red]")