"""Webhook filter validation and help command."""

import typer
from rich.table import Table
from rich.panel import Panel

from gira.utils.console import console
from gira.utils.project import ensure_gira_project
from gira.utils.webhook_filters import WebhookFilterManager


def filter_help():
    """Show help for webhook filter expressions.
    
    Displays supported fields, operators, and example filter expressions
    for webhook event filtering.
    """
    ensure_gira_project()
    
    console.print("[bold cyan]Webhook Filter Help[/bold cyan]\n")
    
    # Show supported fields
    console.print("[bold]Supported Fields:[/bold]")
    fields_table = Table(show_header=True, header_style="bold magenta")
    fields_table.add_column("Field", style="cyan", width=15)
    fields_table.add_column("Description")
    
    supported_fields = WebhookFilterManager.get_supported_fields()
    for field, description in supported_fields.items():
        fields_table.add_row(field, description)
    
    console.print(fields_table)
    
    # Show operators
    console.print("\n[bold]Operators:[/bold]")
    operators_table = Table(show_header=True, header_style="bold magenta")
    operators_table.add_column("Operator", style="cyan", width=10)
    operators_table.add_column("Description")
    operators_table.add_column("Example")
    
    operators_table.add_row(":", "Equals", "priority:high")
    operators_table.add_row("!=", "Not equals", "status!=done")
    operators_table.add_row("~", "Contains", "labels~security")
    operators_table.add_row("AND", "Logical AND", "type:bug AND priority:high")
    operators_table.add_row("OR", "Logical OR", "type:bug OR priority:high")
    
    console.print(operators_table)
    
    # Show examples
    console.print("\n[bold]Example Filter Expressions:[/bold]")
    examples = WebhookFilterManager.get_filter_examples()
    
    for i, example in enumerate(examples, 1):
        panel_content = f"[cyan]{example['expression']}[/cyan]\n\n{example['description']}"
        panel = Panel(panel_content, title=f"Example {i}", expand=False)
        console.print(panel)
        if i < len(examples):
            console.print()
    
    console.print("\n[dim]Use these expressions with:[/dim]")
    console.print("  gira webhook add <name> <url> --filter \"<expression>\"")
    console.print("  gira webhook filter validate \"<expression>\"")


def validate(
    expression: str = typer.Argument(..., help="Filter expression to validate")
):
    """Validate a webhook filter expression.
    
    Checks if the filter expression is syntactically correct and provides
    feedback on any issues.
    
    Examples:
        gira webhook filter validate "priority:high"
        gira webhook filter validate "type:bug OR priority:high"
        gira webhook filter validate "invalid:syntax"
    """
    ensure_gira_project()
    
    console.print(f"[cyan]Validating filter expression:[/cyan] {expression}")
    
    is_valid, error_message = WebhookFilterManager.validate_filter_expression(expression)
    
    if is_valid:
        console.print("[green]✓[/green] Filter expression is valid")
        
        # Show what the filter would match
        console.print("\n[dim]This filter will match events where:[/dim]")
        
        # Parse and explain the filter
        from gira.utils.webhook_filters import WebhookFilter
        webhook_filter = WebhookFilter(expression)
        
        if webhook_filter.parsed_conditions:
            for i, condition_group in enumerate(webhook_filter.parsed_conditions):
                if i > 0:
                    console.print("  [dim]OR[/dim]")
                
                conditions = condition_group["conditions"]
                for j, condition in enumerate(conditions):
                    if j > 0:
                        console.print("  [dim]AND[/dim]")
                    
                    field = condition["field"]
                    value = condition["value"]
                    condition_type = condition["type"]
                    
                    if condition_type == "equals":
                        console.print(f"  • {field} equals '{value}'")
                    elif condition_type == "not_equals":
                        console.print(f"  • {field} does not equal '{value}'")
                    elif condition_type == "contains":
                        console.print(f"  • {field} contains '{value}'")
        else:
            console.print("  [yellow]Empty filter - matches all events[/yellow]")
    
    else:
        console.print(f"[red]✗[/red] Filter expression is invalid")
        console.print(f"[red]Error:[/red] {error_message}")
        
        console.print("\n[dim]Get help with filter syntax:[/dim]")
        console.print("  gira webhook filter help")
        
        raise typer.Exit(1)