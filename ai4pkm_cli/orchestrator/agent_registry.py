"""
Agent registry for orchestrator.

Loads and manages agent definitions from _Settings_/Agents/.
"""
import logging
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
import fnmatch

from .models import AgentDefinition
from ..markdown_utils import read_frontmatter, extract_body

logger = logging.getLogger(__name__)


# JSON Schema for agent definition validation
AGENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["title", "abbreviation", "category", "trigger_pattern", "trigger_event"],
    "properties": {
        "title": {"type": "string"},
        "abbreviation": {"type": "string", "pattern": "^[A-Z]{3}$"},
        "category": {"enum": ["ingestion", "publish", "research"]},
        "trigger_pattern": {"type": "string"},
        "trigger_event": {"enum": ["created", "modified", "deleted", "scheduled", "manual"]},
        "executor": {"enum": ["claude_code", "gemini_cli", "custom_script"]},
        "max_parallel": {"type": "integer", "minimum": 1},
        "timeout_minutes": {"type": "integer", "minimum": 1}
    }
}


class AgentRegistry:
    """
    Registry of all available agents.
    
    Loads agent definitions from _Settings_/Agents/ directory.
    """

    def __init__(self, agents_dir: Path, vault_path: Path):
        """
        Initialize agent registry.

        Args:
            agents_dir: Directory containing agent definition files
            vault_path: Path to vault root
        """
        self.agents_dir = Path(agents_dir)
        self.vault_path = Path(vault_path)
        self.agents: Dict[str, AgentDefinition] = {}
        
        self.load_all_agents()

    def load_all_agents(self):
        """Load all agent definitions from directory."""
        if not self.agents_dir.exists():
            logger.warning(f"Agent directory does not exist: {self.agents_dir}")
            return

        # Get all .md files but exclude README files
        agent_files = [f for f in self.agents_dir.glob("*.md") if not f.stem.upper().startswith("README")]
        logger.info(f"Loading agents from {self.agents_dir}")

        for agent_file in agent_files:
            try:
                agent = self._load_agent(agent_file)
                if agent:
                    self.agents[agent.abbreviation] = agent
                    logger.info(f"Loaded agent: {agent.abbreviation} ({agent.name})")
            except Exception as e:
                logger.error(f"Error loading agent from {agent_file}: {e}")

        logger.info(f"Total agents loaded: {len(self.agents)}")

    def _load_agent(self, file_path: Path) -> Optional[AgentDefinition]:
        """
        Load a single agent definition from file.

        Args:
            file_path: Path to agent definition file

        Returns:
            AgentDefinition instance or None if invalid
        """
        frontmatter = read_frontmatter(file_path)
        if not frontmatter:
            logger.warning(f"No frontmatter found in {file_path}")
            return None

        # Validate required fields (basic check)
        required = ['title', 'abbreviation', 'category', 'input_path', 'input_type']
        for field in required:
            if field not in frontmatter:
                logger.error(f"Missing required field '{field}' in {file_path}")
                return None

        # Extract prompt body
        prompt_body = extract_body(file_path.read_text(encoding='utf-8'))

        # Convert frontmatter to AgentDefinition
        # Handle list fields
        input_path = frontmatter.get('input_path', [])
        if isinstance(input_path, str):
            input_path = [input_path]

        # Derive trigger_pattern and trigger_event if not specified
        trigger_pattern = frontmatter.get('trigger_pattern')
        trigger_event = frontmatter.get('trigger_event')

        if not trigger_pattern or not trigger_event:
            trigger_pattern, trigger_event = self._derive_trigger_from_input(
                input_path,
                frontmatter.get('input_type', 'new_file'),
                frontmatter.get('input_pattern')
            )

        skills = frontmatter.get('skills', [])
        if isinstance(skills, str):
            skills = [skills]

        mcp_servers = frontmatter.get('mcp_servers', [])
        if isinstance(mcp_servers, str):
            mcp_servers = [mcp_servers]

        trigger_wait_for = frontmatter.get('trigger_wait_for', [])
        if isinstance(trigger_wait_for, str):
            trigger_wait_for = [trigger_wait_for]

        agent = AgentDefinition(
            name=frontmatter['title'],
            abbreviation=frontmatter['abbreviation'],
            category=frontmatter['category'],
            trigger_pattern=trigger_pattern,
            trigger_event=trigger_event,
            trigger_exclude_pattern=frontmatter.get('trigger_exclude_pattern'),
            trigger_content_pattern=frontmatter.get('trigger_content_pattern'),
            trigger_schedule=frontmatter.get('trigger_schedule'),
            trigger_wait_for=trigger_wait_for,
            input_path=input_path,
            input_type=frontmatter.get('input_type', 'new_file'),
            output_path=frontmatter.get('output_path', ''),
            output_type=frontmatter.get('output_type', 'new_file'),
            output_naming=frontmatter.get('output_naming', '{title} - {agent}.md'),
            prompt_body=prompt_body,
            skills=skills,
            mcp_servers=mcp_servers,
            executor=frontmatter.get('executor', 'claude_code'),
            max_parallel=int(frontmatter.get('max_parallel', 1)),
            timeout_minutes=int(frontmatter.get('timeout_minutes', 30)),
            log_prefix=frontmatter.get('log_prefix', frontmatter['abbreviation']),
            log_pattern=frontmatter.get('log_pattern', '{timestamp}-{agent}.log'),
            post_process_action=frontmatter.get('post_process_action'),
            task_create=frontmatter.get('task_create', True),
            task_priority=frontmatter.get('task_priority', 'medium'),
            task_archived=frontmatter.get('task_archived', False),
            file_path=file_path,
            version=frontmatter.get('version', '1.0')
        )

        return agent

    def _derive_trigger_from_input(self, input_paths: List[str], input_type: str, input_pattern: Optional[str] = None) -> tuple:
        """
        Derive trigger_pattern and trigger_event from input_path and input_type.

        Args:
            input_paths: List of input paths (relative to vault root)
            input_type: Type of input (new_file, updated_file, daily_file, manual)
            input_pattern: Optional custom file pattern (e.g., "*.{jpg,png}")

        Returns:
            Tuple of (trigger_pattern, trigger_event)
        """
        # Map input_type to trigger_event
        event_mapping = {
            'new_file': 'created',
            'updated_file': 'modified',
            'daily_file': 'scheduled',
            'manual': 'manual'
        }
        trigger_event = event_mapping.get(input_type, 'created')

        # Build trigger_pattern from first input_path
        if not input_paths:
            trigger_pattern = "**/*.md"  # Default pattern
        else:
            first_path = input_paths[0].rstrip('/')  # Remove trailing slash

            # Use custom input_pattern if specified
            if input_pattern:
                # Extract file extensions if provided
                trigger_pattern = f"{first_path}/{input_pattern}"
            else:
                # Default to *.md for text files
                trigger_pattern = f"{first_path}/*.md"

        logger.debug(f"Derived trigger: pattern='{trigger_pattern}', event='{trigger_event}' from input_paths={input_paths}, input_type={input_type}")

        return trigger_pattern, trigger_event

    def find_matching_agents(self, event_data: Dict) -> List[AgentDefinition]:
        """
        Find agents whose triggers match the event.

        Args:
            event_data: Event dictionary with path, event_type, etc.

        Returns:
            List of matching AgentDefinition instances
        """
        matching = []
        event_path = event_data.get('path', '')
        event_type = event_data.get('event_type', '')
        
        for agent in self.agents.values():
            if self._matches_trigger(agent, event_path, event_type):
                matching.append(agent)

        return matching

    def _matches_trigger(self, agent: AgentDefinition, event_path: str, event_type: str) -> bool:
        """
        Check if event matches agent's trigger conditions.

        Args:
            agent: AgentDefinition to check
            event_path: File path from event
            event_type: Event type (created, modified, deleted)

        Returns:
            True if event matches agent's trigger
        """
        # Check event type matches
        if agent.trigger_event != event_type:
            return False

        # Check pattern matches
        if not fnmatch.fnmatch(event_path, agent.trigger_pattern):
            return False

        # Check exclusion pattern if specified
        if agent.trigger_exclude_pattern:
            if fnmatch.fnmatch(event_path, agent.trigger_exclude_pattern):
                return False

        # Check content pattern if specified
        if agent.trigger_content_pattern:
            if not self._check_content_pattern(event_path, agent.trigger_content_pattern):
                return False

            # Check for existing task to avoid duplication
            if self._has_existing_task(event_path):
                logger.debug(f"Skipping {event_path} - task already exists")
                return False

        return True

    def _check_content_pattern(self, event_path: str, pattern: str) -> bool:
        """
        Check if file content matches the pattern.

        Args:
            event_path: Relative file path from event
            pattern: Regex pattern to match in file content

        Returns:
            True if pattern found in file content
        """
        try:
            # Convert to absolute path
            file_path = self.vault_path / event_path
            if not file_path.exists():
                return False

            content = file_path.read_text(encoding='utf-8')

            # Apply pattern (case-insensitive)
            return bool(re.search(pattern, content, re.IGNORECASE | re.MULTILINE))

        except Exception as e:
            logger.error(f"Error reading file {event_path}: {e}")
            return False

    def _has_existing_task(self, event_path: str) -> bool:
        """
        Check if a task already exists for this file in _Tasks_/ directory.

        Args:
            event_path: Relative file path from event

        Returns:
            True if task file already exists
        """
        try:
            tasks_dir = self.vault_path / "_Tasks_"
            if not tasks_dir.exists():
                return False

            # Extract filename without extension
            source_filename = Path(event_path).stem

            # Search for task files containing the source filename
            # Format: YYYY-MM-DD {agent} - {source_filename}.md
            for task_file in tasks_dir.glob("*.md"):
                if source_filename in task_file.stem:
                    logger.debug(f"Found existing task: {task_file.name}")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking for existing task: {e}")
            return False

    def export_config_snapshot(self, output_path: Path):
        """
        Export current agent configurations to JSON for debugging.

        Args:
            output_path: Path to output JSON file
        """
        config = {}
        
        for abbr, agent in self.agents.items():
            config[abbr] = {
                'name': agent.name,
                'category': agent.category,
                'trigger_pattern': agent.trigger_pattern,
                'trigger_event': agent.trigger_event,
                'executor': agent.executor,
                'skills': agent.skills,
                'mcp_servers': agent.mcp_servers,
                'file_path': str(agent.file_path) if agent.file_path else None
            }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(config, indent=2), encoding='utf-8')
        logger.info(f"Agent configuration snapshot saved to {output_path}")
