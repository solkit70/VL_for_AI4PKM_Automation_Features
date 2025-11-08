#!/usr/bin/env python3
"""Main entry point for PKM CLI."""

import signal
import sys
import click
import logging

from .trigger_agent import trigger_orchestrator_agent
from .list_agents import list_agents as list_agents_handler
from .show_config import show_config as show_config_handler
from .orchestrator import run_orchestrator_daemon, show_orchestrator_status


def signal_handler(sig, frame):
    """Handle SIGINT (Ctrl+C) gracefully."""
    print("\n\nShutting down PKM CLI...")
    sys.exit(0)


@click.command()
@click.option(
    "-o",
    "--orchestrator",
    "orchestrator",
    is_flag=True,
    help="Run orchestrator daemon (new multi-agent system)",
)
@click.option(
    "--orchestrator-status",
    is_flag=True,
    help="Show orchestrator status and loaded agents",
)
@click.option(
    "-t",
    "--trigger-agent",
    "trigger_agent",
    is_flag=True,
    help="Trigger an orchestrator agent interactively once",
)
@click.argument("agent_abbreviation", required=False)
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
@click.option(
    "--list-agents", is_flag=True, help="List available AI agents and their status"
)
@click.option("--show-config", is_flag=True, help="Show current configuration")
def main(
    orchestrator,
    orchestrator_status,
    trigger_agent,
    agent_abbreviation,
    debug,
    list_agents,
    show_config,
):
    """PKM CLI - Personal Knowledge Management framework."""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if orchestrator or orchestrator_status:
        # Use new orchestrator system
        if orchestrator_status:
            show_orchestrator_status()
        else:
            run_orchestrator_daemon(debug=debug)
    elif trigger_agent:
        # Trigger an orchestrator agent interactively once
        trigger_orchestrator_agent(abbreviation=agent_abbreviation)
    elif list_agents:
        # List available agents
        list_agents_handler()
    elif show_config:
        # Show current configuration
        show_config_handler()
    else:
        click.echo(main.get_help(click.get_current_context()))


if __name__ == "__main__":
    main()

