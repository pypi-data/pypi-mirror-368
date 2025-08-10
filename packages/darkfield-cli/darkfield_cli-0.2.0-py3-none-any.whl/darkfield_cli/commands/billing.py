"""
Billing and payment commands for darkfield CLI
"""

import click
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.progress import track
import keyring

console = Console()

@click.group()
def billing():
    """Manage billing and payments"""
    pass

@billing.command()
def add_payment_method():
    """Add a payment method to your account"""
    from ..api_client import DarkfieldClient
    
    client = DarkfieldClient()
    
    console.print("\n[cyan]Setting up payment method...[/cyan]")
    
    try:
        # Create Stripe checkout session
        response = client.post("/api/v1/billing/create-checkout-session", json={
            "mode": "setup",
            "success_url": "https://darkfield.ai/cli/payment-success",
            "cancel_url": "https://darkfield.ai/cli/payment-cancelled"
        })
        
        checkout_url = response["url"]
        
        console.print(f"\n[yellow]Please complete payment setup at:[/yellow]")
        console.print(f"{checkout_url}\n")
        
        if click.confirm("Open in browser?", default=True):
            import webbrowser
            webbrowser.open(checkout_url)
        
        # Wait for completion
        console.print("\n[dim]Waiting for payment method setup...[/dim]")
        console.print("[dim]Press Ctrl+C to cancel[/dim]")
        
        # Poll for completion
        import time
        start_time = time.time()
        while time.time() - start_time < 300:  # 5 minute timeout
            time.sleep(3)
            
            status = client.get("/api/v1/billing/payment-methods")
            if status["payment_methods"]:
                console.print("\n[green]✓[/green] Payment method added successfully!")
                console.print(f"Card: {status['payment_methods'][0]['card']['brand']} ending in {status['payment_methods'][0]['card']['last4']}")
                return
        
        console.print("\n[yellow]Setup timed out. Please check your account online.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error setting up payment: {e}[/red]")

