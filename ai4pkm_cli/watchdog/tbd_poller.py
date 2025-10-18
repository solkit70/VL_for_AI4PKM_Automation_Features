"""
Periodic TBD task polling as fallback for FSEvents reliability issues.

macOS FSEvents doesn't reliably detect files created by subprocesses (e.g., Claude Code agent).
This poller provides a safety net by periodically scanning for TBD tasks that the file
system observer might have missed.
"""

import os
import time
import threading
from typing import Optional
from datetime import datetime


class TBDTaskPoller:
    """Periodic scanner for TBD tasks as fallback to FSEvents.

    Background:
    - macOS FSEvents uses temporal coalescing of file events
    - Files created by subprocesses may not trigger events visible to parent process
    - Manual testing showed: bash-created files detected instantly, subprocess files missed

    Solution:
    - Poll AI/Tasks/*.md every N seconds
    - Check frontmatter for status: "TBD"
    - Manually trigger TaskProcessor for missed tasks
    - Minimal overhead: Only reads frontmatter of ~10-130 files

    Args:
        workspace_path: Root path of workspace (contains AI/Tasks/)
        task_handler: TaskProcessor instance to trigger for TBD tasks
        interval: Seconds between scans (default: 30, recommended for KTP workflow)
        logger: Optional logger for debugging
    """

    def __init__(self, workspace_path: str, task_handler, interval: int = 30, logger=None):
        self.workspace_path = workspace_path
        self.task_handler = task_handler
        self.interval = interval
        self.logger = logger
        self.running = False
        self.thread = None
        self.processed_cache = set()  # Track {filepath:mtime} to avoid duplicates

    def start(self):
        """Start polling in background daemon thread."""
        if self.running:
            if self.logger:
                self.logger.warning("TBD poller already running")
            return

        self.running = True
        self.thread = threading.Thread(
            target=self._poll_loop,
            daemon=True,  # Don't block program exit
            name="TBD-Poller"
        )
        self.thread.start()

        if self.logger:
            self.logger.info(f"🔄 TBD task polling started ({self.interval}s interval)")

    def stop(self):
        """Stop polling thread gracefully."""
        if not self.running:
            return

        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)

        if self.logger:
            self.logger.info("🔄 TBD task polling stopped")

    def _poll_loop(self):
        """Main polling loop - runs in background thread."""
        while self.running:
            try:
                self._scan_for_tbd_tasks()
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error in TBD polling: {e}", exc_info=True)

            # Sleep in small increments to allow quick shutdown
            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)

    def _scan_for_tbd_tasks(self):
        """Scan AI/Tasks/*.md for TBD status and trigger handler."""
        tasks_dir = os.path.join(self.workspace_path, "AI", "Tasks")

        if not os.path.exists(tasks_dir):
            return

        try:
            files = os.listdir(tasks_dir)
        except OSError as e:
            if self.logger:
                self.logger.warning(f"Cannot read tasks directory: {e}")
            return

        for filename in files:
            if not filename.endswith('.md'):
                continue

            # Skip template/index files
            if filename in ['Tasks.md', 'Task Template.md']:
                continue

            filepath = os.path.join(tasks_dir, filename)

            # Skip if not a file (could be directory)
            if not os.path.isfile(filepath):
                continue

            try:
                # Check cache to avoid re-processing same file
                file_mtime = os.path.getmtime(filepath)
                cache_key = f"{filepath}:{file_mtime}"

                if cache_key in self.processed_cache:
                    continue

                # Quick check: Read only first ~500 chars (frontmatter should be in first few lines)
                with open(filepath, 'r', encoding='utf-8') as f:
                    header = f.read(500)

                    # Look for status: "TBD" in various formats
                    if ('status: "TBD"' in header or
                        "status: 'TBD'" in header or
                        'status: TBD' in header):

                        # Found TBD task - trigger handler
                        if self.logger:
                            self.logger.info(f"🔄 Polling detected TBD task: {filename}")

                        # Trigger TaskProcessor handler
                        self.task_handler.process(filepath, 'modified')

                        # Add to cache to avoid re-processing
                        self.processed_cache.add(cache_key)

                        # Clean old cache entries (older than 1 hour)
                        self._clean_cache()

            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Error checking {filename}: {e}")

    def _clean_cache(self):
        """Remove old cache entries to prevent unbounded growth."""
        # Keep cache size reasonable - if too large, clear old entries
        if len(self.processed_cache) > 1000:
            # Keep only recent half
            self.processed_cache = set(list(self.processed_cache)[-500:])
