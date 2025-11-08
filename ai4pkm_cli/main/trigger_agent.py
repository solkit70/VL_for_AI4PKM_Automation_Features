"""Handler for --trigger-agent command."""

import time
from pathlib import Path
from rich.console import Console

from ..logger import Logger
from ..config import Config
from ..orchestrator.core import Orchestrator

logger = Logger()
console = Console()


def trigger_orchestrator_agent():
    """Trigger an orchestrator agent interactively."""
    try:
        config = Config()

        # Create orchestrator (but don't start daemon)
        orch = Orchestrator(vault_path=Path.cwd(), config=config)

        # Get agents that can be triggered manually
        # Include: agents with cron schedules (can run on-demand)
        # Exclude: pure file-based agents (no cron, need specific file events)
        agents_list = []
        for abbr, agent in orch.agent_registry.agents.items():
            # Show agents that have a cron schedule (scheduled agents)
            # These can be triggered manually and will work without specific file input
            if agent.cron:
                agents_list.append(agent)
            # Also show agents with no input_path and no cron (manual agents)
            elif not agent.input_path or (isinstance(agent.input_path, list) and not any(agent.input_path)):
                agents_list.append(agent)

        if not agents_list:
            logger.error("No triggerable agents found")
            logger.error(
                "[yellow]No agents available for manual trigger.[/yellow]"
            )
            logger.error(
                "[dim]File-based agents (EIC, CTP) require file events to trigger.[/dim]"
            )
            return

        # Sort by abbreviation for consistent display
        agents_list.sort(key=lambda a: a.abbreviation)

        # Display available agents
        console.print("\n[bold blue]Available Orchestrator Agents:[/bold blue]")
        for i, agent in enumerate(agents_list, 1):
            cron_info = f" [dim]cron: {agent.cron}[/dim]" if agent.cron else ""
            input_info = (
                f" [dim]→ {agent.output_path}[/dim]" if agent.output_path else ""
            )

            console.print(
                f"[cyan]{i}.[/cyan] [bold]{agent.name} ({agent.abbreviation})[/bold]"
            )
            console.print(f"   Category: {agent.category}{cron_info}{input_info}\n")

        # Get user selection
        try:
            choice = input(
                f"Enter agent number (1-{len(agents_list)}) or 'q' to quit: "
            ).strip()

            if choice.lower() == "q":
                logger.info("Trigger cancelled by user")
                return

            agent_index = int(choice) - 1
            if agent_index < 0 or agent_index >= len(agents_list):
                logger.error(
                    f"Invalid choice: {choice}. Please enter a number between 1 and {len(agents_list)}"
                )
                return

        except ValueError:
            logger.error(f"Invalid input: {choice}. Please enter a number or 'q'")
            return
        except KeyboardInterrupt:
            logger.info("\nTrigger cancelled by user")
            return

        # Trigger the selected agent
        selected_agent = agents_list[agent_index]
        logger.info(f"Triggering agent: {selected_agent.abbreviation}")
        
        start_time = time.time()

        try:
            # Trigger agent once (synchronously)
            ctx = orch.trigger_agent_once(selected_agent.abbreviation)

            end_time = time.time()
            execution_time = end_time - start_time

            if ctx and ctx.success:
                logger.info(
                    f"✓ Agent completed successfully ({execution_time:.1f}s)"
                )
                console.print(f"\n[green]✓ Agent completed successfully[/green]")
                console.print(
                    f"[dim]Execution time: {execution_time:.2f}s[/dim]"
                )
                if ctx.task_file:
                    console.print(f"[dim]Task file: {ctx.task_file.name}[/dim]")
            else:
                error_msg = ctx.error_message if ctx else "Unknown error"
                logger.error(f"✗ Agent failed: {error_msg}")
                console.print(f"\n[red]✗ Agent failed: {error_msg}[/red]")

        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.error(f"✗ Trigger error ({execution_time:.1f}s): {e}")
            console.print(
                f"\n[red]✗ Trigger error after {execution_time:.2f}s: {e}[/red]"
            )

    except Exception as e:
        logger.error(f"Error initializing orchestrator: {e}")
        console.print(f"[red]✗ Error: {e}[/red]")

