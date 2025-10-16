"""Handler for TBD task files that triggers KTP automatically."""

import os
import subprocess
import sys
from datetime import datetime
from ..file_watchdog import BaseFileHandler


class TBDTaskHandler(BaseFileHandler):
    """
    Handler for task files in AI/Tasks/ with TBD status.
    
    Automatically triggers the KTP (Knowledge Task Processor) 
    when a task's status changes to TBD.
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
        
    def process(self, file_path: str, event_type: str) -> None:
        """
        Process task files that have TBD status.
        
        Monitors both file creation and modification to catch:
        - Newly created task files with TBD status
        - Existing task files whose status changed to TBD
        
        Args:
            file_path: Path to the task file
            event_type: Type of event ('created' or 'modified')
        """
        # Skip if not a task file in AI/Tasks directory
        if not self._is_task_file(file_path):
            return
            
        # Read task file and check status
        try:
            task_data = self._read_task_frontmatter(file_path)
            status = task_data.get('status', '').upper()
            
            # Only process TBD tasks
            if status != 'TBD':
                return
                
            # Check if already processed recently (avoid duplicates)
            file_mtime = os.path.getmtime(file_path)
            cache_key = f"{file_path}:{file_mtime}"
            
            if cache_key in self.processed_cache:
                return
                
            # Mark as processed
            self.processed_cache[cache_key] = datetime.now()
            
            # Clean old cache entries (older than 1 hour)
            self._clean_cache()
            
            # Trigger KTP for this task
            self.logger.info(f"TBD task detected: {os.path.basename(file_path)}")
            self._trigger_ktp(file_path)
            
        except Exception as e:
            self.logger.error(f"Error processing TBD task {file_path}: {e}")
    
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
        """Read YAML frontmatter from task file.
        
        Args:
            file_path: Path to task file
            
        Returns:
            Dictionary of frontmatter fields
        """
        import re
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return {}
            
        yaml_content = match.group(1)
        frontmatter = {}
        
        # Simple YAML parser
        for line in yaml_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                    
                frontmatter[key] = value
                
        return frontmatter
    
    def _trigger_ktp(self, task_file: str):
        """Trigger KTP for the specified task.
        
        Args:
            task_file: Path to task file
        """
        # Get just the filename
        task_filename = os.path.basename(task_file)
        
        self.logger.info(f"🚀 Triggering KTP for task: {task_filename}")
        
        # Option 1: Run KTP directly via Python (preferred for integration)
        try:
            # Import and run KTP
            from ...commands.ktp_runner import KTPRunner
            from ...config import Config
            
            config = Config()
            runner = KTPRunner(self.logger, config)
            runner.run_tasks(task_file=task_filename)
            
            self.logger.info("✅ KTP processing completed")
            
        except Exception as e:
            self.logger.error(f"Error running KTP: {e}")
            self.logger.error(f"Error type: {type(e).__name__}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Option 2: Fallback to subprocess call
            self.logger.info("Falling back to subprocess KTP execution")
            try:
                cmd = [sys.executable, '-m', 'ai4pkm_cli.main', '--ktp-task', task_filename]
                self.logger.info(f"Running command: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd,
                    cwd=self.workspace_path,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    self.logger.info("✅ KTP subprocess completed")
                else:
                    self.logger.error(f"KTP subprocess failed with code {result.returncode}")
                    self.logger.error(f"STDERR: {result.stderr}")
                    self.logger.error(f"STDOUT: {result.stdout}")
                    
            except subprocess.TimeoutExpired:
                self.logger.error("KTP subprocess timed out")
            except FileNotFoundError as e2:
                self.logger.error(f"File not found in subprocess: {e2}")
                self.logger.error(f"Python executable: {sys.executable}")
                self.logger.error(f"Working directory: {self.workspace_path}")
            except Exception as e2:
                self.logger.error(f"Error running KTP subprocess: {e2}")
                self.logger.error(f"Error type: {type(e2).__name__}")
    
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


# Export the handler class
__all__ = ['TBDTaskHandler']

