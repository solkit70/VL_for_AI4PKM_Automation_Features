"""Handler for task request files that triggers KTG (Knowledge Task Generator)."""

import os
from datetime import datetime
from ..file_watchdog import BaseFileHandler
from ..task_semaphore import get_task_semaphore
from ...agent_factory import AgentFactory
from ...config import Config


class TaskRequestFileHandler(BaseFileHandler):
    """
    Handler for task request markdown files in AI/Tasks/Requests/{source}/.
    
    Automatically triggers the KTG (Knowledge Task Generator) agent
    when new request files are created.
    """
    
    def __init__(self, logger=None, workspace_path=None):
        """
        Initialize the handler.

        Args:
            logger: Logger instance
            workspace_path: Path to the workspace root
        """
        super().__init__(logger, workspace_path)
        self.config = Config()

        # Get generation semaphore (separate from execution)
        from ..task_semaphore import get_generation_semaphore
        self.semaphore = get_generation_semaphore(self.config, self.logger)
    
    def process(self, file_path: str, event_type: str) -> None:
        """
        Process task request files by triggering KTG agent.
        
        Only reacts to file creation, not modification.
        This method returns immediately after spawning a background thread.
        
        Args:
            file_path: Path to the request file
            event_type: Type of event ('created' or 'modified')
        """
        # Only process newly created files
        if event_type != 'created':
            return
        
        # Spawn background thread immediately (don't block watchdog)
        import threading
        thread = threading.Thread(
            target=self._process_async,
            args=(file_path,),
            daemon=True,
            name=f"KTG-{os.path.basename(file_path)}"
        )
        thread.start()
    
    def _process_async(self, file_path: str):
        """Process task request in background thread with semaphore control."""
        import threading
        import json

        # Read request file to get task description for better thread naming
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                request_data = json.load(f)
            task_type = request_data.get('task_type', 'Unknown')
            # Update thread name with task type
            threading.current_thread().name = f"KTG-{task_type}"
        except Exception:
            # If we can't read the file, keep the default name
            pass

        self.logger.info(f"⏳ Waiting for generation slot: {os.path.basename(file_path)}")

        # Acquire semaphore (block if at max concurrent limit)
        with self.semaphore:
            try:
                # Execute KTG with the agent
                self._execute_ktg(file_path)

            except Exception as e:
                self.logger.error(f"Error processing task request file {file_path}: {e}")
    
    def _execute_ktg(self, file_path: str) -> None:
        """
        Execute KTG agent with prompt including system instructions.

        Args:
            file_path: Path to the request file
        """
        try:
            # Read system prompt template
            system_prompt = self._read_system_prompt()

            # Get generation agent from config
            generation_agent = self.config.get_generation_agent()
            
            # Create agent by name
            agent = AgentFactory.create_agent_by_name(generation_agent, self.logger, self.config)

            # Build full prompt
            prompt = f"Run Knowledge Task Generator given the task generation request file in {file_path}"
            if system_prompt:
                prompt += f"\n\n{system_prompt}"

            self.logger.info(f"🚀 KTG → {generation_agent} → {os.path.basename(file_path)}")
            self.logger.debug(f"Request file: {file_path}")

            # Execute the agent using run_prompt
            result = agent.run_prompt(inline_prompt=prompt)

            if result:
                response_text, session_id = result
                self.logger.info("✅ KTG execution completed successfully")
                if session_id:
                    self.logger.info(f"Session ID: {session_id}")
            else:
                self.logger.warning("⚠️ KTG execution completed with no response")

        except Exception as e:
            self.logger.error(f"Error executing KTG: {e}")
        # Note: Request files are NOT deleted after processing
        # They serve as timestamp markers for handlers (Limitless, Gobi) to track
        # what content has already been processed (via get_last_sync_timestamp)

    def _read_system_prompt(self) -> str:
        """Read system prompt from task_generation.md.

        Returns:
            Formatted system prompt or empty string if file not found
        """
        try:
            from datetime import datetime
            import re

            # Get path to system prompt file
            # Handler is in ai4pkm_cli/watchdog/handlers/
            # Need to go up to ai4pkm_cli/ then into prompts/
            handler_dir = os.path.dirname(os.path.abspath(__file__))
            ai4pkm_cli_dir = os.path.dirname(os.path.dirname(handler_dir))
            prompt_file = os.path.join(ai4pkm_cli_dir, "prompts", "task_generation.md")

            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract template between ``` markers in "System Prompt Template" section
                match = re.search(r'## System Prompt Template.*?```\s*\n(.*?)\n```', content, re.DOTALL)
                if match:
                    template = match.group(1).strip()
                    # Get current datetime with seconds (YYYY-MM-DDTHH:MM:SS)
                    current_datetime = datetime.now().isoformat()
                    # Replace placeholders
                    return (template
                           .replace('{ktg_request_prompt}', '')
                           .replace('{current_datetime}', current_datetime))
        except Exception as e:
            self.logger.warning(f"Could not read system prompt: {e}")

        # Fallback to simple instructions
        from datetime import datetime
        current_datetime = datetime.now().isoformat()
        return f"""
IMPORTANT: When creating a task file, include these properties in frontmatter:
- created: {current_datetime} (full ISO format: YYYY-MM-DDTHH:MM:SS)

Write generation logs directly to the task file's ## Process Log section.
Ensure the 'created' property uses full datetime format, not just date.
"""

