"""Example file handlers demonstrating pattern-based processing."""

from ..file_watchdog import BaseFileHandler


class MarkdownFileHandler(BaseFileHandler):
    """Handler for markdown files."""
    
    def process(self, file_path: str, event_type: str) -> None:
        """Process markdown files."""
        self.logger.info(f"Markdown file {event_type}: {file_path}")
        