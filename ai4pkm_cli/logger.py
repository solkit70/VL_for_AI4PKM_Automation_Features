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

        # Print log file path for user reference
        # print(f"📝 Log file: {os.path.abspath(self.log_file)}")

        self._ensure_log_file()
        
    def _ensure_log_file(self):
        """Ensure log file exists and clear it for fresh start."""
        with open(self.log_file, 'w') as f:
            f.write(f"PKM CLI Log - Started at {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n")

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
