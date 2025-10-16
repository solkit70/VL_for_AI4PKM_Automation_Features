"""KTP (Knowledge Task Processor) Runner - Executes and monitors knowledge tasks."""

import os
import sys
import json
import re
import subprocess
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
        self.routing = self.config.get_ktp_routing()
        self.timeout_minutes = self.config.get_ktp_timeout()
        self.max_retries = self.config.get_ktp_max_retries()
        
    def run_tasks(self, task_file: str = None, priority: str = None, status: str = None):
        """Run tasks based on filters.
        
        Args:
            task_file: Specific task filename to process (optional)
            priority: Filter by priority (P0, P1, P2, P3)
            status: Filter by status (TBD, IN_PROGRESS, UNDER_REVIEW)
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
        
        # Process each task
        for idx, task in enumerate(tasks, 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Processing task {idx}/{len(tasks)}: {task['file']}")
            self.logger.info(f"{'='*60}")
            
            try:
                self._process_task(task['file'])
            except Exception as e:
                self.logger.error(f"Error processing task {task['file']}: {e}")
                continue
                
        self.logger.info("\n✅ KTP processing complete")
    
    def _get_task_queue(self, priority: str = None, status: str = None) -> List[Dict[str, Any]]:
        """Get task queue from Task Status Manager.
        
        Args:
            priority: Filter by priority
            status: Filter by status
            
        Returns:
            List of task dictionaries
        """
        # Run task status manager script
        script_path = os.path.join(
            self.workspace_path, 
            "ai4pkm_cli", 
            "scripts", 
            "task_status.py"
        )
        
        if not os.path.exists(script_path):
            self.logger.error(f"Task Status Manager script not found: {script_path}")
            self.logger.error(f"Workspace path: {self.workspace_path}")
            self.logger.error(f"Current working directory: {os.getcwd()}")
            return []
            
        # Build command
        cmd = [sys.executable, script_path]
        
        if priority:
            cmd.extend(['--priority', priority])
            
        if status:
            cmd.extend(['--status', status])
        elif not status:
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
        elif current_status == 'UNDER_REVIEW':
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
        agent_name = self.routing.get(task_type, self.routing.get('default', 'claude_code'))
        
        self.logger.info(f"Task type: {task_type}")
        self.logger.info(f"Routing to agent: {agent_name}")
        
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
        self.logger.info("\n⚙️  Phase 2: Execution & Monitoring (IN_PROGRESS → UNDER_REVIEW)")
        
        # Get agent
        worker = task_data.get('worker', self.routing.get('default', 'claude_code'))
        
        try:
            agent = AgentFactory.create_agent_by_name(worker, self.logger, self.config)
        except ValueError as e:
            self.logger.error(f"Failed to create agent: {e}")
            self._update_task_status(task_file, 'FAILED', worker=worker)
            return
            
        # Build prompt for agent
        task_path = os.path.join(self.tasks_dir, task_file)
        prompt = f"Process the knowledge task defined in the file: {task_path}\n\n"
        prompt += "Follow the instructions in the task file and update the task file with:\n"
        prompt += "- Process Log entries documenting your work\n"
        prompt += "- Output property with wiki links to created files\n"
        prompt += "- Status updated to UNDER_REVIEW when complete\n"
        
        self.logger.info(f"Executing task with agent: {worker}")
        
        try:
            # Execute the task
            result = agent.run_prompt(inline_prompt=prompt)
            
            if result:
                response_text, session_id = result
                self.logger.info("✅ Task execution completed")
                
                # Check if status was updated to UNDER_REVIEW
                updated_data = self._read_task_file(task_path)
                if updated_data.get('status') == 'UNDER_REVIEW':
                    self.logger.info("Status updated to UNDER_REVIEW by agent")
                    # Proceed to Phase 3
                    self._phase3_evaluate_task(task_file, updated_data)
                else:
                    # Agent didn't update status, do it manually
                    self.logger.warning("Agent didn't update status, updating manually")
                    self._update_task_status(task_file, 'UNDER_REVIEW', worker=worker)
            else:
                self.logger.warning("Task execution completed with no response")
                self._update_task_status(task_file, 'UNDER_REVIEW', worker=worker)
                
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
        """Phase 3: Evaluate task results and complete or request refinements.
        
        Args:
            task_file: Task filename
            task_data: Task metadata dictionary
        """
        self.logger.info("\n✓ Phase 3: Results Evaluation (UNDER_REVIEW → COMPLETE)")
        
        # Read current task state
        task_path = os.path.join(self.tasks_dir, task_file)
        current_data = self._read_task_file(task_path)
        
        # Validate outputs
        output_links = current_data.get('output', '')
        
        if not output_links:
            self.logger.warning("⚠️  No output property found in task")
            self.logger.info("Task may need manual review")
            # Keep status as UNDER_REVIEW for manual review
            return
            
        # Parse and validate wiki links
        valid_outputs = self._validate_output_links(output_links)
        
        if valid_outputs:
            self.logger.info(f"✅ Validated {len(valid_outputs)} output file(s)")
            
            # Check for process log
            task_content = self._read_file_content(task_path)
            if '## Process Log' not in task_content:
                self.logger.warning("⚠️  No Process Log section found")
            
            # Mark as complete
            self._update_task_status(task_file, 'COMPLETED', worker=current_data.get('worker', ''))
            self.logger.info("🎉 Task completed successfully")
        else:
            self.logger.warning("⚠️  Output validation failed")
            self.logger.info("Task may need refinement or manual review")
            # Keep status as UNDER_REVIEW for manual intervention
    
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
        script_path = os.path.join(
            self.workspace_path, 
            "ai4pkm_cli", 
            "scripts", 
            "task_status.py"
        )
        
        cmd = [
            sys.executable, 
            script_path,
            '--update', task_file,
            '--status-new', new_status
        ]
        
        if worker:
            cmd.extend(['--worker', worker])
            
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"Updated task status: {new_status}")
            else:
                self.logger.error(f"Failed to update task status: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"Error updating task status: {e}")
    
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
    parser.add_argument('--status', type=str, choices=['TBD', 'IN_PROGRESS', 'UNDER_REVIEW'], help='Filter by status')
    
    args = parser.parse_args()
    
    runner.run_tasks(task_file=args.task, priority=args.priority, status=args.status)

