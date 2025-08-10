"""
Authentication commands for darkfield CLI
"""

import click
import webbrowser
import time
import keyring
from urllib.parse import urlencode
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..config import DARKFIELD_API_URL, DARKFIELD_WEB_URL

console = Console()

@click.group()
def auth():
    """Manage authentication and API keys"""
    pass

@auth.command()
@click.option('--api-key', help='API key for authentication')
@click.option('--email', help='Email address for authentication')
def login(api_key, email):
    """Authenticate with darkfield"""
    # Quick hint for new users
    console.print("[dim]New user? Get a free trial key with: 'darkfield auth signup'[/dim]")
    # Fast path: if API key provided via flag, use it directly
    if api_key:
        console.print("\n[cyan]darkfield Authentication[/cyan]")
        console.print("\nAuthenticating with provided API key...")
        
        # If email not provided, prompt for it
        if not email:
            email = click.prompt("Enter your email", type=str)
        
        # Verify credentials with the API
        import requests
        
        try:
            verify_url = f"{DARKFIELD_API_URL}/api/v1/auth/verify"
            response = requests.get(
                verify_url,
                headers={"X-API-Key": api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Store credentials securely
                keyring.set_password("darkfield-cli", "api_key", api_key)
                keyring.set_password("darkfield-cli", "user_email", email)
                keyring.set_password("darkfield-cli", "user_id", data.get("user_id", ""))
                keyring.set_password("darkfield-cli", "auth_method", "api_key")
                
                console.print(f"\n[green]✓[/green] Successfully authenticated as {email}")
                console.print(f"[green]✓[/green] API tier: {data.get('tier', 'free').upper()}")
                return
            elif response.status_code == 401:
                console.print("\n[red]✗[/red] Invalid API key. Please check your credentials and try again.")
                return
            else:
                console.print(f"\n[red]✗[/red] Authentication failed: {response.status_code}")
                return
        except requests.exceptions.ConnectionError:
            console.print("\n[red]✗[/red] Could not connect to API")
            console.print("[yellow]Using mock mode for development[/yellow]")
            # Store credentials for mock mode
            keyring.set_password("darkfield-cli", "api_key", api_key)
            keyring.set_password("darkfield-cli", "user_email", email)
            keyring.set_password("darkfield-cli", "auth_method", "api_key")
            console.print(f"\n[green]✓[/green] Credentials saved for offline development")
            return
        except Exception as e:
            console.print(f"\n[red]✗[/red] Error during authentication: {e}")
            return
    
    # Original interactive flow
    console.print("\n[cyan]darkfield Authentication[/cyan]")
    console.print("\nTo use the darkfield CLI, you need to authenticate.")
    console.print("If you don't have an API key yet, run: [bold]darkfield auth signup[/bold]")
    console.print("\n[bold]Option 1: Login with email (session-based)[/bold]")
    console.print("\n[bold]Option 2: Use an API key[/bold]")
    console.print(f"Visit: [cyan]{DARKFIELD_WEB_URL}/auth[/cyan] to get an API key")
    
    # Ask which method
    use_session = click.confirm("Login with email (session-based)?", default=True)
    
    if use_session:
        # Session-based login
        email = click.prompt("Email address", type=str)
        
        # Login via API
        import requests
        console.print("\nLogging in...")
        
        try:
            login_url = f"{DARKFIELD_API_URL}/api/v1/auth/login"
            response = requests.post(
                login_url,
                json={"email": email},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Store session token and email
                keyring.set_password("darkfield-cli", "session_token", data["session_token"])
                keyring.set_password("darkfield-cli", "user_email", email)
                keyring.set_password("darkfield-cli", "user_id", data["user_id"])
                keyring.set_password("darkfield-cli", "auth_method", "session")
                
                console.print(f"\n[green]✓[/green] Successfully logged in as {email}")
                console.print(f"[green]✓[/green] Account tier: {data.get('tier', 'free').upper()}")
                console.print("\n[cyan]Get started with:[/cyan]")
                console.print("• [bold]darkfield analyze demo --trait helpful[/bold] - Run a demo")
                console.print("• [bold]darkfield auth status[/bold] - Check your session")
                console.print("• [bold]darkfield --help[/bold] - View all commands")
                
            elif response.status_code == 401:
                console.print("\n[red]✗[/red] Login failed. User not found.")
                console.print("Please register at: [cyan]{DARKFIELD_WEB_URL}/auth[/cyan]")
            else:
                console.print(f"\n[red]✗[/red] Login failed: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            console.print("\n[red]✗[/red] Could not connect to API")
        except Exception as e:
            console.print(f"\n[red]✗[/red] Error during login: {e}")
            
    else:
        # API key authentication
        console.print("\n[bold]Using API key authentication[/bold]")
        
        # Check if user wants to open browser
        if click.confirm(f"Open {DARKFIELD_WEB_URL}/auth in your browser?", default=True):
            webbrowser.open(f"{DARKFIELD_WEB_URL}/auth")
            console.print("\n[yellow]Please generate an API key and return here to continue.[/yellow]")
            click.pause()
        
        # Get API key from user
        api_key = click.prompt("API key", type=str, hide_input=True)
        
        # Validate the API key format
        if not api_key.startswith(("df_live_", "df_test_")):
            console.print("\n[red]✗[/red] Invalid API key format. API keys should start with 'df_live_' or 'df_test_'")
            return
        
        # Verify credentials with the API
        import requests
        
        console.print("\nVerifying API key...")
        
        try:
            verify_url = f"{DARKFIELD_API_URL}/api/v1/auth/verify"
            response = requests.get(
                verify_url,
                headers={"X-API-Key": api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Store credentials securely
                keyring.set_password("darkfield-cli", "api_key", api_key)
                keyring.set_password("darkfield-cli", "user_email", data.get("email", ""))
                keyring.set_password("darkfield-cli", "user_id", data.get("user_id", ""))
                keyring.set_password("darkfield-cli", "auth_method", "api_key")
                
                console.print(f"\n[green]✓[/green] Successfully authenticated")
                console.print(f"[green]✓[/green] API tier: {data.get('tier', 'free').upper()}")
                
                return
                
            elif response.status_code == 401:
                console.print("\n[red]✗[/red] Invalid API key. Please check your credentials and try again.")
                return
                
        except requests.exceptions.ConnectionError:
            console.print("\n[red]✗[/red] Could not connect to API")
        except Exception as e:
            console.print(f"\n[red]✗[/red] Error during authentication: {e}")

@auth.command()
def logout():
    """Log out from darkfield"""
    try:
        # Get current user for confirmation
        email = keyring.get_password("darkfield-cli", "user_email")
        auth_method = keyring.get_password("darkfield-cli", "auth_method") or "api_key"
        
        if email and click.confirm(f"Log out from {email}?"):
            # Logout based on auth method
            if auth_method == "session":
                session_token = keyring.get_password("darkfield-cli", "session_token")
                if session_token:
                    import requests
                    try:
                        response = requests.post(
                            f"{DARKFIELD_API_URL}/api/v1/auth/logout",
                            headers={"X-Session-Token": session_token}
                        )
                    except:
                        pass  # Best effort
            else:
                # API key logout (revoke if supported)
                api_key = keyring.get_password("darkfield-cli", "api_key")
                if api_key:
                    import requests
                    try:
                        requests.post(f"{DARKFIELD_API_URL}/auth/revoke", 
                                    headers={"X-API-Key": api_key})
                    except:
                        pass  # Best effort
            
            # Clear local credentials
            for key in ["api_key", "session_token", "user_email", "user_id", "auth_method"]:
                try:
                    keyring.delete_password("darkfield-cli", key)
                except:
                    pass
            
            console.print("[green]✓[/green] Successfully logged out")
        else:
            console.print("[yellow]Logout cancelled[/yellow]")
            
    except keyring.errors.PasswordDeleteError:
        console.print("[yellow]Not currently logged in[/yellow]")

@auth.command()
def status():
    """Show current authentication status"""
    try:
        email = keyring.get_password("darkfield-cli", "user_email")
        auth_method = keyring.get_password("darkfield-cli", "auth_method") or "api_key"
        
        if email:
            # Verify credentials are still valid
            import requests
            
            headers = {}
            if auth_method == "session":
                session_token = keyring.get_password("darkfield-cli", "session_token")
                headers = {"X-Session-Token": session_token}
            else:
                api_key = keyring.get_password("darkfield-cli", "api_key")
                headers = {"X-API-Key": api_key}
            
            response = requests.get(f"{DARKFIELD_API_URL}/api/v1/auth/verify",
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                console.print(f"[green]✓[/green] Authenticated as: {email}")
                console.print(f"Auth Method: {auth_method.replace('_', ' ').title()}")
                console.print(f"API Tier: {data.get('tier', 'free').upper()}")
                console.print(f"Organization: {data.get('organization', 'Personal')}")
                
                if auth_method == "api_key":
                    # Show API key preview (last 4 chars only for security)
                    api_key = keyring.get_password("darkfield-cli", "api_key")
                    key_preview = f"...{api_key[-4:]}"
                    console.print(f"API Key: {key_preview}")
            else:
                console.print("[red]✗[/red] Authentication is no longer valid")
                console.print("Please run: [bold]darkfield auth login[/bold]")
        else:
            console.print("[yellow]Not authenticated[/yellow]")
            console.print("Run: [bold]darkfield auth login[/bold]")
            
    except Exception as e:
        console.print(f"[red]Error checking auth status: {e}[/red]")

@auth.command()
@click.option('--email', prompt=True, help='Email address to register a trial account')
@click.option('--organization', default='', help='Organization (optional)')
def signup(email, organization):
    """Sign up for a trial API key (free tier)."""
    from ..api_client import DarkfieldClient
    import requests
    client = DarkfieldClient()
    try:
        resp = client.post("/api/v1/auth/register", json={
            "email": email,
            "organization": organization or None,
        })
        api_key = resp.get("api_key")
        if not api_key:
            console.print("[red]Registration failed: missing API key in response[/red]")
            return
        # Offer to save
        if click.confirm("Save API key to system keychain?", default=True):
            keyring.set_password("darkfield-cli", "api_key", api_key)
            keyring.set_password("darkfield-cli", "user_email", email)
            keyring.set_password("darkfield-cli", "auth_method", "api_key")
            console.print("[green]✓[/green] API key saved to keychain")
        console.print("\n[green]✓[/green] Trial API key issued (free tier with usage limits)")
        console.print("Use: export DARKFIELD_API_KEY=...  or run 'darkfield auth status'\n")
    except requests.HTTPError as e:
        console.print(f"[red]Signup failed: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error during signup: {e}[/red]")

@auth.command()
@click.option('--name', required=True, help='Name for this API key')
@click.option('--scopes', default='api:full', help='Comma-separated scopes')
def create_key(name, scopes):
    """Create a new API key for programmatic access"""
    # Get auth headers
    auth_method = keyring.get_password("darkfield-cli", "auth_method") or "api_key"
    headers = {}
    
    if auth_method == "session":
        session_token = keyring.get_password("darkfield-cli", "session_token")
        if not session_token:
            console.print("[red]Not authenticated. Please login first.[/red]")
            return
        headers = {"X-Session-Token": session_token}
    else:
        api_key = keyring.get_password("darkfield-cli", "api_key")
        if not api_key:
            console.print("[red]Not authenticated. Please login first.[/red]")
            return
        headers = {"X-API-Key": api_key}
    
    import requests
    
    console.print(f"Creating API key '{name}' with scopes: {scopes}")
    
    response = requests.post(f"{DARKFIELD_API_URL}/api-keys", 
                           headers=headers,
                           json={"name": name, "scopes": scopes.split(",")})
    
    if response.status_code in (200, 201):
        data = response.json()
        console.print(f"\n[green]✓[/green] API key created successfully")
        console.print(f"\n[yellow]Save this key securely - it won't be shown again:[/yellow]")
        console.print(f"\n[bold]{data.get('key', data.get('api_key'))}[/bold]\n")
        console.print(f"Key ID: {data.get('id', data.get('key_id'))}")
        console.print(f"Created: {data['created_at']}")
    else:
        console.print(f"[red]Failed to create API key: {response.json().get('error', 'Unknown error')}[/red]")

@auth.command()
def list_keys():
    """List all API keys for your account"""
    # Get auth headers
    auth_method = keyring.get_password("darkfield-cli", "auth_method") or "api_key"
    headers = {}
    
    if auth_method == "session":
        session_token = keyring.get_password("darkfield-cli", "session_token")
        if not session_token:
            console.print("[red]Not authenticated. Please login first.[/red]")
            return
        headers = {"X-Session-Token": session_token}
    else:
        api_key = keyring.get_password("darkfield-cli", "api_key")
        if not api_key:
            console.print("[red]Not authenticated. Please login first.[/red]")
            return
        headers = {"X-API-Key": api_key}
    
    import requests
    from rich.table import Table
    
    response = requests.get(f"{DARKFIELD_API_URL}/api-keys",
                          headers=headers)
    
    if response.status_code == 200:
        keys = response.json()["keys"]
        
        table = Table(title="API Keys", show_header=True)
        table.add_column("Name", style="cyan")
        table.add_column("Key Preview", style="dim")
        table.add_column("Created", style="dim")
        table.add_column("Last Used")
        
        for key in keys:
            last_used = key.get("last_used_at", "Never")
            if last_used != "Never":
                last_used = last_used[:10]  # Just date
            created = key["created_at"][:10]  # Just date
            table.add_row(key["name"], key.get("prefix", "..."), created, last_used)
        
        console.print(table)
    else:
        console.print(f"[red]Failed to list keys: {response.json().get('error', 'Unknown error')}[/red]")

@auth.command()
def sessions():
    """List active sessions for your account"""
    # Get auth headers
    auth_method = keyring.get_password("darkfield-cli", "auth_method") or "api_key"
    headers = {}
    
    if auth_method == "session":
        session_token = keyring.get_password("darkfield-cli", "session_token")
        if not session_token:
            console.print("[red]Not authenticated. Please login first.[/red]")
            return
        headers = {"X-Session-Token": session_token}
    else:
        api_key = keyring.get_password("darkfield-cli", "api_key")
        if not api_key:
            console.print("[red]Not authenticated. Please login first.[/red]")
            return
        headers = {"X-API-Key": api_key}
    
    import requests
    from rich.table import Table
    
    response = requests.get(f"{DARKFIELD_API_URL}/api/v1/sessions",
                          headers=headers)
    
    if response.status_code == 200:
        sessions = response.json()["sessions"]
        
        table = Table(title="Active Sessions", show_header=True)
        table.add_column("IP Address", style="cyan")
        table.add_column("User Agent", style="dim", width=40)
        table.add_column("Last Activity")
        table.add_column("Created")
        
        for session in sessions:
            user_agent = session.get("user_agent", "Unknown")[:40]
            if len(session.get("user_agent", "")) > 40:
                user_agent += "..."
            last_activity = session["last_activity"][:19]  # Remove microseconds
            created = session["created_at"][:19]
            table.add_row(
                session.get("ip_address", "Unknown"),
                user_agent,
                last_activity,
                created
            )
        
        console.print(table)
        console.print(f"\nTotal active sessions: {len(sessions)}")
    else:
        console.print(f"[red]Failed to list sessions: {response.json().get('error', 'Unknown error')}[/red]")