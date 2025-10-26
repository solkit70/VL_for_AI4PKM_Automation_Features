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
        self.vault_path = vault_path or Path.cwd()
        self.orchestrator = None

    def run_daemon(self, max_concurrent: int = 3):
        """
        Run orchestrator in daemon mode.

        Args:
            max_concurrent: Maximum concurrent executions
        """
        self.console.print(Panel.fit(
            "[bold cyan]AI4PKM Orchestrator[/bold cyan]\n"
            f"Vault: {self.vault_path}\n"
            f"Max concurrent: {max_concurrent}",
            title="Starting"
        ))

        # Create orchestrator
        agents_dir = self.vault_path / "_Settings_" / "Agents"
        self.orchestrator = Orchestrator(
            vault_path=self.vault_path,
            agents_dir=agents_dir,
            max_concurrent=max_concurrent
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
        agents_dir = self.vault_path / "_Settings_" / "Agents"
        orch = Orchestrator(
            vault_path=self.vault_path,
            agents_dir=agents_dir,
            max_concurrent=1  # Don't actually start
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
def daemon(max_concurrent):
    """Run orchestrator in daemon mode (monitors files and triggers agents)."""
    cli = OrchestratorCLI()
    cli.run_daemon(max_concurrent=max_concurrent)


@orchestrator_cli.command()
def status():
    """Show orchestrator status and loaded agents."""
    cli = OrchestratorCLI()
    cli.show_status()


if __name__ == '__main__':
    orchestrator_cli()
