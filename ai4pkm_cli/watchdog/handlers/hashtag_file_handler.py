"""Handler for markdown files with #AI hashtag that triggers task creation."""

import os
import re
from datetime import datetime
from ..file_watchdog import BaseFileHandler


class HashtagFileHandler(BaseFileHandler):
    """
    Handler for markdown files containing #AI hashtag.
    
    Automatically creates a task request when #AI hashtag is detected in a file.
    """
    
    def __init__(self, logger=None, workspace_path=None):
        """
        Initialize the handler.
        
        Args:
            logger: Logger instance
            workspace_path: Path to the workspace root
        """
        super().__init__(logger, workspace_path)
        self._processed_files = set()  # Track processed files to avoid duplicates
    
    def process(self, file_path: str, event_type: str) -> None:
        """
        Process markdown files by checking for #AI hashtag.
        
        Reacts to both file creation and modification.
        
        Args:
            file_path: Path to the markdown file
            event_type: Type of event ('created' or 'modified')
        """
        # Create a unique key for this file and its modification time
        try:
            mtime = os.path.getmtime(file_path)
            file_key = f"{file_path}:{mtime}"
            
            # Skip if we've already processed this version of the file
            if file_key in self._processed_files:
                return
            
            # Check if file contains #AI hashtag
            if not self._contains_ai_hashtag(file_path):
                return
            
            self.logger.info(f"Detected #AI hashtag in: {file_path}")
            
            # Create task request
            self._create_task_request(file_path)
            
            # Mark as processed
            self._processed_files.add(file_key)
            
            # Cleanup old entries (keep only last 100)
            if len(self._processed_files) > 100:
                self._processed_files = set(list(self._processed_files)[-100:])
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
    
    def _contains_ai_hashtag(self, file_path: str) -> bool:
        """
        Check if file contains #AI hashtag.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            True if #AI hashtag is found, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for #AI hashtag (word boundary to avoid matching #AIR, #AIDING, etc.)
            # Match #AI as standalone tag or in YAML tags list
            pattern = r'(?:^|\s|-)#AI(?:\s|$|,)'
            return bool(re.search(pattern, content, re.MULTILINE))
            
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return False
    
    def _create_task_request(self, file_path: str) -> None:
        """
        Create a task request file for the file with #AI hashtag.
        
        Saves to: AI/Tasks/Requests/Hashtag/YYYY-MM-DD-{milliseconds}.md
        
        Args:
            file_path: Path to the file with #AI hashtag
        """
        try:
            # Generate filename: YYYY-MM-DD-{milliseconds}.md
            now = datetime.now()
            date_str = now.strftime('%Y-%m-%d')
            milliseconds = int(now.timestamp() * 1000)
            filename = f"{date_str}-{milliseconds}.md"
            
            # Get output directory (AI/Tasks/Requests/Hashtag/)
            output_dir = self._get_requests_dir()
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, filename)
            
            # Generate markdown content
            content = self._generate_request_content(file_path, now)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Created task request: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating task request file: {e}")
    
    def _generate_request_content(self, file_path: str, generated_time: datetime) -> str:
        """
        Generate markdown content for task request.
        
        Args:
            file_path: Path to the file with #AI hashtag
            generated_time: Time when the request was generated
            
        Returns:
            Markdown formatted string
        """
        # Convert to relative path if absolute
        if os.path.isabs(file_path):
            try:
                rel_path = os.path.relpath(file_path, self.workspace_path)
            except ValueError:
                rel_path = file_path
        else:
            rel_path = file_path
        
        lines = []
        
        # Frontmatter
        lines.append("---")
        lines.append(f"generated: {generated_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"handler: {self.__class__.__name__}")
        lines.append("task_type: Hashtag")
        lines.append(f"target_file: {rel_path}")
        lines.append("---")
        lines.append("")
        
        # Title
        lines.append(f"# AI Task Request - {generated_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Description
        lines.append("File with #AI hashtag detected. Requesting task creation.")
        lines.append("")
        
        # Target file
        lines.append("## Target File")
        lines.append("")
        lines.append(f"`{rel_path}`")
        lines.append("")
        
        # Instructions
        lines.append("## Instructions")
        lines.append("")
        lines.append("Review the file content and determine the appropriate action:")
        lines.append("- Create appropriate task(s) based on the context around #AI hashtag")
        lines.append("- Remove or update the #AI hashtag after processing")
        lines.append("")
        
        return '\n'.join(lines)

