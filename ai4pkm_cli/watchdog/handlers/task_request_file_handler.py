"""Handler for task request files that triggers KTG (Knowledge Task Generator)."""

import os
from datetime import datetime
from ..file_watchdog import BaseFileHandler
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
    
    def process(self, file_path: str, event_type: str) -> None:
        """
        Process task request files by triggering KTG agent.
        
        Only reacts to file creation, not modification.
        
        Args:
            file_path: Path to the request file
            event_type: Type of event ('created' or 'modified')
        """
        # Only process newly created files
        if event_type != 'created':
            return
        
        self.logger.info(f"Processing task request file: {file_path}")
        
        try:
            # Execute KTG with the agent
            self._execute_ktg(file_path)
            
        except Exception as e:
            self.logger.error(f"Error processing task request file {file_path}: {e}")
    
    def _execute_ktg(self, file_path: str) -> None:
        """
        Execute KTG agent with a simple prompt.
        
        Args:
            file_path: Path to the request file
        """
        try:
            # Create agent
            agent = AgentFactory.create_agent(self.logger, self.config)
            
            # Simple prompt
            prompt = f"Run Knowledge Task Generator given the task generation request file in {file_path}"
            
            self.logger.info("🤖 Executing Knowledge Task Generator (KTG)")
            self.logger.info(f"Request file: {file_path}")
            
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

