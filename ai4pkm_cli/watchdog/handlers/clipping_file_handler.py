"""Handler for Clipping markdown files that triggers EIC (Enrich Ingested Content)."""

import os
from datetime import datetime
from ..file_watchdog import BaseFileHandler


class ClippingFileHandler(BaseFileHandler):
    """
    Handler for clipping markdown files in Ingest/Clippings/.
    
    Automatically creates EIC task request when new clipping files are created
    (excluding files that already have "EIC" in their filename).
    """
    
    def process(self, file_path: str, event_type: str) -> None:
        """
        Process clipping files by creating EIC task request.
        
        Only reacts to file creation, not modification.
        Skips files that already contain "EIC" in the filename.
        
        Args:
            file_path: Path to the clipping file
            event_type: Type of event ('created' or 'modified')
        """
        # Only process newly created files
        if event_type != 'created':
            return
        
        # Skip files that already have "EIC" in the filename
        filename = os.path.basename(file_path)
        if 'EIC' in filename:
            self.logger.info(f"Skipping file with EIC in name: {file_path}")
            return
        
        self.logger.info(f"Creating EIC task request for: {file_path}")
        
        try:
            # Create EIC task request file
            self._create_eic_request(file_path)
            
        except Exception as e:
            self.logger.error(f"Error creating EIC task request for {file_path}: {e}")
    
    def _create_eic_request(self, file_path: str) -> None:
        """
        Create an EIC task request file for the clipping.
        
        Saves to: AI/Tasks/Requests/Clippings/YYYY-MM-DD-{milliseconds}.md
        
        Args:
            file_path: Path to the clipping file
        """
        try:
            # Generate filename: YYYY-MM-DD-{milliseconds}.md
            now = datetime.now()
            date_str = now.strftime('%Y-%m-%d')
            milliseconds = int(now.timestamp() * 1000)
            filename = f"{date_str}-{milliseconds}.md"
            
            # Get output directory (AI/Tasks/Requests/Clippings/)
            output_dir = self._get_requests_dir()
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, filename)
            
            # Generate markdown content
            content = self._generate_request_content(file_path, now)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Created EIC task request: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating EIC request file: {e}")
    
    def _generate_request_content(self, file_path: str, generated_time: datetime) -> str:
        """
        Generate markdown content for EIC task request.
        
        Args:
            file_path: Path to the clipping file
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
        lines.append("task_type: EIC")
        lines.append(f"target_file: {rel_path}")
        lines.append("---")
        lines.append("")
        
        # Title
        lines.append(f"# EIC Task Request - {generated_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Description
        lines.append("New clipping file detected. Requesting EIC (Enrich Ingested Content) processing.")
        lines.append("")
        
        # Target file
        lines.append("## Target File")
        lines.append("")
        lines.append(f"`{rel_path}`")
        lines.append("")
        
        return '\n'.join(lines)

