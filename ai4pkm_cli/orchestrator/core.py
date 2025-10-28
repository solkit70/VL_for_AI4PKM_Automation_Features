"""
Orchestrator core - main event loop and coordination.

Ties together file monitoring, agent matching, and execution management.
"""
import logging
import threading
import time
from pathlib import Path
from typing import Optional
from queue import Empty

from .file_monitor import FileSystemMonitor
from .agent_registry import AgentRegistry
from .execution_manager import ExecutionManager
from .models import FileEvent

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Main orchestrator for multi-agent AI4PKM system.

    Coordinates file monitoring, agent matching, and task execution.
    """

    def __init__(
        self,
        vault_path: Path,
        agents_dir: Optional[Path] = None,
        max_concurrent: int = 3,
        poll_interval: float = 1.0
    ):
        """
        Initialize orchestrator.

        Args:
            vault_path: Path to vault root
            agents_dir: Directory containing agent definitions (defaults to vault/_Settings_/Prompts)
            max_concurrent: Maximum concurrent task executions
            poll_interval: Seconds between event queue polls
        """
        self.vault_path = Path(vault_path)
        self.agents_dir = agents_dir or self.vault_path / "_Settings_" / "Prompts"
        self.max_concurrent = max_concurrent
        self.poll_interval = poll_interval

        # Initialize components
        self.agent_registry = AgentRegistry(self.agents_dir, self.vault_path)
        self.execution_manager = ExecutionManager(self.vault_path, max_concurrent)
        self.file_monitor = FileSystemMonitor(self.vault_path, self.agent_registry)

        # Control state
        self._running = False
        self._event_thread: Optional[threading.Thread] = None

        logger.info(f"Orchestrator initialized for vault: {self.vault_path}")
        logger.info(f"Loaded {len(self.agent_registry.agents)} agents")

    def start(self):
        """Start the orchestrator event loop."""
        if self._running:
            logger.warning("Orchestrator already running")
            return

        logger.info("Starting orchestrator...")

        # Start file monitor
        self.file_monitor.start()

        # Start event processing thread
        self._running = True
        self._event_thread = threading.Thread(target=self._event_loop, daemon=True)
        self._event_thread.start()

        logger.info("Orchestrator started successfully")

    def stop(self):
        """Stop the orchestrator event loop."""
        if not self._running:
            logger.warning("Orchestrator not running")
            return

        logger.info("Stopping orchestrator...")

        # Stop event processing
        self._running = False

        # Stop file monitor
        self.file_monitor.stop()

        # Wait for event thread to finish
        if self._event_thread and self._event_thread.is_alive():
            self._event_thread.join(timeout=5.0)

        logger.info("Orchestrator stopped")

    def _event_loop(self):
        """
        Main event processing loop.

        Polls file monitor queue and processes events.
        """
        logger.info("Event loop started")

        while self._running:
            try:
                # Poll event queue with timeout
                try:
                    file_event = self.file_monitor.event_queue.get(timeout=self.poll_interval)
                except Empty:
                    # No events, continue polling
                    continue

                # Process event
                self._process_event(file_event)

            except Exception as e:
                logger.error(f"Error in event loop: {e}", exc_info=True)
                time.sleep(self.poll_interval)

        logger.info("Event loop stopped")

    def _process_event(self, file_event: FileEvent):
        """
        Process a single file event.

        Args:
            file_event: File event to process
        """
        logger.debug(f"Processing event: {file_event.event_type} {file_event.path}")

        # Convert FileEvent to event_data dict
        event_data = {
            'path': file_event.path,
            'event_type': file_event.event_type,
            'is_directory': file_event.is_directory,
            'timestamp': file_event.timestamp,
            'frontmatter': file_event.frontmatter
        }

        # Find matching agents
        matching_agents = self.agent_registry.find_matching_agents(event_data)

        if not matching_agents:
            logger.debug(f"No agents match event: {file_event.path}")
            return

        logger.info(f"Found {len(matching_agents)} matching agent(s) for {file_event.path}")

        # Execute each matching agent
        for agent in matching_agents:
            # Check if we can execute (concurrency limits)
            if not self.execution_manager.can_execute(agent):
                logger.warning(
                    f"Cannot execute {agent.abbreviation}: "
                    f"concurrency limit reached (global={self.execution_manager.get_running_count()}, "
                    f"agent={self.execution_manager.get_agent_running_count(agent.abbreviation)})"
                )
                # TODO: Queue for later execution
                continue

            # Execute in background thread
            execution_thread = threading.Thread(
                target=self._execute_agent,
                args=(agent, event_data),
                daemon=True
            )
            execution_thread.start()

    def _execute_agent(self, agent, event_data):
        """
        Execute an agent task.

        Args:
            agent: AgentDefinition to execute
            event_data: Event data dictionary
        """
        try:
            ctx = self.execution_manager.execute(agent, event_data)

            if ctx.success:
                logger.info(
                    f"✓ {agent.abbreviation} completed successfully "
                    f"(duration: {ctx.duration:.1f}s)"
                )
            else:
                duration_str = f"{ctx.duration:.1f}s" if ctx.duration else "unknown"
                logger.error(
                    f"✗ {agent.abbreviation} failed: {ctx.status} "
                    f"(duration: {duration_str})"
                )
                if ctx.error_message:
                    logger.error(f"  Error: {ctx.error_message}")

        except Exception as e:
            logger.error(f"Unexpected error executing {agent.abbreviation}: {e}", exc_info=True)

    def get_status(self) -> dict:
        """
        Get current orchestrator status.

        Returns:
            Dictionary with status information
        """
        return {
            'running': self._running,
            'vault_path': str(self.vault_path),
            'agents_loaded': len(self.agent_registry.agents),
            'running_executions': self.execution_manager.get_running_count(),
            'max_concurrent': self.max_concurrent,
            'agent_list': [
                {
                    'abbreviation': agent.abbreviation,
                    'name': agent.name,
                    'category': agent.category,
                    'running': self.execution_manager.get_agent_running_count(agent.abbreviation)
                }
                for agent in self.agent_registry.agents.values()
            ]
        }

    def run_forever(self):
        """
        Start orchestrator and run forever (until interrupted).

        Blocks until KeyboardInterrupt or stop() is called.
        """
        self.start()

        try:
            logger.info("Orchestrator running. Press Ctrl+C to stop.")
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()
