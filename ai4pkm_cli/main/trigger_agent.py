"""Handler for --trigger-agent command."""

import time
from pathlib import Path
from rich.console import Console

from ..logger import Logger
from ..config import Config
from ..orchestrator.core import Orchestrator

logger = Logger(console_output=True)

def trigger_orchestrator_agent(abbreviation=None):
    """Trigger an orchestrator agent interactively.
    
    Args:
        abbreviation: Optional agent abbreviation to skip selection UX
    """
    try:
        config = Config()

        # Create orchestrator (but don't start daemon)
        orch = Orchestrator(vault_path=Path.cwd(), config=config)

        agents_list = [agent for agent in orch.agent_registry.agents.values()]
        
        if not agents_list:
            logger.error("No agents found", console=True)
            return

        # If abbreviation provided, skip selection
        if abbreviation:
            abbreviation = abbreviation.upper()
            selected_agent = orch.agent_registry.agents.get(abbreviation)
            if not selected_agent:
                logger.error(f"Agent '{abbreviation}' not found", console=True)
                logger.info(f"[dim]Available agents: {', '.join(sorted(orch.agent_registry.agents.keys()))}[/dim]")
                return
        else:
            # Sort by abbreviation for consistent display
            agents_list.sort(key=lambda a: a.abbreviation)

            # Display available agents
            logger.info("\n[bold blue]Available Orchestrator Agents:[/bold blue]")
            for i, agent in enumerate(agents_list, 1):
                cron_info = f" [dim]cron: {agent.cron}[/dim]" if agent.cron else ""
                output_info = (
                    f" [dim]→ {agent.output_path}[/dim]" if agent.output_path else ""
                )

                logger.info(
                    f"[cyan]{i}.[/cyan] [bold]{agent.name} ({agent.abbreviation})[/bold]"
                )
                logger.info(f"   Category: {agent.category}{cron_info}{output_info}\n")

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
                logger.info(f"\n[green]✓ Agent completed successfully[/green]")
                logger.info(
                    f"[dim]Execution time: {execution_time:.2f}s[/dim]"
                )
                if ctx.task_file:
                    logger.info(f"[dim]Task file: {ctx.task_file.name}[/dim]")
            else:
                error_msg = ctx.error_message if ctx else "Unknown error"
                logger.error(f"✗ Agent failed: {error_msg}")
                logger.info(f"\n[red]✗ Agent failed: {error_msg}[/red]")

        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.error(f"✗ Trigger error ({execution_time:.1f}s): {e}")
            logger.info(
                f"\n[red]✗ Trigger error after {execution_time:.2f}s: {e}[/red]"
            )

    except Exception as e:
        logger.error(f"Error initializing orchestrator: {e}")
        logger.info(f"[red]✗ Error: {e}[/red]")

