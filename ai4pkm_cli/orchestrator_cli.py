"""CLI for orchestrator - separate from legacy KTM."""

import sys
import signal
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .orchestrator.core import Orchestrator


class OrchestratorCLI:
    """CLI wrapper for orchestrator."""

    def __init__(self, vault_path: Path = None):
        """Initialize orchestrator CLI."""
        self.console = Console()
        # Use CWD as vault (requires config file in CWD)
        self.vault_path = vault_path or Path.cwd()
        self.orchestrator = None

    def run_daemon(self, max_concurrent: int = None, debug: bool = False):
        """
        Run orchestrator in daemon mode.

        Args:
            max_concurrent: Maximum concurrent executions (defaults to config)
            debug: Enable debug logging to console
        """
        from .config import Config

        # Check for config file in CWD
        config_path = Path.cwd() / "ai4pkm_cli.json"
        if not config_path.exists():
            self.console.print(f"[red]✗ Error:[/red] ai4pkm_cli.json not found in current directory")
            self.console.print(f"[yellow]Current directory:[/yellow] {Path.cwd()}")
            self.console.print(f"\n[cyan]Must run from vault directory containing ai4pkm_cli.json[/cyan]")
            sys.exit(1)

        config = Config(config_file=str(config_path))

        # Use config value if not specified
        if max_concurrent is None:
            max_concurrent = config.get_orchestrator_max_concurrent()

        debug_mode = "[yellow](DEBUG)[/yellow]" if debug else ""
        self.console.print(Panel.fit(
            f"[bold cyan]AI4PKM Orchestrator[/bold cyan] {debug_mode}\n"
            f"Vault: {self.vault_path}\n"
            f"Max concurrent: {max_concurrent}",
            title="Starting"
        ))

        # Create orchestrator (it will load paths from config)
        self.orchestrator = Orchestrator(
            vault_path=self.vault_path,
            max_concurrent=max_concurrent,
            config=config,
            debug=debug
        )

        # Setup signal handlers
        def signal_handler(sig, frame):
            self.console.print("\n[yellow]Received interrupt signal, shutting down...[/yellow]")
            if self.orchestrator:
                self.orchestrator.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Show loaded agents
        status = self.orchestrator.get_status()
        self.console.print(f"\n[green]✓[/green] Loaded {status['agents_loaded']} agent(s):")
        for agent_info in status['agent_list']:
            self.console.print(
                f"  • [{agent_info['abbreviation']}] {agent_info['name']} "
                f"({agent_info['category']})"
            )

        # Start orchestrator
        self.console.print("\n[cyan]Starting orchestrator...[/cyan]")
        self.orchestrator.run_forever()

    def show_status(self):
        """Show orchestrator status."""
        from .config import Config

        # Check for config file in CWD
        config_path = Path.cwd() / "ai4pkm_cli.json"
        if not config_path.exists():
            self.console.print(f"[red]✗ Error:[/red] ai4pkm_cli.json not found in current directory")
            self.console.print(f"[yellow]Current directory:[/yellow] {Path.cwd()}")
            self.console.print(f"\n[cyan]Must run from vault directory containing ai4pkm_cli.json[/cyan]")
            sys.exit(1)

        config = Config(config_file=str(config_path))

        # Create orchestrator just to load agents (don't start)
        orch = Orchestrator(
            vault_path=self.vault_path,
            config=config
        )

        status = orch.get_status()

        self.console.print(Panel.fit(
            f"[bold]Vault:[/bold] {status['vault_path']}\n"
            f"[bold]Agents loaded:[/bold] {status['agents_loaded']}\n"
            f"[bold]Max concurrent:[/bold] {status['max_concurrent']}",
            title="Orchestrator Status"
        ))

        if status['agent_list']:
            self.console.print("\n[bold]Available Agents:[/bold]")
            for agent_info in status['agent_list']:
                self.console.print(
                    f"  • [{agent_info['abbreviation']}] {agent_info['name']}\n"
                    f"    Category: {agent_info['category']}"
                )


@click.group()
def orchestrator_cli():
    """Orchestrator commands (new multi-agent system)."""
    pass


@orchestrator_cli.command()
@click.option(
    '--max-concurrent',
    '-m',
    default=3,
    help='Maximum concurrent agent executions'
)
@click.option(
    '--debug',
    '-d',
    is_flag=True,
    help='Enable debug logging to console'
)
def daemon(max_concurrent, debug):
    """Run orchestrator in daemon mode (monitors files and triggers agents)."""
    cli = OrchestratorCLI()
    cli.run_daemon(max_concurrent=max_concurrent, debug=debug)


@orchestrator_cli.command()
def status():
    """Show orchestrator status and loaded agents."""
    cli = OrchestratorCLI()
    cli.show_status()


if __name__ == '__main__':
    orchestrator_cli()
