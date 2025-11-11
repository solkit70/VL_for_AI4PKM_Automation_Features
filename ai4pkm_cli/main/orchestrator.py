"""Orchestrator daemon and status functions."""

import sys
import signal
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from ..orchestrator.core import Orchestrator
from ..logger import Logger

logger = Logger(console_output=True)


def run_orchestrator_daemon(vault_path: Path = None, debug: bool = False, working_dir: str = None):
    """
    Run orchestrator in daemon mode.

    Args:
        vault_path: Path to vault root (defaults to CWD)
        debug: Enable debug logging to console
        working_dir: Working directory for agent subprocess execution (defaults to vault_path)
    """
    from ..config import Config
    
    config = Config()
    
    # Use CWD as vault (requires config file in CWD)
    vault_path = vault_path or Path.cwd()
    max_concurrent = config.get_orchestrator_max_concurrent()

    debug_mode = "[yellow](DEBUG)[/yellow]" if debug else ""
    logger.info(Panel.fit(
        f"[bold cyan]AI4PKM Orchestrator[/bold cyan] {debug_mode}\n"
        f"Vault: {vault_path}\n"
        f"Max concurrent: {max_concurrent}",
        title="Starting"
    ))

    # Create orchestrator (it will load paths from config)
    orch = Orchestrator(
        vault_path=vault_path,
        max_concurrent=max_concurrent,
        config=config,
        working_dir=Path(working_dir) if working_dir else None
    )

    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info("\n[yellow]Received interrupt signal, shutting down...[/yellow]")
        if orch:
            orch.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Show loaded agents
    status = orch.get_status()
    logger.info(f"\n[green]✓[/green] Loaded {status['agents_loaded']} agent(s):")
    for agent_info in status['agent_list']:
        logger.info(
            f"  • [{agent_info['abbreviation']}] {agent_info['name']} "
            f"({agent_info['category']})"
        )

    # Start orchestrator
    logger.info("\n[cyan]Starting orchestrator...[/cyan]")
    orch.run_forever()


def show_orchestrator_status(vault_path: Path = None, working_dir: str = None):
    """
    Show orchestrator status and loaded agents.

    Args:
        vault_path: Path to vault root (defaults to CWD)
        working_dir: Working directory for agent subprocess execution (defaults to vault_path)
    """
    from ..config import Config
    
    config = Config()
    
    # Use CWD as vault (requires config file in CWD)
    vault_path = vault_path or Path.cwd()

    # Create orchestrator just to load agents (don't start)
    orch = Orchestrator(
        vault_path=vault_path,
        config=config,
        working_dir=Path(working_dir) if working_dir else None
    )

    status = orch.get_status()

    logger.info(Panel.fit(
        f"[bold]Vault:[/bold] {status['vault_path']}\n"
        f"[bold]Agents loaded:[/bold] {status['agents_loaded']}\n"
        f"[bold]Max concurrent:[/bold] {status['max_concurrent']}",
        title="Orchestrator Status"
    ))

    if status['agent_list']:
        logger.info("\n[bold]Available Agents:[/bold]")
        for agent_info in status['agent_list']:
            logger.info(
                f"  • [{agent_info['abbreviation']}] {agent_info['name']}\n"
                f"    Category: {agent_info['category']}"
            )

