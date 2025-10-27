"""Claude Code CLI agent implementation."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from .base_agent import BaseAgent


class ClaudeAgent(BaseAgent):
    """Claude Code CLI agent implementation."""

    def __init__(self, logger, config: Dict[str, Any]):
        """Initialize Claude agent."""
        super().__init__(logger, config)
        self.claude_path = self._find_claude_cli()

    def _find_claude_cli(self):
        """Find the Claude CLI executable."""
        # First try the user's local installation
        local_path = Path.home() / ".claude" / "local" / "claude"
        if local_path.exists():
            return str(local_path)

        # Try to find it in PATH
        try:
            result = subprocess.run(
                ["which", "claude"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            self.logger.warning(f"Could not find claude in PATH: {e}")

        # Last resort: try common locations
        common_paths = [
            "/usr/local/bin/claude",
            str(Path.home() / "node_modules" / ".bin" / "claude"),
        ]
        for path in common_paths:
            if Path(path).exists():
                return path

        return None

    def is_available(self) -> bool:
        """Check if Claude CLI is available."""
        return self.claude_path is not None
        
    def get_agent_name(self) -> str:
        """Get the display name of this agent."""
        return "Claude Code"

    def get_cli_command(self, inline_prompt: Optional[str] = None) -> str:
        """Get the CLI command for Claude Code CLI."""
        if inline_prompt:
            # Escape quotes in prompt for shell
            escaped_prompt = inline_prompt.replace('"', '\\"').replace('\n', '\\n')
            if len(escaped_prompt) > 100:
                escaped_prompt = escaped_prompt[:100] + "..."
            return f'claude --permission-mode bypassPermissions -p "{escaped_prompt}"'
        return "claude --permission-mode bypassPermissions"
        
    def run_prompt(self, inline_prompt: Optional[str] = None, prompt_name: Optional[str] = None,
                   params: Optional[Dict[str, Any]] = None, context: Optional[str] = None,
                   session_id: Optional[str] = None) -> Optional[Tuple[str, Optional[str]]]:
        """Run a prompt using Claude Code CLI with template parameter replacement."""
        prompt_content = self._prepare_prompt_content(inline_prompt, prompt_name, params, context)
        if prompt_content is None:
            return None

        try:
            # Use Claude CLI to run the prompt
            result, session_id = self._execute_claude_prompt(prompt_content, prompt_name or inline_prompt, session_id)
            if result:
                return result, session_id
            else:
                self.logger.error(f"No response received from Claude")
                return None

        except Exception as e:
            self.logger.error(f"Error running prompt: {e}")
            return None
            
    def _execute_claude_prompt(self, prompt_content: str, prompt_name: str, session_id: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """Execute the prompt using Claude Code CLI."""
        try:
            # Check if Claude CLI is available
            if self.claude_path is None:
                self.logger.warning("Claude CLI not found, using fallback")
                return self._fallback_execution(prompt_content, prompt_name), None

            # Write prompt to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt_content)
                prompt_file = f.name

            try:
                # Build command
                permission_mode = self.config.get('permission_mode', 'bypassPermissions')
                cmd = [
                    self.claude_path,
                    "--permission-mode", permission_mode,
                ]

                # Add session ID if provided
                if session_id:
                    cmd.extend(["--resume", session_id])

                # Add prompt as argument (claude CLI reads from stdin if no file specified)
                self.logger.info(f"🚀 Executing Claude CLI: {' '.join(cmd[:2])}")

                # Execute Claude CLI
                result = subprocess.run(
                    cmd,
                    input=prompt_content,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                    cwd=os.getcwd()
                )

                # Clean up temp file
                try:
                    os.unlink(prompt_file)
                except:
                    pass

                if result.returncode != 0:
                    self.logger.error(f"Claude CLI failed with code {result.returncode}")
                    self.logger.error(f"STDERR: {result.stderr}")
                    return self._fallback_execution(prompt_content, prompt_name), None

                # Log output
                if result.stdout:
                    self.logger.info("✅ Claude response received")

                # Return the response (no session_id support in CLI mode)
                return result.stdout, None

            except subprocess.TimeoutExpired:
                self.logger.error("Claude CLI execution timed out after 10 minutes")
                return self._fallback_execution(prompt_content, prompt_name), None
            except Exception as e:
                self.logger.error(f"Claude CLI execution failed: {e}")
                return self._fallback_execution(prompt_content, prompt_name), None

        except Exception as e:
            self.logger.error(f"Claude execution error: {e}")
            return None, None
            
    def _fallback_execution(self, prompt_content: str, prompt_name: str) -> str:
        """Fallback execution when Claude CLI is not available."""
        self.logger.info("Using fallback execution - returning processed prompt template")

        # Simple fallback: return a basic response based on the prompt
        fallback_response = f"""# Generated Response for {prompt_name}

Based on the provided prompt and parameters, here is the generated content:

{prompt_content}

---
*Note: This is a fallback response. For AI-generated content, ensure Claude Code CLI is available at ~/.claude/local/claude*
"""
        return fallback_response
