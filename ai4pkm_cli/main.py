#!/usr/bin/env python3
"""Main entry point for PKM CLI."""

import signal
import sys
import click
from .cli import PKMApp
import logging

from dotenv import load_dotenv
import json

load_dotenv()


def signal_handler(sig, frame):
    """Handle SIGINT (Ctrl+C) gracefully."""
    print("\n\nShutting down PKM CLI...")
    sys.exit(0)


@click.command()
@click.option("-p", "--prompt", help="Execute a one-time prompt")
@click.option("-cmd", "--command", help="Execute a one-time command")
@click.option("-args", "--arguments", help="Arguments for the command", default="{}")
@click.option(
    "--ktp",
    is_flag=True,
    help="Run Knowledge Task Processor (process tasks from AI/Tasks/)",
)
@click.option(
    "--ktp-task",
    help="Process specific task file with KTP (e.g., 2025-10-16-task.md)",
)
@click.option(
    "--ktp-priority",
    type=click.Choice(["P0", "P1", "P2", "P3"], case_sensitive=False),
    help="Filter KTP tasks by priority",
)
@click.option(
    "--ktp-status",
    type=click.Choice(["TBD", "IN_PROGRESS", "UNDER_REVIEW"], case_sensitive=False),
    help="Filter KTP tasks by status (default: TBD)",
)
@click.option(
    "-t",
    "--test",
    "test_cron",
    is_flag=True,
    help="Test a specific cron job interactively",
)
@click.option(
    "-c", "--cron", "run_cron", is_flag=True, help="Run continuous cron job scheduler"
)
@click.option(
    "-a",
    "--agent",
    help="Override agent for prompt execution (c/claude, g/gemini, o/codex) - only usable with -p",
)
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
@click.option(
    "--list-agents", is_flag=True, help="List available AI agents and their status"
)
@click.option("--show-config", is_flag=True, help="Show current configuration")
def main(
    prompt,
    command,
    arguments,
    ktp,
    ktp_task,
    ktp_priority,
    ktp_status,
    test_cron,
    run_cron,
    agent,
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

    # Initialize the PKM application
    # Suppress default agent logging when using agent override for prompts
    suppress_logging = bool(agent and prompt)
    app = PKMApp(suppress_agent_logging=suppress_logging)

    if list_agents:
        # List available agents
        app.list_agents()
    elif show_config:
        # Show current configuration
        app.show_config()
    elif ktp or ktp_task:
        # Run Knowledge Task Processor
        ktp_args = {}
        if ktp_task:
            ktp_args["task"] = ktp_task
        if ktp_priority:
            ktp_args["priority"] = ktp_priority.upper()
        if ktp_status:
            ktp_args["status"] = ktp_status.upper()
        
        app.execute_command("ktp", ktp_args)
    elif agent and not prompt:
        # Error: agent option can only be used with prompts
        click.echo(
            "❌ Error: The --agent (-a) option can only be used with --prompt (-p)"
        )
        click.echo(
            "   Use 'ai4pkm --show-config' to view/change the default agent in ai4pkm_cli.json"
        )
        sys.exit(1)
    elif prompt:
        # Execute the prompt (with optional agent for this execution only)
        app.execute_prompt(prompt, agent)
    elif command:
        # Execute the command
        app.execute_command(command, json.loads(arguments))
    elif test_cron:
        # Test a specific cron job
        app.test_cron_job()
    elif run_cron:
        # Run continuously with cron jobs and log display
        app.run_continuous()
    else:
        # Show default information (config and instructions)
        app.show_default_info()


if __name__ == "__main__":
    main()