"""Handler for --list-agents command."""

from pathlib import Path
from rich.console import Console
from rich.table import Table

from ..config import Config
from ..orchestrator.core import Orchestrator
from ..logger import Logger

logger = Logger(console_output=True)


def list_agents():
    """List available AI agents and their status."""
    try:
        config = Config()
        orch = Orchestrator(vault_path=Path.cwd(), config=config)

        if not orch.agent_registry.agents:
            logger.info("[yellow]No agents found.[/yellow]")
            return

        # Create table
        table = Table(title="Available Agents")
        table.add_column("Abbreviation", style="cyan", no_wrap=True)
        table.add_column("Name", style="bold")
        table.add_column("Category", style="green")
        table.add_column("Input Path", style="dim")
        table.add_column("Output Path", style="dim")
        table.add_column("Cron", style="yellow")

        # Sort agents by abbreviation
        sorted_agents = sorted(
            orch.agent_registry.agents.values(),
            key=lambda a: a.abbreviation
        )

        for agent in sorted_agents:
            input_path = (
                ", ".join(agent.input_path)
                if isinstance(agent.input_path, list)
                else (agent.input_path or "—")
            )
            output_path = agent.output_path or "—"
            cron = agent.cron or "—"

            table.add_row(
                agent.abbreviation,
                agent.name,
                agent.category,
                input_path,
                output_path,
                cron,
            )

        logger.info(table)

    except Exception as e:
        logger.info(f"[red]✗ Error listing agents: {e}[/red]")