@billing.command()
@click.option('--month', default='current', help='Month to show (YYYY-MM or "current")')
@click.option('--detailed', is_flag=True, help='Show detailed breakdown')
@click.option('--export', type=click.Path(), help='Export to CSV file')
def usage(month, detailed, export):
    """Show usage and costs for the specified month"""
    from ..api_client import DarkfieldClient
    
    client = DarkfieldClient()
    
    # Parse month
    if month == 'current':
        target_date = datetime.now()
    else:
        try:
            target_date = datetime.strptime(month, '%Y-%m')
        except ValueError:
            console.print("[red]Invalid month format. Use YYYY-MM or 'current'[/red]")
            return
    
    console.print(f"\n[cyan]Fetching usage for {target_date.strftime('%B %Y')}...[/cyan]")
    
    try:
        usage_data = client.get(f"/billing/usage", params={
            "year": target_date.year,
            "month": target_date.month,
            "detailed": detailed
        })
        
        # Summary table
        table = Table(title=f"Usage Summary - {target_date.strftime('%B %Y')}", show_header=True)
        table.add_column("Service", style="cyan")
        table.add_column("Usage", justify="right")
        table.add_column("Unit Cost", justify="right", style="dim")
        table.add_column("Total Cost", justify="right", style="green")
        
        services = [
            ("Vector Extraction", usage_data["vector_extraction"]["count"], 
             "traits", "$0.50/1k", usage_data["vector_extraction"]["cost"]),
            ("Data Analysis", usage_data["data_analysis"]["gb"], 
             "GB", "$2.00/GB", usage_data["data_analysis"]["cost"]),
            ("Model Monitoring", usage_data["model_monitoring"]["hours"], 
             "hours", "$0.10/hr", usage_data["model_monitoring"]["cost"]),
            ("API Requests", usage_data["api_requests"]["count"], 
             "requests", "$0.25/1k", usage_data["api_requests"]["cost"])
        ]
        
        for service, amount, unit, unit_cost, cost in services:
            if isinstance(amount, float):
                amount_str = f"{amount:,.2f} {unit}"
            else:
                amount_str = f"{amount:,} {unit}"
            table.add_row(service, amount_str, unit_cost, f"${cost:.2f}")
        
        console.print(table)
        console.print(f"\n[bold]Total Cost: ${usage_data['total_cost']:.2f}[/bold]")
        
        # Detailed breakdown if requested
        if detailed and usage_data.get("daily_breakdown"):
            detail_table = Table(title="Daily Breakdown", show_header=True)
            detail_table.add_column("Date", style="cyan")
            detail_table.add_column("Vectors", justify="right")
            detail_table.add_column("Data (GB)", justify="right")
            detail_table.add_column("Monitoring", justify="right")
            detail_table.add_column("API Calls", justify="right")
            detail_table.add_column("Cost", justify="right", style="green")
            
            for day in usage_data["daily_breakdown"]:
                detail_table.add_row(
                    day["date"],
                    f"{day['vectors']:,}",
                    f"{day['data_gb']:.1f}",
                    f"{day['monitoring_hours']:.1f}h",
                    f"{day['api_calls']:,}",
                    f"${day['cost']:.2f}"
                )
            
            console.print("\n")
            console.print(detail_table)
        
        # Export if requested
        if export:
            import csv
            with open(export, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Service", "Usage", "Unit", "Unit Cost", "Total Cost"])
                for service, amount, unit, unit_cost, cost in services:
                    writer.writerow([service, amount, unit, unit_cost, f"${cost:.2f}"])
                writer.writerow([])
                writer.writerow(["Total", "", "", "", f"${usage_data['total_cost']:.2f}"])
            
            console.print(f"\n[green]✓[/green] Usage data exported to {export}")
        
    except Exception as e:
        console.print(f"[red]Error fetching usage: {e}[/red]")

@billing.command()
@click.option('--limit', default=10, help='Number of invoices to show')
def invoices(limit):
    """List recent invoices"""
    from ..api_client import DarkfieldClient
    
    client = DarkfieldClient()
    
    try:
        invoices_data = client.get("/api/v1/billing/invoices", params={"limit": limit})
        
        if not invoices_data["invoices"]:
            console.print("[yellow]No invoices found[/yellow]")
            return
        
        table = Table(title="Recent Invoices", show_header=True)
        table.add_column("Invoice #", style="cyan")
        table.add_column("Date", style="dim")
        table.add_column("Amount", justify="right", style="green")
        table.add_column("Status")
        table.add_column("Download")
        
        for invoice in invoices_data["invoices"]:
            status_color = "green" if invoice["status"] == "paid" else "yellow"
            status = f"[{status_color}]{invoice['status'].upper()}[/{status_color}]"
            
            table.add_row(
                invoice["number"],
                invoice["date"],
                f"${invoice['amount']:.2f}",
                status,
                f"[link]{invoice['pdf_url']}[/link]"
            )
        
        console.print(table)
        console.print("\n[dim]Click on download links to get PDF invoices[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error fetching invoices: {e}[/red]")

@billing.command()
def upgrade():
    """Upgrade to a higher tier"""
    from ..api_client import DarkfieldClient
    
    client = DarkfieldClient()
    
    # Show pricing tiers
    console.print("\n[cyan]darkfield Pricing Tiers[/cyan]\n")
    
    tiers = [
        ("Free", "Try darkfield with limited usage", [
            "10 requests/minute",
            "1,000 requests/day",
            "1 GB data analysis/month",
            "10,000 vector extractions/month"
        ], "$0/month"),
        ("Pay-as-you-go", "Scale with your needs", [
            "100 requests/minute",
            "100,000 requests/day",
            "1,000 GB data analysis/month",
            "1,000,000 vector extractions/month",
            "Usage-based pricing"
        ], "From $0/month"),
        ("Enterprise", "Unlimited scale with SLA", [
            "1,000+ requests/minute",
            "Unlimited requests/day",
            "100,000+ GB data analysis/month",
            "100,000,000+ vector extractions/month",
            "Priority support",
            "Custom integrations",
            "99.9% uptime SLA"
        ], "Custom pricing")
    ]
    
    for i, (name, desc, features, price) in enumerate(tiers):
        console.print(f"[bold]{i+1}. {name}[/bold] - {desc}")
        for feature in features:
            console.print(f"   • {feature}")
        console.print(f"   [green]{price}[/green]\n")
    
    # Get current tier
    try:
        current = client.get("/api/v1/auth/verify")
        console.print(f"[dim]Current tier: {current['tier'].upper()}[/dim]\n")
        
        if current['tier'] == 'enterprise':
            console.print("[yellow]You're already on the Enterprise tier![/yellow]")
            return
        
        choice = click.prompt("Select tier to upgrade to", type=int)
        
        if choice == 1 and current['tier'] != 'free':
            console.print("[yellow]Cannot downgrade to free tier[/yellow]")
            return
        elif choice == 2:
            # Upgrade to pay-as-you-go
            response = client.post("/api/v1/billing/upgrade", json={"tier": "pay_as_you_go"})
            if response.get("checkout_url"):
                console.print("\n[yellow]Complete upgrade at:[/yellow]")
                console.print(response["checkout_url"])
                if click.confirm("\nOpen in browser?", default=True):
                    import webbrowser
                    webbrowser.open(response["checkout_url"])
            else:
                console.print("[green]✓[/green] Successfully upgraded to Pay-as-you-go!")
        elif choice == 3:
            # Enterprise - contact sales
            console.print("\n[cyan]Enterprise tier requires a custom agreement.[/cyan]")
            console.print("Please contact: [bold]sales@darkfield.ai[/bold]")
            console.print("Or visit: [link]https://darkfield.ai/enterprise[/link]")
        
    except Exception as e:
        console.print(f"[red]Error during upgrade: {e}[/red]")

@billing.command()
@click.option('--amount', type=float, required=True, help='Budget amount in USD')
@click.option('--action', type=click.Choice(['alert', 'stop']), default='alert', 
              help='Action when budget is exceeded')
def set_budget(amount, action):
    """Set a monthly spending budget"""
    from ..api_client import DarkfieldClient
    
    client = DarkfieldClient()
    
    try:
        response = client.post("/api/v1/billing/budget", json={
            "amount": amount,
            "action": action,
            "currency": "USD"
        })
        
        console.print(f"[green]✓[/green] Budget set to ${amount:.2f}/month")
        console.print(f"Action on exceed: {action}")
        
        if action == 'alert':
            console.print("[dim]You'll receive email alerts at 80% and 100% of budget[/dim]")
        else:
            console.print("[yellow]Warning: API access will be suspended when budget is exceeded[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error setting budget: {e}[/red]")