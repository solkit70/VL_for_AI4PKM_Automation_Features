"""Handler for Gobi markdown files with timestamp tracking."""

import os
import re
import json
from datetime import datetime
from typing import List, Tuple, Dict
from ..file_watchdog import BaseFileHandler


# Pattern and keywords from ktg_helper.py
TASK_REQUEST_PATTERN = re.compile(r'hey pkm', re.IGNORECASE)
PREFERENCE_KEYWORDS = ["좋겠고", "원해", "필요해", "했으면", "해줘"]

class TranscriptionFileHandler(BaseFileHandler):
    """
    Handler for Transcription markdown files.
    
    Tracks lastSyncTimestamp and filters content to process only new entries.
    """
    
    def _detect_task_creation_requests(self, entries: List[Tuple[datetime, Dict]], file_path: str) -> List[Dict]:
        """
        Detect task creation requests in entries using ktg_helper.py logic.
        
        Args:
            entries: List of (timestamp, dict) tuples where dict has "speaker" and "content" keys
            file_path: Path to the source file
            
        Returns:
            List of candidate dictionaries with file, timestamp, context, and has_preference
        """
        candidates = []

        for i, entry in enumerate(entries):
            entry_timestamp, entry_data = entry
            entry_content = entry_data["content"]
            
            if TASK_REQUEST_PATTERN.search(entry_content):
                # Extract context (surrounding 5 entries before and 5 after)
                context_start = max(0, i - 5)
                context_end = min(len(entries), i + 6)
                
                # Format context lines
                context_lines = []
                for ctx_timestamp, ctx_data in entries[context_start:context_end]:
                    speaker = ctx_data["speaker"]
                    content = ctx_data["content"]
                    # Format with speaker if available
                    if speaker:
                        context_lines.append(f"{ctx_timestamp.strftime('%m/%d/%y %I:%M %p')} {speaker}: {content}")
                    else:
                        context_lines.append(f"{ctx_timestamp.strftime('%Y-%m-%d %H:%M:%S')} {content}")
                
                context = '\n'.join(context_lines)
                
                # Check for preference keywords
                has_preference = any(kw in context for kw in PREFERENCE_KEYWORDS)
                
                candidates.append({
                    "file": file_path,
                    "timestamp": entry_timestamp.isoformat(),
                    "context": context,
                    "has_preference": has_preference,
                })

        return candidates
    
    def _save_candidates_to_file(self, candidates: List[Dict]) -> None:
        """
        Save task creation request candidates to a JSON file.
        
        Saves to: AI/Tasks/Requests/{source}/YYYY-MM-DD-{milliseconds}.json
        
        Args:
            candidates: List of candidate dictionaries
        """
        try:
            # Generate filename: YYYY-MM-DD-{milliseconds}.json
            now = datetime.now()
            date_str = now.strftime('%Y-%m-%d')
            # Get milliseconds since epoch
            milliseconds = int(now.timestamp() * 1000)
            filename = f"{date_str}-{milliseconds}.json"
            
            # Get output directory (AI/Tasks/Requests/{source}/)
            output_dir = self._get_requests_dir()
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, filename)
            
            # Generate JSON content
            content = self._generate_json_content(candidates, now)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(candidates)} task creation request(s) to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving candidates to file: {e}")
    
    def _generate_json_content(self, candidates: List[Dict], generated_time: datetime) -> Dict:
        """
        Generate JSON content for candidates.
        
        Args:
            candidates: List of candidate dictionaries
            generated_time: Time when the file was generated
            
        Returns:
            Dictionary to be serialized as JSON
        """
        return {
            "metadata": {
                "generated": generated_time.strftime('%Y-%m-%d %H:%M:%S'),
                "handler": self.__class__.__name__,
                "total_requests": len(candidates)
            },
            "requests": candidates
        }

