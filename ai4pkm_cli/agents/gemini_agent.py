"""Gemini CLI agent implementation."""

import subprocess
import os
from typing import Optional, Tuple, Dict, Any
from .base_agent import BaseAgent


class GeminiAgent(BaseAgent):
    """Gemini CLI agent implementation."""
    
    def __init__(self, logger, config: Dict[str, Any]):
        """Initialize Gemini agent."""
        super().__init__(logger, config)
        self.command = config.get('command', 'gemini')
        # Use CLI default model when no model specified
        
    def is_available(self) -> bool:
        """Check if Gemini CLI is available."""
        try:
            result = subprocess.run([self.command, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
            
    def get_agent_name(self) -> str:
        """Get the display name of this agent."""
        return "Gemini CLI"
        
    def run_prompt(self, inline_prompt: Optional[str] = None, prompt_name: Optional[str] = None, 
                   params: Optional[Dict[str, Any]] = None, context: Optional[str] = None, 
                   session_id: Optional[str] = None) -> Optional[Tuple[str, Optional[str]]]:
        """Run a prompt using Gemini CLI with auto_edit approval mode by default."""
        prompt_content = self._prepare_prompt_content(inline_prompt, prompt_name, params, context)
        if prompt_content is None:
            return None
            
        try:
            # Execute the prompt using Gemini CLI with auto_edit by default
            result = self._execute_gemini_prompt(prompt_content, approval_mode='auto_edit')
            if result:
                # Log the result
                self.logger.info(result)
                return result, None  # Gemini CLI doesn't support session continuity
            else:
                self.logger.error("No response received from Gemini CLI")
                return None
                
        except Exception as e:
            self.logger.error(f"Error running Gemini prompt: {e}")
            return None
            
    def _execute_gemini_prompt(self, prompt_content: str, approval_mode: Optional[str] = None) -> Optional[str]:
        """Execute the prompt using Gemini CLI."""
        try:
            # Build the command using -p/--prompt for non-interactive mode with quoted prompt
            cmd = [
                self.command,
                '--prompt', f'"{prompt_content}"'
            ]
            
            # Add approval mode if specified
            if approval_mode == 'auto_edit':
                cmd.extend(['--approval-mode', 'auto_edit'])
                self.logger.debug("Added --approval-mode auto_edit to Gemini command")
            
            # Add any additional CLI options from config
            if 'additional_args' in self.config:
                cmd.extend(self.config['additional_args'])
            
            # Execute the command - show full command
            self.logger.debug(f"Executing Gemini command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                self.logger.error(f"Gemini CLI error (exit code {result.returncode}): {result.stderr}")
                return None
                    
        except subprocess.TimeoutExpired:
            self.logger.error("Gemini CLI command timed out")
            return None
        except Exception as e:
            self.logger.error(f"Gemini CLI execution error: {e}")
            return None
