"""Handler for --show-config command."""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from ..config import Config

console = Console()


def show_config():
    """Show current configuration."""
    try:
        config = Config()

        # Get orchestrator config
        orch_config = config.get_orchestrator_config()
        defaults = config.get_defaults()
        nodes = config.get_nodes()

        # Build display content
        content_parts = []

        if orch_config:
            content_parts.append("[bold cyan]Orchestrator Settings:[/bold cyan]")
            for key, value in orch_config.items():
                content_parts.append(f"  {key}: {value}")
            content_parts.append("")

        if defaults:
            content_parts.append("[bold cyan]Default Agent Settings:[/bold cyan]")
            for key, value in defaults.items():
                content_parts.append(f"  {key}: {value}")
            content_parts.append("")

        if nodes:
            content_parts.append(f"[bold cyan]Configured Agents:[/bold cyan] {len(nodes)}")
            for node in nodes:
                if node.get("type") == "agent":
                    name = node.get("name", "Unknown")
                    content_parts.append(f"  • {name}")

        content = "\n".join(content_parts) if content_parts else "[yellow]No configuration found.[/yellow]"

        # Show config file path
        config_path = config.config_path
        console.print(Panel.fit(
            content,
            title=f"Configuration ({config_path})"
        ))

        # Optionally show raw YAML
        if config_path.exists():
            try:
                yaml_content = config_path.read_text(encoding="utf-8")
                console.print("\n[bold]Raw YAML:[/bold]")
                syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True)
                console.print(syntax)
            except Exception as e:
                console.print(f"[yellow]Could not display raw YAML: {e}[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error showing config: {e}[/red]")

