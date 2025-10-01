"""Codex CLI agent implementation."""

import subprocess
from typing import Optional, Tuple, Dict, Any
from .base_agent import BaseAgent


class CodexAgent(BaseAgent):
    """Codex CLI agent implementation."""
    
    def __init__(self, logger, config: Dict[str, Any]):
        """Initialize Codex agent."""
        super().__init__(logger, config)
        self.command = config.get('command', 'codex')
        # Use CLI default model when no model specified
        
    def is_available(self) -> bool:
        """Check if Codex CLI is available."""
        try:
            result = subprocess.run([self.command, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
            
    def get_agent_name(self) -> str:
        """Get the display name of this agent."""
        return "Codex CLI"
        
    def run_prompt(self, inline_prompt: Optional[str] = None, prompt_name: Optional[str] = None, 
                   params: Optional[Dict[str, Any]] = None, context: Optional[str] = None, 
                   session_id: Optional[str] = None) -> Optional[Tuple[str, Optional[str]]]:
        """Run a prompt using Codex CLI with full_auto and search enabled by default."""
        prompt_content = self._prepare_prompt_content(inline_prompt, prompt_name, params, context)
        if prompt_content is None:
            return None
            
        try:
            # Execute the prompt using Codex CLI with full_auto and search by default
            result = self._execute_codex_prompt(prompt_content)
            if result:
                # Log the result
                self.logger.info(result)
                return result, None  # Codex CLI doesn't support session continuity
            else:
                self.logger.error("No response received from Codex CLI")
                return None
                
        except Exception as e:
            self.logger.error(f"Error running Codex prompt: {e}")
            return None
            
    def _execute_codex_prompt(self, prompt_content: str) -> Optional[str]:
        """Execute the prompt using Codex CLI with full_auto and search enabled by default."""
        try:
            # Build the command - flags need to come before 'exec'
            cmd = [self.command]
            
            # Add --search by default for Codex (global flag)
            cmd.append('--search')
            self.logger.debug("Added --search flag to Codex command (default)")
            
            # Add exec subcommand and additional flags
            cmd.append('exec')
            
            # Always add full-auto flag (exec-specific flag)
            cmd.append('--full-auto')
            self.logger.debug("Added --full-auto flag to Codex command (default)")
            
            # Add the prompt content
            cmd.append(f'"{prompt_content}"')
            
            # Add any additional CLI options from config
            if 'additional_args' in self.config:
                cmd.extend(self.config['additional_args'])
            
            # Execute the command - show full command
            self.logger.debug(f"Executing Codex command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                self.logger.error(f"Codex CLI error (exit code {result.returncode}): {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error("Codex CLI command timed out")
            return None
        except Exception as e:
            self.logger.error(f"Codex CLI execution error: {e}")
            return None
