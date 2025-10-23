"""Handler for UNDER_REVIEW task files that triggers evaluation (KTP Phase 3)."""

import os
import subprocess
import sys
import threading
from datetime import datetime
from ..file_watchdog import BaseFileHandler


class TaskEvaluator(BaseFileHandler):
    """
    Handler for task files in AI/Tasks/ with PROCESSED status.

    Automatically triggers the KTP (Knowledge Task Processor) evaluation
    when a task's status is PROCESSED.
    """
    
    def __init__(self, logger=None, workspace_path=None):
        """
        Initialize the handler.

        Args:
            logger: Logger instance
            workspace_path: Path to the workspace root
        """
        super().__init__(logger, workspace_path)
        self.processed_cache = {}  # Track processed files to avoid duplicates

        # Get execution semaphore (separate from generation)
        from ...config import Config
        from ..task_semaphore import get_execution_semaphore
        config = Config()
        self.semaphore = get_execution_semaphore(config, self.logger)
        
    def process(self, file_path: str, event_type: str) -> None:
        """
        Process task files that have PROCESSED status.

        Monitors both file creation and modification to catch:
        - Newly created task files with PROCESSED status
        - Existing task files whose status changed to PROCESSED

        This method returns immediately after spawning a background thread.

        Args:
            file_path: Path to the task file
            event_type: Type of event ('created' or 'modified')
        """
        # Quick check if it's a task file (minimal I/O)
        if not self._is_task_file(file_path):
            return
        
        # Spawn background thread immediately for all processing
        thread = threading.Thread(
            target=self._process_async,
            args=(file_path,),
            daemon=True,
            name=f"KTP-eval-{os.path.basename(file_path)}"
        )
        thread.start()
    
    def _process_async(self, file_path: str):
        """Process task file in background thread (with file I/O and semaphore control)."""
        try:
            # Read task file and check status
            task_data = self._read_task_frontmatter(file_path)
            status = task_data.get('status', '').upper()

            # Only process PROCESSED tasks
            # Any other status means already in evaluation pipeline or complete
            if status != 'PROCESSED':
                return

            # Check if already processed recently (avoid duplicates from FSEvents)
            file_mtime = os.path.getmtime(file_path)
            cache_key = f"{file_path}:{file_mtime}:PROCESSED"

            if cache_key in self.processed_cache:
                self.logger.debug(f"Cache hit for {os.path.basename(file_path)}, skipping")
                return

            # Mark as processed in cache
            self.processed_cache[cache_key] = datetime.now()

            # Clean old cache entries (older than 1 hour)
            self._clean_cache()

            # Determine evaluation agent and update thread name
            from ...config import Config
            config = Config()
            agent_name = config.get_evaluation_agent()
            agent_short = agent_name.replace('_cli', '').replace('_code', '')  # claude, gemini, codex

            # Get task title for better thread naming
            task_title = task_data.get('title', os.path.basename(file_path).replace('.md', ''))

            # Update thread name with agent type and title
            threading.current_thread().name = f"KTP-eval-{agent_short}-{task_title}"

            # Log detection and trigger KTP evaluation
            self.logger.info(f"📋 PROCESSED task detected: {os.path.basename(file_path)}")
            self._trigger_evaluation(file_path)

        except Exception as e:
            self.logger.error(f"Error processing PROCESSED task {file_path}: {e}")
    
    def _is_task_file(self, file_path: str) -> bool:
        """Check if file is a task file in AI/Tasks directory.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if it's a task file
        """
        # Normalize paths
        file_path = os.path.abspath(file_path)
        tasks_dir = os.path.join(self.workspace_path, "AI", "Tasks")
        
        # Must be in AI/Tasks directory (not subdirectories)
        if not file_path.startswith(tasks_dir):
            return False
            
        # Must be markdown file
        if not file_path.endswith('.md'):
            return False
            
        # Must be directly in AI/Tasks (not in Requests subdirectory)
        rel_path = os.path.relpath(file_path, tasks_dir)
        if os.path.sep in rel_path:
            return False
            
        # Skip the Tasks.md index file
        if os.path.basename(file_path) == 'Tasks.md':
            return False
            
        return True
    
    def _read_task_frontmatter(self, file_path: str) -> dict:
        """Read frontmatter from task file.
        
        Args:
            file_path: Path to task file
            
        Returns:
            Dictionary of frontmatter properties
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple frontmatter extraction
            if not content.startswith('---'):
                return {}
                
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {}
                
            yaml_content = parts[1]
            frontmatter = {}
            
            for line in yaml_content.split('\n'):
                line = line.strip()
                if not line or ':' not in line:
                    continue
                    
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                
                frontmatter[key] = value
                
            return frontmatter
            
        except Exception as e:
            self.logger.error(f"Error reading frontmatter from {file_path}: {e}")
            return {}
    
    def _trigger_evaluation(self, task_file: str):
        """Trigger KTP evaluation for the specified task.
        
        Args:
            task_file: Path to task file
        """
        # Get just the filename
        task_filename = os.path.basename(task_file)
        
        # Acquire semaphore (block if at max concurrent limit)
        self.logger.info(f"⏳ Waiting for evaluation slot: {task_filename}")
        with self.semaphore:
            self.logger.info(f"🔎 Evaluating task: {task_filename}")
            
            # Run KTP evaluation
            self._evaluate_task(task_filename)
    
    def _evaluate_task(self, task_filename: str):
        """Evaluate the task (runs within semaphore context).

        Args:
            task_filename: Task filename
        """
        try:
            # Create thread-specific log file
            log_path = self.logger.create_thread_log(task_filename, phase="eval")
            self.logger.info(f"📝 Thread log created: {log_path}")

            # Import and run KTP evaluation
            from ...commands.ktp_runner import KTPRunner
            from ...config import Config

            config = Config()
            runner = KTPRunner(self.logger, config)
            runner.evaluate_task(task_filename)

            self.logger.info(f"✅ KTP evaluation completed: {task_filename}")

            # Update task file with evaluation log link
            self._add_log_link_to_task(task_filename, log_path, "evaluation_log")

        except Exception as e:
            self.logger.error(f"Error running KTP evaluation: {e}")
            self.logger.error(f"Error type: {type(e).__name__}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _clean_cache(self):
        """Clean old entries from processed cache."""
        from datetime import timedelta

        now = datetime.now()
        cutoff = now - timedelta(hours=1)

        # Remove old entries
        to_remove = [
            key for key, timestamp in self.processed_cache.items()
            if timestamp < cutoff
        ]

        for key in to_remove:
            del self.processed_cache[key]

    def _add_log_link_to_task(self, task_filename: str, log_path: str, property_name: str):
        """Add log file link to task frontmatter.

        Args:
            task_filename: Task filename
            log_path: Absolute path to log file
            property_name: Property name (execution_log or evaluation_log)
        """
        try:
            task_path = os.path.join(self.workspace_path, "AI", "Tasks", task_filename)

            # Read task file
            with open(task_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse frontmatter
            if not content.startswith('---'):
                self.logger.warning(f"Task file {task_filename} has no frontmatter")
                return

            parts = content.split('---', 2)
            if len(parts) < 3:
                self.logger.warning(f"Task file {task_filename} has invalid frontmatter")
                return

            frontmatter = parts[1]
            body = parts[2]

            # Convert absolute log path to relative wiki link
            # From: /Users/.../AI/Tasks/Logs/2025-10-16 Task-eval.log
            # To: [[Tasks/Logs/2025-10-16 Task-eval]]
            log_relative = os.path.relpath(log_path, os.path.join(self.workspace_path, "AI"))
            log_link = log_relative.replace('.log', '').replace(os.sep, '/')
            wiki_link = f"[[{log_link}]]"

            # Add or update property in frontmatter
            lines = frontmatter.split('\n')
            updated = False
            new_lines = []

            for line in lines:
                if line.strip().startswith(f'{property_name}:'):
                    new_lines.append(f'{property_name}: "{wiki_link}"')
                    updated = True
                else:
                    new_lines.append(line)

            if not updated:
                # Add new property before the last line
                if new_lines and new_lines[-1].strip() == '':
                    new_lines.insert(-1, f'{property_name}: "{wiki_link}"')
                else:
                    new_lines.append(f'{property_name}: "{wiki_link}"')

            # Rebuild content
            new_frontmatter = '\n'.join(new_lines)
            new_content = f"---{new_frontmatter}---{body}"

            # Write back
            with open(task_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            self.logger.info(f"Added {property_name} link to task: {wiki_link}")

        except Exception as e:
            self.logger.error(f"Error adding log link to task: {e}")


# Export the handler class
__all__ = ['TaskEvaluator']

