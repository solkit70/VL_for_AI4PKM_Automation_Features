"""Orchestrator daemon and status functions."""

import sys
import signal
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from ..orchestrator.core import Orchestrator


def run_orchestrator_daemon(vault_path: Path = None, debug: bool = False):
    """
    Run orchestrator in daemon mode.

    Args:
        vault_path: Path to vault root (defaults to CWD)
        debug: Enable debug logging to console
    """
    from ..config import Config
    
    config = Config()
    console = Console()
    
    # Use CWD as vault (requires config file in CWD)
    vault_path = vault_path or Path.cwd()
    max_concurrent = config.get_orchestrator_max_concurrent()

    debug_mode = "[yellow](DEBUG)[/yellow]" if debug else ""
    console.print(Panel.fit(
        f"[bold cyan]AI4PKM Orchestrator[/bold cyan] {debug_mode}\n"
        f"Vault: {vault_path}\n"
        f"Max concurrent: {max_concurrent}",
        title="Starting"
    ))

    # Create orchestrator (it will load paths from config)
    orchestrator = Orchestrator(
        vault_path=vault_path,
        max_concurrent=max_concurrent,
        config=config,
        debug=debug
    )

    # Setup signal handlers
    def signal_handler(sig, frame):
        console.print("\n[yellow]Received interrupt signal, shutting down...[/yellow]")
        if orchestrator:
            orchestrator.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Show loaded agents
    status = orchestrator.get_status()
    console.print(f"\n[green]✓[/green] Loaded {status['agents_loaded']} agent(s):")
    for agent_info in status['agent_list']:
        console.print(
            f"  • [{agent_info['abbreviation']}] {agent_info['name']} "
            f"({agent_info['category']})"
        )

    # Start orchestrator
    console.print("\n[cyan]Starting orchestrator...[/cyan]")
    orchestrator.run_forever()


def show_orchestrator_status(vault_path: Path = None):
    """
    Show orchestrator status and loaded agents.

    Args:
        vault_path: Path to vault root (defaults to CWD)
    """
    from ..config import Config
    
    config = Config()
    console = Console()
    
    # Use CWD as vault (requires config file in CWD)
    vault_path = vault_path or Path.cwd()

    # Create orchestrator just to load agents (don't start)
    orch = Orchestrator(
        vault_path=vault_path,
        config=config
    )

    status = orch.get_status()

    console.print(Panel.fit(
        f"[bold]Vault:[/bold] {status['vault_path']}\n"
        f"[bold]Agents loaded:[/bold] {status['agents_loaded']}\n"
        f"[bold]Max concurrent:[/bold] {status['max_concurrent']}",
        title="Orchestrator Status"
    ))

    if status['agent_list']:
        console.print("\n[bold]Available Agents:[/bold]")
        for agent_info in status['agent_list']:
            console.print(
                f"  • [{agent_info['abbreviation']}] {agent_info['name']}\n"
                f"    Category: {agent_info['category']}"
            )

