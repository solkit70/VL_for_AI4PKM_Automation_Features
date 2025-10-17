"""Handler for Limitless markdown files with timestamp tracking."""

import os
import re
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
from .transcription_file_handler import TranscriptionFileHandler


class LimitlessFileHandler(TranscriptionFileHandler):
    """
    Handler for Limitless markdown files.

    Tracks lastSyncTimestamp and filters content to process only new entries.
    Implements deduplication to handle multiple file system events.
    """

    def __init__(self, logger=None, workspace_path=None):
        """Initialize handler with deduplication cache."""
        super().__init__(logger, workspace_path)
        self._processed_cache = {}  # file_path -> (mtime, last_processed_time)

    def process(self, file_path: str, event_type: str) -> None:
        """
        Process Limitless markdown files, filtering by timestamp.

        Implements deduplication to prevent processing the same file multiple times
        when file system generates duplicate events (common with iCloud Drive).

        Args:
            file_path: Path to the Limitless markdown file
            event_type: Type of event ('created' or 'modified')
        """
        # Check if this is a duplicate event
        try:
            file_mtime = os.path.getmtime(file_path)
            now = datetime.now()

            # Check cache for recent processing
            if file_path in self._processed_cache:
                cached_mtime, last_processed = self._processed_cache[file_path]

                # If same mtime and processed within last 2 seconds, skip (duplicate event)
                if cached_mtime == file_mtime and (now - last_processed).total_seconds() < 2:
                    self.logger.debug(f"Skipping duplicate event for {file_path} (processed {(now - last_processed).total_seconds():.2f}s ago)")
                    return

            # Update cache
            self._processed_cache[file_path] = (file_mtime, now)

            # Clean old cache entries (older than 5 minutes)
            self._clean_cache()

        except OSError as e:
            self.logger.warning(f"Could not check file modification time for {file_path}: {e}")
            # Continue processing anyway

        self.logger.info(f"Processing Limitless file {event_type}: {file_path}")

        try:
            # Get last sync timestamp
            last_sync = self.get_last_sync_timestamp()

            if last_sync:
                self.logger.info(f"Last sync was at {last_sync.isoformat()}")
            else:
                self.logger.info("No previous sync timestamp - processing all content")

            # Read and filter the file content
            new_entries = self._read_and_filter_entries(file_path, last_sync)
            
            if new_entries:
                self.logger.info(f"Found {len(new_entries)} new entries to process")
                
                # Detect task creation requests in new entries
                candidates = self._detect_task_creation_requests(new_entries, file_path)
                
                if candidates:
                    self.logger.info(f"Found {len(candidates)} task creation request(s) in new entries")
                    # Save candidates to file (timestamp tracking is now filename-based)
                    self._save_candidates_to_file(candidates)
                else:
                    self.logger.info("No task creation requests found in new entries")
            else:
                self.logger.info("No new entries found")
                
        except Exception as e:
            self.logger.error(f"Error processing Limitless file {file_path}: {e}")
    
    def _read_and_filter_entries(self, file_path: str, last_sync: datetime = None) -> List[Tuple[datetime, str]]:
        """
        Read the Limitless markdown file and filter entries after the last sync timestamp.
        
        Args:
            file_path: Path to the markdown file
            last_sync: Last sync timestamp (None to get all entries)
            
        Returns:
            List of (timestamp, content) tuples for entries after last_sync
        """
        new_entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            entries = self._parse_entries(content)
            
            for timestamp, entry_content in entries:
                if last_sync is None or timestamp > last_sync:
                    new_entries.append((timestamp, entry_content))
                    
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            
        return new_entries
    
    def _parse_entries(self, content: str) -> List[Tuple[datetime, Dict[str, str]]]:
        """
        Parse entries from the Limitless markdown content.
        
        Limitless format has lines like:
        - {SpeakerName} (10/14/25 1:55 PM): content
        
        Examples:
        - Unknown (10/14/25 1:55 PM): content
        - You (10/14/25 10:13 AM): content
        - John Doe (10/14/25 2:30 PM): content
        
        Args:
            content: Full markdown content
            
        Returns:
            List of (timestamp, dict) tuples where dict has "speaker" and "content" keys
        """
        entries = []
        
        pattern = r'-\s+(.+?)\s+\((\d{1,2}/\d{1,2}/\d{2})\s+(\d{1,2}:\d{2}\s+(?:AM|PM))\):'
        
        lines = content.split('\n')
        
        for line in lines:
            match = re.search(pattern, line)
            if match:
                speaker_name = match.group(1).strip()  # Speaker name
                datetime_str = f"{match.group(2)} {match.group(3)}"
                line_content = line[match.end():].strip()

                try:
                    timestamp = datetime.strptime(datetime_str, "%m/%d/%y %I:%M %p")
                    entries.append((timestamp, {"speaker": speaker_name, "content": line_content}))
                except ValueError as e:
                    self.logger.debug(f"Could not parse timestamp: {datetime_str} - {e}")
                    continue

        return sorted(entries, key=lambda x: x[0])

    def _clean_cache(self):
        """Clean old entries from processed cache to prevent memory leaks."""
        now = datetime.now()
        cutoff = now - timedelta(minutes=5)

        # Remove entries older than 5 minutes
        to_remove = [
            path for path, (mtime, last_processed) in self._processed_cache.items()
            if last_processed < cutoff
        ]

        for path in to_remove:
            del self._processed_cache[path]

        if to_remove:
            self.logger.debug(f"Cleaned {len(to_remove)} old entries from deduplication cache")