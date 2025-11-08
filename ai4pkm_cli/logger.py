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

    _instances = {}
    _lock = Lock()

    def __new__(cls, log_file=None, console_output=False):
        """Singleton pattern: return same instance for same parameters."""
        # Create a key based on log_file and console_output
        key = (log_file, console_output)
        
        if key not in cls._instances:
            with cls._lock:
                # Double-check after acquiring lock
                if key not in cls._instances:
                    instance = super().__new__(cls)
                    cls._instances[key] = instance
                    instance._initialized = False
        return cls._instances[key]

    def __init__(self, log_file=None, console_output=False):
        """Initialize logger (only once per instance)."""
        if self._initialized:
            return
            
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
        self.console = Console()

        # Print log file path for user reference
        # print(f"📝 Log file: {os.path.abspath(self.log_file)}")

        self._ensure_log_file()

        logging.basicConfig(level=logging.INFO)
        
        self._initialized = True
        
    def _ensure_log_file(self):
        """Ensure log file exists and add header if it's a new file."""
        # Only write header if file doesn't exist
        if not os.path.exists(self.log_file):
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

    def _write_log(self, level, message, exc_info=False, console=False):
        """Write log entry to file and optionally to console."""
        # Check if this message should be logged based on log level
        if not self._should_log(level):
            return

        import traceback
        import sys

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get current thread name
        thread_name = threading.current_thread().name
        # Always add thread prefix for visibility
        thread_prefix = f"[{thread_name}] "

        log_entry = f"[{timestamp}] {thread_prefix}{level}: {message}\n"

        # Add traceback if exc_info is True
        if exc_info:
            exc_type, exc_value, exc_tb = sys.exc_info()
            if exc_type is not None:
                tb_lines = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
                if tb_lines.strip():
                    log_entry += tb_lines

        with self.lock:
            # Write to main log file
            with open(self.log_file, 'a') as f:
                f.write(log_entry)

            # Print to console if requested (message only, no formatting)
            if console or self.console_output:
                self.console.print(message)
                
    def info(self, message, exc_info=False, console=False):
        """Log info message.
        
        Args:
            message: Message to log
            exc_info: Include exception traceback if True
            console: Print to console (message only, no formatting) if True
        """
        self._write_log("INFO", message, exc_info=exc_info, console=console)
        
    def error(self, message, exc_info=False, console=False):
        """Log error message.
        
        Args:
            message: Message to log
            exc_info: Include exception traceback if True
            console: Print to console (message only, no formatting) if True
        """
        self._write_log("ERROR", message, exc_info=exc_info, console=console)
        
    def warning(self, message, exc_info=False, console=False):
        """Log warning message.
        
        Args:
            message: Message to log
            exc_info: Include exception traceback if True
            console: Print to console (message only, no formatting) if True
        """
        self._write_log("WARNING", message, exc_info=exc_info, console=console)
        
    def debug(self, message, exc_info=False, console=False):
        """Log debug message.
        
        Args:
            message: Message to log
            exc_info: Include exception traceback if True
            console: Print to console (message only, no formatting) if True
        """
        self._write_log("DEBUG", message, exc_info=exc_info, console=console)

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
