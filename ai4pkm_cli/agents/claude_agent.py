"""Claude Code SDK agent implementation."""

import os
import asyncio
from typing import Optional, Tuple, Dict, Any
from .base_agent import BaseAgent

try:
    from claude_code_sdk import query, ClaudeCodeOptions
    ClaudeCodeClient = query
except ImportError:
    ClaudeCodeClient = None


class ClaudeAgent(BaseAgent):
    """Claude Code SDK agent implementation."""
    
    def __init__(self, logger, config: Dict[str, Any]):
        """Initialize Claude agent."""
        super().__init__(logger, config)
        self.claude_client = None
        self._initialize_claude_client()
        
    def _initialize_claude_client(self):
        """Initialize the Claude Code SDK client."""
        if ClaudeCodeClient is None:
            self.logger.warning("Claude Code SDK not available. Install with: pip install claude-code-sdk")
            return
            
        try:
            # The query function is available, store it as the client
            self.claude_client = ClaudeCodeClient
            # Claude SDK is ready
        except Exception as e:
            self.logger.error(f"Failed to initialize Claude Code SDK client: {e}")
            self.claude_client = None
            
    def is_available(self) -> bool:
        """Check if Claude Code SDK is available."""
        return self.claude_client is not None
        
    def get_agent_name(self) -> str:
        """Get the display name of this agent."""
        return "Claude Code"

    def get_cli_command(self, inline_prompt: Optional[str] = None) -> str:
        """Get the CLI command for Claude Code SDK."""
        if inline_prompt:
            # Escape quotes in prompt for shell
            escaped_prompt = inline_prompt.replace('"', '\\"').replace('\n', '\\n')
            if len(escaped_prompt) > 100:
                escaped_prompt = escaped_prompt[:100] + "..."
            return f'claude-code -p "{escaped_prompt}"'
        return "claude-code"
        
    def run_prompt(self, inline_prompt: Optional[str] = None, prompt_name: Optional[str] = None, 
                   params: Optional[Dict[str, Any]] = None, context: Optional[str] = None, 
                   session_id: Optional[str] = None) -> Optional[Tuple[str, Optional[str]]]:
        """Run a prompt using Claude Code SDK with template parameter replacement."""
        prompt_content = self._prepare_prompt_content(inline_prompt, prompt_name, params, context)
        if prompt_content is None:
            return None
            
        try:
            # Use claude-code-sdk to run the prompt
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
        """Execute the prompt using Claude Code SDK."""
        try:
            # Check if Claude client is available
            if self.claude_client is None:
                self.logger.warning("Claude Code SDK not available, using fallback")
                return self._fallback_execution(prompt_content, prompt_name), None
            
            permission_mode = self.config.get('permission_mode', 'bypassPermissions')
            options = ClaudeCodeOptions(
                cwd=os.getcwd(),
                permission_mode=permission_mode,
                resume=session_id,
            )

            # Send the prompt to Claude using async query function
            try:
                async def run_query():
                    response_parts = []
                    final_session_id = None
                    message_count = 0
                    
                    async for message in self.claude_client(prompt=prompt_content, options=options):
                        message_count += 1
                        
                        # Extract only the text content from the message
                        extracted_text = ""
                        if hasattr(message, 'content') and message.content:
                            if isinstance(message.content, list):
                                for block in message.content:
                                    if hasattr(block, 'text'):
                                        extracted_text += block.text
                            elif hasattr(message.content, 'text'):
                                extracted_text = message.content.text
                            elif isinstance(message.content, str):
                                extracted_text = message.content
                        elif hasattr(message, 'data') and isinstance(message.data, dict):
                            final_session_id = message.data.get('session_id')
                        
                        # Append extracted text to response and log it
                        if extracted_text:
                            response_parts.append(extracted_text)
                            self.logger.debug(f"Response chunk: {len(extracted_text)} chars")
                    
                    return '\n'.join(response_parts), final_session_id

                # Run the async query
                processed_content, final_session_id = asyncio.run(run_query())
                return processed_content, final_session_id
                
            except AttributeError as e:
                self.logger.error(f"Claude SDK API mismatch: {e}")
                return self._fallback_execution(prompt_content, prompt_name), None
            except Exception as e:
                self.logger.error(f"Claude API call failed: {e}")
                return self._fallback_execution(prompt_content, prompt_name), None
            
        except Exception as e:
            self.logger.error(f"Claude execution error: {e}")
            return None, None
            
    def _fallback_execution(self, prompt_content: str, prompt_name: str) -> str:
        """Fallback execution when Claude SDK is not available."""
        self.logger.info("Using fallback execution - returning processed prompt template")
        
        # Simple fallback: return a basic response based on the prompt
        fallback_response = f"""# Generated Response for {prompt_name}

Based on the provided prompt and parameters, here is the generated content:

{prompt_content}

---
*Note: This is a fallback response. For AI-generated content, ensure Claude Code SDK is properly configured.*
"""
        return fallback_response
