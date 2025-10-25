"""KTP (Knowledge Task Processor) Runner - Executes and monitors knowledge tasks."""

import os
import sys
import json
import re
import subprocess
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from ..agent_factory import AgentFactory
from ..config import Config


class KTPRunner:
    """Main KTP runner implementing 3-phase task processing workflow."""
    
    def __init__(self, logger, config: Config = None):
        """Initialize KTP Runner.

        Args:
            logger: Logger instance
            config: Configuration instance (will create default if None)
        """
        self.logger = logger
        self.config = config or Config()
        self.workspace_path = os.getcwd()
        self.tasks_dir = os.path.join(self.workspace_path, "AI", "Tasks")
        self.processing_agent = self.config.get_ktp_routing()  # Maps task type to agent for Phase 1 & 2
        self.timeout_minutes = self.config.get_ktp_timeout()
        self.max_retries = self.config.get_ktp_max_retries()

    def _read_execution_prompt(self, task_path: str) -> str:
        """Read execution prompt from system prompt file.

        Args:
            task_path: Path to the task file

        Returns:
            Formatted execution prompt
        """
        # Try to read from system prompt file in ai4pkm_cli/prompts
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_file = os.path.join(module_dir, "prompts", "task_execution.md")

        try:
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract the prompt template between ``` markers
                match = re.search(r'```\s*\n(.*?)\n```', content, re.DOTALL)
                if match:
                    template = match.group(1).strip()
                    # Replace placeholder
                    return template.replace('{task_path}', task_path)
        except Exception as e:
            self.logger.warning(f"Could not read execution prompt from file: {e}")

        # Fallback to hardcoded prompt
        prompt = f"Process the knowledge task defined in the file: {task_path}\n\n"
        prompt += "Follow the instructions in the task file and update the task file with:\n"
        prompt += "- Process Log entries documenting your work\n"
        prompt += "- Output property with wiki links to created files\n"
        prompt += "- Status updated to PROCESSED when complete\n"
        return prompt

    def _read_evaluation_prompt(self, task_path: str, task_type: str, priority: str,
                                instructions: str, output_section: str) -> str:
        """Read evaluation prompt from system prompt file.

        Args:
            task_path: Path to the task file
            task_type: Task type
            priority: Task priority
            instructions: Task instructions
            output_section: Output files section

        Returns:
            Formatted evaluation prompt
        """
        # Try to read from system prompt file in ai4pkm_cli/prompts
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_file = os.path.join(module_dir, "prompts", "task_evaluation.md")

        try:
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract the prompt template between ``` markers
                match = re.search(r'```\s*\n(.*?)\n```', content, re.DOTALL)
                if match:
                    template = match.group(1).strip()
                    # Replace placeholders
                    return (template
                           .replace('{task_path}', task_path)
                           .replace('{task_type}', task_type)
                           .replace('{priority}', priority)
                           .replace('{instructions}', instructions)
                           .replace('{output_section}', output_section))
        except Exception as e:
            self.logger.warning(f"Could not read evaluation prompt from file: {e}")

        # Fallback to hardcoded prompt
        prompt = f"""Review this task and its output to determine if it should be marked COMPLETED or FAILED.

Task File: {task_path}
Task Type: {task_type}
Priority: {priority}

## Original Instructions
{instructions}

## Output Files
{output_section}

## Evaluation Criteria
1. Are output files specified in the 'output' property?
2. Do the output files exist and are they accessible?
3. Does the output address the task instructions?
4. Is the output complete and well-structured?
5. Are there any obvious errors or omissions?

Respond with:
- APPROVED if the task is complete and meets all requirements
- NEEDS_REWORK if the task has issues (missing outputs, incorrect content, etc.)

Format your response as:
DECISION: [APPROVED or NEEDS_REWORK]
REASON: [brief explanation]
FEEDBACK: [specific improvements needed if NEEDS_REWORK]
"""
        return prompt
        
    def evaluate_task(self, task_file: str):
        """Evaluate a single PROCESSED task (Phase 3 only).

        Args:
            task_file: Task filename to evaluate
        """
        self.logger.info(f"🔍 Evaluating task: {task_file}")

        # Read task data
        task_path = os.path.join(self.tasks_dir, task_file)
        if not os.path.exists(task_path):
            self.logger.error(f"Task file not found: {task_file}")
            return

        task_data = self._read_task_file(task_path)

        # Can evaluate either PROCESSED (not yet evaluated) or UNDER_REVIEW (retry)
        status = task_data.get('status', '')
        if status not in ['PROCESSED', 'UNDER_REVIEW']:
            self.logger.warning(f"Task status is {status}, not eligible for evaluation (expected PROCESSED or UNDER_REVIEW)")
            return

        # Run Phase 3 evaluation
        self._phase3_evaluate_task(task_file, task_data)
    
    def run_tasks(self, task_file: str = None, priority: str = None, status: str = None):
        """Run tasks based on filters.

        Args:
            task_file: Specific task filename to process (optional)
            priority: Filter by priority (P0, P1, P2, P3)
            status: Filter by status (TBD, IN_PROGRESS, PROCESSED, UNDER_REVIEW)
        """
        self.logger.info("🚀 Starting KTP (Knowledge Task Processor)")

        # If specific task file provided, process only that
        if task_file:
            self._process_single_task(task_file)
            return

        # Otherwise, get task queue from Task Status Manager
        tasks = self._get_task_queue(priority, status)

        if not tasks:
            self.logger.info("No tasks found matching criteria")
            return

        self.logger.info(f"Found {len(tasks)} task(s) to process")

        # Process each task based on requested status
        threads = []
        for idx, task in enumerate(tasks, 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Processing task {idx}/{len(tasks)}: {task['file']}")
            self.logger.info(f"{'='*60}")

            try:
                # If status filter is PROCESSED or UNDER_REVIEW, spawn thread for evaluation
                if status in ['PROCESSED', 'UNDER_REVIEW']:
                    thread = self._spawn_evaluation_thread(task['file'])
                    threads.append(thread)
                else:
                    # Normal processing (handles TBD and IN_PROGRESS)
                    # Spawn thread for processing
                    thread = self._spawn_processing_thread(task['file'])
                    threads.append(thread)
            except Exception as e:
                self.logger.error(f"Error processing task {task['file']}: {e}")
                continue

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        self.logger.info("\n✅ KTP processing complete")
    
    def _get_task_queue(self, priority: str = None, status: str = None) -> List[Dict[str, Any]]:
        """Get task queue from Task Status Manager.
        
        Args:
            priority: Filter by priority
            status: Filter by status
            
        Returns:
            List of task dictionaries
        """
        # Run task status manager script (relative to this module's location)
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(module_dir, "scripts", "task_status.py")
        
        if not os.path.exists(script_path):
            self.logger.error(f"Task Status Manager script not found: {script_path}")
            self.logger.error(f"Module directory: {module_dir}")
            self.logger.error(f"Current working directory: {os.getcwd()}")
            return []
            
        # Build command
        cmd = [sys.executable, script_path]
        
        if priority:
            cmd.extend(['--priority', priority])

        if status:
            cmd.extend(['--status', status])
        else:
            # Default to TBD if no status specified
            cmd.extend(['--status', 'TBD'])
            
        try:
            # Run the script and capture output
            result = subprocess.run(
                cmd,
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.error(f"Task Status Manager failed with code {result.returncode}")
                self.logger.error(f"STDERR: {result.stderr}")
                self.logger.error(f"STDOUT: {result.stdout}")
                self.logger.error(f"Command: {' '.join(cmd)}")
                return []
                
            # Parse JSON output
            data = json.loads(result.stdout)
            return data.get('execution_queue', [])
            
        except subprocess.TimeoutExpired:
            self.logger.error("Task Status Manager timed out")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse task queue JSON: {e}")
            self.logger.error(f"Output was: {result.stdout[:200]}")
            return []
        except FileNotFoundError as e:
            self.logger.error(f"File not found error: {e}")
            self.logger.error(f"Python executable: {sys.executable}")
            self.logger.error(f"Script path: {script_path}")
            return []
        except Exception as e:
            self.logger.error(f"Error running Task Status Manager: {e}")
            self.logger.error(f"Error type: {type(e).__name__}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def _spawn_evaluation_thread(self, task_file: str) -> threading.Thread:
        """Spawn a thread for task evaluation.

        Args:
            task_file: Task filename to evaluate

        Returns:
            Thread object
        """
        # Get evaluation agent name from config
        agent_name = self.config.get_evaluation_agent()
        agent_short = agent_name.replace('_cli', '').replace('_code', '')  # claude, gemini, codex

        thread = threading.Thread(
            target=self.evaluate_task,
            args=(task_file,),
            daemon=True,
            name=f"KTP-eval-{agent_short}-{task_file}"
        )
        thread.start()
        return thread

    def _spawn_processing_thread(self, task_file: str) -> threading.Thread:
        """Spawn a thread for task processing.

        Args:
            task_file: Task filename to process

        Returns:
            Thread object
        """
        # Determine agent from task type
        task_path = os.path.join(self.tasks_dir, task_file)
        try:
            task_data = self._read_task_file(task_path)
            task_type = task_data.get('task_type', 'Unknown')
            agent_name = self.processing_agent.get(task_type, self.processing_agent.get('default', 'claude_code'))
            agent_short = agent_name.replace('_cli', '').replace('_code', '')  # claude, gemini, codex
        except Exception as e:
            self.logger.warning(f"Could not determine agent for {task_file}, using default: {e}")
            agent_short = "unknown"

        thread = threading.Thread(
            target=self._process_task,
            args=(task_file,),
            daemon=True,
            name=f"KTP-exec-{agent_short}-{task_file}"
        )
        thread.start()
        return thread

    def _process_single_task(self, task_file: str):
        """Process a single task file.
        
        Args:
            task_file: Task filename
        """
        self.logger.info(f"Processing task: {task_file}")
        self._process_task(task_file)
    
    def _process_task(self, task_file: str):
        """Process a task through the 3-phase workflow.
        
        Args:
            task_file: Task filename
        """
        task_path = os.path.join(self.tasks_dir, task_file)
        
        if not os.path.exists(task_path):
            self.logger.error(f"Task file not found: {task_file}")
            return
            
        # Read task metadata
        task_data = self._read_task_file(task_path)
        current_status = task_data.get('status', 'TBD')
        
        self.logger.info(f"Current status: {current_status}")
        
        # Route based on current status
        if current_status == 'TBD':
            self._phase1_route_task(task_file, task_data)
        elif current_status == 'IN_PROGRESS':
            self._phase2_execute_task(task_file, task_data)
        elif current_status == 'PROCESSED':
            self._phase3_evaluate_task(task_file, task_data)
        elif current_status == 'UNDER_REVIEW':
            # Retry evaluation if it was interrupted
            self._phase3_evaluate_task(task_file, task_data)
        elif current_status == 'COMPLETED':
            self.logger.info("Task already completed, skipping")
        else:
            self.logger.warning(f"Unknown status: {current_status}")
    
    def _phase1_route_task(self, task_file: str, task_data: Dict[str, Any]):
        """Phase 1: Route task to appropriate agent and start execution.
        
        Args:
            task_file: Task filename
            task_data: Task metadata dictionary
        """
        self.logger.info("\n📍 Phase 1: Task Routing (TBD → IN_PROGRESS)")
        
        # Determine agent based on task type
        task_type = task_data.get('task_type', 'Unknown')
        agent_name = self.processing_agent.get(task_type, self.processing_agent.get('default', 'claude_code'))
        
        self.logger.debug(f"Task type: {task_type}")
        self.logger.debug(f"Routing to agent: {agent_name}")
        
        # Update task status to IN_PROGRESS
        self._update_task_status(task_file, 'IN_PROGRESS', worker=agent_name)
        
        # Proceed to Phase 2
        task_data['status'] = 'IN_PROGRESS'
        task_data['worker'] = agent_name
        self._phase2_execute_task(task_file, task_data)
    
    def _phase2_execute_task(self, task_file: str, task_data: Dict[str, Any]):
        """Phase 2: Execute task with selected agent.

        Args:
            task_file: Task filename
            task_data: Task metadata dictionary
        """
        self.logger.info("\n⚙️  Phase 2: Execution & Monitoring (IN_PROGRESS → PROCESSED)")

        # Get agent
        worker = task_data.get('worker', self.processing_agent.get('default', 'claude_code'))

        try:
            agent = AgentFactory.create_agent_by_name(worker, self.logger, self.config)
        except ValueError as e:
            self.logger.error(f"Failed to create agent: {e}")
            self._update_task_status(task_file, 'FAILED', worker=worker)
            return

        # Build prompt for agent using template from file
        task_path = os.path.join(self.tasks_dir, task_file)
        prompt = self._read_execution_prompt(task_path)

        self.logger.debug(f"Executing task with agent: {worker}")

        try:
            # Execute the task
            result = agent.run_prompt(inline_prompt=prompt)

            if result:
                response_text, session_id = result
                self.logger.info("✅ Task execution completed")

                # Check if status was updated to PROCESSED
                updated_data = self._read_task_file(task_path)
                if updated_data.get('status') == 'PROCESSED':
                    self.logger.debug("Status updated to PROCESSED by agent")
                    # Proceed to Phase 3
                    self._phase3_evaluate_task(task_file, updated_data)
                else:
                    # Agent didn't update status, do it manually
                    self.logger.warning("Agent didn't update status, updating manually")
                    self._update_task_status(task_file, 'PROCESSED', worker=worker)
            else:
                self.logger.warning("Task execution completed with no response")
                self._update_task_status(task_file, 'PROCESSED', worker=worker)
                
        except Exception as e:
            self.logger.error(f"Error executing task: {e}")
            
            # Check retry count
            retry_count = task_data.get('retry_count', 0)
            if retry_count < self.max_retries:
                self.logger.info(f"Retrying task (attempt {retry_count + 1}/{self.max_retries})")
                self._update_task_retry(task_file, retry_count + 1)
            else:
                self.logger.error(f"Max retries ({self.max_retries}) exceeded")
                self._update_task_status(task_file, 'FAILED', worker=worker)
    
    def _phase3_evaluate_task(self, task_file: str, task_data: Dict[str, Any]):
        """Phase 3: Evaluate task results and complete the work.

        This is a ONE-TIME evaluation where the evaluator MUST either:
        - Complete any unfinished work and mark COMPLETED
        - Mark NEEDS_INPUT if human intervention required

        Args:
            task_file: Task filename
            task_data: Task metadata dictionary
        """
        self.logger.info("\n✓ Phase 3: Results Evaluation (PROCESSED → COMPLETED or NEEDS_INPUT)")

        # Mark as actively under review
        task_path = os.path.join(self.tasks_dir, task_file)
        current_data = self._read_task_file(task_path)

        # Check status to determine if evaluation already done or in progress
        # Use status as the single source of truth (not 'evaluated' flag)
        status = current_data.get('status', '')
        if status in ['UNDER_REVIEW', 'COMPLETED', 'NEEDS_INPUT', 'FAILED']:
            self.logger.info(f"Task already evaluated (status: {status}), skipping")
            return

        # Only PROCESSED tasks should reach here
        if status != 'PROCESSED':
            self.logger.warning(f"Unexpected status for evaluation: {status} (expected PROCESSED)")
            return

        # Update to UNDER_REVIEW status (marks evaluation in progress)
        self._update_task_status(task_file, 'UNDER_REVIEW', worker=current_data.get('worker', ''))
        # Re-read after status update
        current_data = self._read_task_file(task_path)

        # Read task content
        task_content = self._read_file_content(task_path)

        # AI-powered evaluation (agent updates status directly)
        self.logger.info("🤖 Running AI evaluation of task output...")
        self._evaluate_with_ai(task_file, task_data, current_data, task_content)

        # Read final status after agent completes evaluation
        final_data = self._read_task_file(task_path)
        final_status = final_data.get('status', 'UNDER_REVIEW')

        if final_status == 'COMPLETED':
            self.logger.info(f"🎉 Task completed successfully")
        elif final_status == 'FAILED':
            self.logger.warning(f"❌ Task failed review")
        else:
            # Agent didn't update status - something went wrong
            self.logger.warning(f"⚠️  Agent didn't update status (still {final_status}), assuming evaluation incomplete")
            self.logger.warning("Check evaluation log for details")
    
    def _evaluate_with_ai(self, task_file: str, task_data: Dict[str, Any], current_data: Dict[str, Any], task_content: str) -> None:
        """Use AI to evaluate if task output meets requirements.

        Agent updates task status directly to COMPLETED or FAILED.

        Args:
            task_file: Task filename
            task_data: Task metadata
            current_data: Current task frontmatter data
            task_content: Full task file content
        """
        try:
            # Extract instructions from task
            instructions_match = re.search(r'## Instructions\s*\n(.*?)(?=\n##|\Z)', task_content, re.DOTALL)
            instructions = instructions_match.group(1).strip() if instructions_match else "No instructions found"

            # Get output property from task
            output_links = current_data.get('output', '')

            # Parse wiki links and build file path list
            output_file_paths = []
            if output_links:
                valid_outputs = self._validate_output_links(output_links)
                output_file_paths = valid_outputs

            # Build output files section with paths only
            if output_file_paths:
                output_section = "The following output files were created:\n"
                for output_file in output_file_paths:
                    output_section += f"- {output_file}\n"
                output_section += "\nPlease review these files to evaluate if the task was completed successfully."
            else:
                output_section = "No output files specified or found."

            # Get task file path for agent to access
            task_path = os.path.join(self.tasks_dir, task_file)

            # Build evaluation prompt using template from file
            prompt = self._read_evaluation_prompt(
                task_path=task_path,
                task_type=task_data.get('task_type', 'Unknown'),
                priority=task_data.get('priority', 'P2'),
                instructions=instructions,
                output_section=output_section
            )

            # Add critical one-time evaluation note
            prompt += f"\n\n## CRITICAL: One-Time Evaluation\n"
            prompt += f"⚠️  This is a ONE-TIME evaluation. You MUST complete the task now.\n"
            prompt += f"- If work is incomplete: COMPLETE it yourself (finish truncated sections, add missing parts)\n"
            prompt += f"- If you cannot complete: Mark NEEDS_INPUT with specific requirements\n"
            prompt += f"- DO NOT mark FAILED - that would restart execution and waste resources\n"
            prompt += f"- Your job is to COMPLETE the work, not just review it\n"

            # Get agent for evaluation (use configured evaluation agent)
            evaluation_agent_name = self.config.get_evaluation_agent()
            agent = AgentFactory.create_agent_by_name(evaluation_agent_name, self.logger, self.config)

            # Execute evaluation - agent will update task status directly
            result = agent.run_prompt(inline_prompt=prompt)

            if result and result[0]:
                self.logger.info("✅ Agent evaluation completed")
            else:
                self.logger.warning("⚠️  No response from AI evaluator")

        except Exception as e:
            self.logger.error(f"Error in AI evaluation: {e}")
    
    def _fail_task(self, task_file: str, reason: str, feedback: str = ""):
        """Mark task as FAILED with feedback.

        Args:
            task_file: Task filename
            reason: Reason for failure
            feedback: Detailed feedback explaining why it failed
        """
        self.logger.info(f"❌ Adding failure feedback to task and marking as FAILED")

        # Read task file
        task_path = os.path.join(self.tasks_dir, task_file)
        with open(task_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add review feedback section
        feedback_section = f"""

## Review Feedback ({datetime.now().strftime('%Y-%m-%d %H:%M')})

**Status**: Failed Review

**Reason**: {reason}

{f"**Feedback**:{chr(10)}{feedback}" if feedback else ""}

---
"""

        # Append feedback before any existing review sections or at the end
        if '## Review Feedback' in content:
            # Find the first review feedback section and insert before it
            content = content.replace('## Review Feedback', feedback_section + '## Review Feedback', 1)
        else:
            # Append to end of file
            content += feedback_section

        # Write back
        with open(task_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Mark status as FAILED
        self._update_task_status(task_file, 'FAILED')
        self.logger.info("💥 Task marked as FAILED")
    
    def _read_task_file(self, task_path: str) -> Dict[str, Any]:
        """Read and parse task file.
        
        Args:
            task_path: Path to task file
            
        Returns:
            Dictionary with task metadata
        """
        with open(task_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract frontmatter
        frontmatter = self._extract_frontmatter(content)
        return frontmatter
    
    def _read_file_content(self, file_path: str) -> str:
        """Read full file content.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content as string
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown content.
        
        Args:
            content: Markdown file content
            
        Returns:
            Dictionary of frontmatter properties
        """
        # Match YAML frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return {}
            
        yaml_content = match.group(1)
        frontmatter = {}
        
        # Simple YAML parser for our needs
        for line in yaml_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Match key: value pairs
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                    
                # Convert boolean strings
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value == '':
                    value = ''
                    
                frontmatter[key] = value
                
        return frontmatter
    
    def _update_task_status(self, task_file: str, new_status: str, worker: str = None):
        """Update task status using Task Status Manager.
        
        Args:
            task_file: Task filename
            new_status: New status value
            worker: Worker/agent name (optional)
        """
        # Get script path relative to this module's location
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(module_dir, "scripts", "task_status.py")
        
        cmd = [
            sys.executable, 
            script_path,
            '--update', task_file,
            '--status-new', new_status
        ]
        
        if worker:
            cmd.extend(['--worker', worker])
            
        try:
            self.logger.info(f"Updating task status to: {new_status}")
            result = subprocess.run(
                cmd,
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                if result.stdout:
                    self.logger.info(result.stdout.strip())
                self.logger.info(f"✅ Task status updated to: {new_status}")
            else:
                self.logger.error(f"Failed to update task status (exit code {result.returncode})")
                if result.stderr:
                    self.logger.error(f"STDERR: {result.stderr}")
                if result.stdout:
                    self.logger.error(f"STDOUT: {result.stdout}")
                
        except Exception as e:
            self.logger.error(f"Error updating task status: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def _update_task_retry(self, task_file: str, retry_count: int):
        """Update task retry count in frontmatter.

        Args:
            task_file: Task filename
            retry_count: New retry count
        """
        task_path = os.path.join(self.tasks_dir, task_file)

        try:
            with open(task_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update retry_count in frontmatter
            content = self._update_frontmatter_field(content, 'retry_count', str(retry_count))

            with open(task_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.logger.info(f"Updated retry count: {retry_count}")

        except Exception as e:
            self.logger.error(f"Error updating retry count: {e}")

    def _update_frontmatter_counter(self, task_file: str, field: str, value: int):
        """Update a counter field in frontmatter (for evaluation_attempts, etc).

        Args:
            task_file: Task filename
            field: Field name to update
            value: New counter value
        """
        task_path = os.path.join(self.tasks_dir, task_file)

        try:
            with open(task_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update field in frontmatter
            content = self._update_frontmatter_field(content, field, str(value))

            with open(task_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.logger.info(f"Updated {field}: {value}")

        except Exception as e:
            self.logger.error(f"Error updating {field}: {e}")
    
    def _update_frontmatter_field(self, content: str, field: str, value: str) -> str:
        """Update a field in YAML frontmatter.
        
        Args:
            content: Full markdown content
            field: Field name to update
            value: New value
            
        Returns:
            Updated content
        """
        # Match frontmatter
        match = re.match(r'^(---\s*\n)(.*?)(\n---\s*\n)', content, re.DOTALL)
        if not match:
            return content
            
        prefix = match.group(1)
        yaml_content = match.group(2)
        suffix = match.group(3)
        rest = content[match.end():]
        
        # Check if field exists
        field_pattern = rf'^{field}:\s*.*$'
        if re.search(field_pattern, yaml_content, re.MULTILINE):
            # Update existing field
            yaml_content = re.sub(field_pattern, f'{field}: "{value}"', yaml_content, flags=re.MULTILINE)
        else:
            # Add new field
            yaml_content += f'\n{field}: "{value}"'
            
        return prefix + yaml_content + suffix + rest
    
    def _validate_output_links(self, output_value: str) -> List[str]:
        """Validate output wiki links point to existing files.
        
        Args:
            output_value: Output property value (may contain wiki links)
            
        Returns:
            List of valid output file paths
        """
        valid_outputs = []
        
        # Extract wiki links [[...]]
        wiki_links = re.findall(r'\[\[([^\]]+)\]\]', output_value)
        
        if not wiki_links:
            self.logger.warning("No wiki links found in output property")
            return valid_outputs
            
        for link in wiki_links:
            # Remove section anchors
            file_ref = link.split('#')[0]
            
            # Try different paths
            possible_paths = [
                os.path.join(self.workspace_path, f"{file_ref}.md"),
                os.path.join(self.workspace_path, file_ref),
                os.path.join(self.workspace_path, "AI", f"{file_ref}.md"),
            ]
            
            found = False
            for path in possible_paths:
                if os.path.exists(path):
                    valid_outputs.append(path)
                    found = True
                    self.logger.info(f"✓ Found output: {file_ref}")
                    break
                    
            if not found:
                self.logger.warning(f"✗ Output not found: {file_ref}")
                
        return valid_outputs


# Standalone execution for testing
if __name__ == '__main__':
    from ..logger import Logger
    
    logger = Logger(console_output=True)
    config = Config()
    
    runner = KTPRunner(logger, config)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='KTP Runner')
    parser.add_argument('--task', type=str, help='Specific task file to process')
    parser.add_argument('--priority', type=str, choices=['P0', 'P1', 'P2', 'P3'], help='Filter by priority')
    parser.add_argument('--status', type=str, choices=['TBD', 'IN_PROGRESS', 'PROCESSED', 'UNDER_REVIEW'], help='Filter by status')
    
    args = parser.parse_args()
    
    runner.run_tasks(task_file=args.task, priority=args.priority, status=args.status)

