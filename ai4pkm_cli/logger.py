"""Logging system with file output and real-time tail display."""

import os
import time
import logging
import threading
from datetime import datetime
from threading import Lock
from rich.console import Console
from rich.text import Text


class Logger:
    """Logger that writes to logs.txt and supports real-time tail display."""

    def __init__(self, log_file=None, console_output=True):
        """Initialize logger."""
        if log_file is None:
            # Use current working directory as project root
            project_root = os.getcwd()

            # Create logs directory path
            logs_dir = os.path.join(project_root, "_Settings_", "Logs")

            # Ensure logs directory exists
            os.makedirs(logs_dir, exist_ok=True)

            # Create date-based log filename with ai4pkm prefix
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(logs_dir, f"ai4pkm_{date_str}.log")

        self.log_file = log_file
        self.lock = Lock()
        self.console_output = console_output
        self.console = Console() if console_output else None
        self.thread_log_files = {}  # Track thread-specific log files

        # Print log file path for user reference
        # print(f"📝 Log file: {os.path.abspath(self.log_file)}")

        self._ensure_log_file()
        
    def _ensure_log_file(self):
        """Ensure log file exists and clear it for fresh start."""
        with open(self.log_file, 'w') as f:
            f.write(f"PKM CLI Log - Started at {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n")

    def create_thread_log(self, task_filename: str, phase: str, agent_command: str = None) -> str:
        """Create a thread-specific log file for a task.

        Args:
            task_filename: Task filename (e.g., "2025-10-16 Task.md")
            phase: Phase type ("exec", "eval", or "gen")
            agent_command: Optional shell command used to invoke the agent

        Returns:
            Absolute path to the created log file
        """
        # Extract task name without extension
        task_name = task_filename.replace('.md', '').replace('.json', '')

        # Create log filename
        log_filename = f"{task_name}-{phase}.log"

        # Use project root for logs
        project_root = os.getcwd()
        logs_dir = os.path.join(project_root, "AI", "Tasks", "Logs")

        # Ensure directory exists
        os.makedirs(logs_dir, exist_ok=True)

        # Full log file path
        log_path = os.path.join(logs_dir, log_filename)

        # Initialize log file
        with open(log_path, 'w') as f:
            f.write(f"Task {phase.upper()} Log - Started at {datetime.now().isoformat()}\n")
            f.write(f"Task: {task_filename}\n")
            if agent_command:
                f.write(f"Agent Command: {agent_command}\n")
            f.write("=" * 60 + "\n")

        # Track in dictionary
        thread_name = threading.current_thread().name
        self.thread_log_files[thread_name] = log_path

        return log_path

    def log_agent_command(self, agent_command: str):
        """Append agent command to current thread's log file.

        Args:
            agent_command: The CLI command used to invoke the agent
        """
        thread_name = threading.current_thread().name
        log_path = self.thread_log_files.get(thread_name)

        if log_path:
            try:
                with open(log_path, 'a') as f:
                    f.write(f"Agent Command: {agent_command}\n")
                    f.write("=" * 60 + "\n")
            except Exception as e:
                # Use self.warning instead of self.logger.warning
                pass

    def _should_log(self, level):
        """Check if message should be logged based on current log level."""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        message_level = level_map.get(level, logging.INFO)
        # Use the global logging level set by logging.basicConfig()
        current_level = logging.getLogger().getEffectiveLevel()
        return message_level >= current_level

    def _write_log(self, level, message):
        """Write log entry to file and optionally to console."""
        # Check if this message should be logged based on log level
        if not self._should_log(level):
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get current thread name
        thread_name = threading.current_thread().name
        # Always add thread prefix for visibility
        thread_prefix = f"[{thread_name}] "

        log_entry = f"[{timestamp}] {thread_prefix}{level}: {message}\n"

        with self.lock:
            # Write to main log file
            with open(self.log_file, 'a') as f:
                f.write(log_entry)

            # Also write to thread-specific log file if exists
            if thread_name in self.thread_log_files:
                thread_log_path = self.thread_log_files[thread_name]
                try:
                    with open(thread_log_path, 'a') as f:
                        # For thread-specific log, omit thread name prefix (redundant)
                        simple_entry = f"[{timestamp}] {level}: {message}\n"
                        f.write(simple_entry)
                except Exception as e:
                    # If thread log fails, just continue with main log
                    pass

            # Also print to console if enabled
            if self.console_output and self.console:
                self._display_log_line(self.console, log_entry.rstrip())
                
    def info(self, message):
        """Log info message."""
        self._write_log("INFO", message)
        
    def error(self, message):
        """Log error message."""
        self._write_log("ERROR", message)
        
    def warning(self, message):
        """Log warning message."""
        self._write_log("WARNING", message)
        
    def debug(self, message):
        """Log debug message."""
        self._write_log("DEBUG", message)

    def _display_log_line(self, console, line):
        """Display a single log line with appropriate styling."""
        if not line.strip():
            return
            
        text = Text()
        
        # Parse log line format: [timestamp] [thread] LEVEL: message
        if "] " in line and ": " in line:
            try:
                # Extract timestamp
                timestamp_part = line.split("] ")[0] + "]"
                rest = line.split("] ", 1)[1]
                
                # Extract thread name (always present now)
                thread_part = ""
                if rest.startswith("[") and "] " in rest:
                    thread_part = rest.split("] ")[0] + "]"
                    rest = rest.split("] ", 1)[1]
                
                # Extract level and message
                level_part = rest.split(": ")[0]
                message_part = rest.split(": ", 1)[1]
                
                # Style timestamp
                text.append(timestamp_part, style="dim")
                text.append(" ")
                
                # Style thread name
                if thread_part:
                    text.append(thread_part, style="cyan")
                    text.append(" ")
                
                # Style level with colors
                if level_part == "ERROR":
                    text.append(level_part, style="bold red")
                elif level_part == "WARNING":
                    text.append(level_part, style="bold yellow")
                elif level_part == "INFO":
                    text.append(level_part, style="bold green")
                elif level_part == "DEBUG":
                    text.append(level_part, style="bold blue")
                else:
                    text.append(level_part, style="bold")
                    
                text.append(": ")
                text.append(message_part)
                
            except (IndexError, ValueError):
                # If parsing fails, display line as-is
                text.append(line)
        else:
            text.append(line)
            
        console.print(text)
