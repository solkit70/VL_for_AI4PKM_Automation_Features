"""Unit tests for agent_registry.py"""

import json
import tempfile
from pathlib import Path
import pytest

from ai4pkm_cli.orchestrator.agent_registry import AgentRegistry
from ai4pkm_cli.orchestrator.models import AgentDefinition


class TestAgentRegistry:
    """Test agent registry loading and matching."""

    @pytest.fixture
    def temp_vault(self):
        """Create temporary vault structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            agents_dir = vault_path / "_Settings_" / "Agents"
            agents_dir.mkdir(parents=True)
            yield vault_path, agents_dir

    @pytest.fixture
    def sample_agent_file(self, temp_vault):
        """Create a sample agent definition file."""
        vault_path, agents_dir = temp_vault

        agent_content = """---
title: "Test Agent"
abbreviation: "TST"
category: "ingestion"
trigger_pattern: "Ingest/Clippings/*.md"
trigger_event: "created"
trigger_exclude_pattern: "*.draft.md"
input_path:
  - "Ingest/Clippings"
output_path: "AI/Tasks"
executor: "claude_code"
max_parallel: 2
timeout_minutes: 15
---

# Test Agent Prompt

This is the prompt body for testing.
"""

        agent_file = agents_dir / "Test Agent.md"
        agent_file.write_text(agent_content, encoding='utf-8')

        return vault_path, agents_dir, agent_file

    def test_init_creates_registry(self, temp_vault):
        """Test registry initialization."""
        vault_path, agents_dir = temp_vault

        registry = AgentRegistry(agents_dir, vault_path)

        assert registry.agents_dir == agents_dir
        assert registry.vault_path == vault_path
        assert isinstance(registry.agents, dict)

    def test_load_single_agent(self, sample_agent_file):
        """Test loading a single agent definition."""
        vault_path, agents_dir, _ = sample_agent_file

        registry = AgentRegistry(agents_dir, vault_path)

        assert len(registry.agents) == 1
        assert "TST" in registry.agents

        agent = registry.agents["TST"]
        assert agent.name == "Test Agent"
        assert agent.abbreviation == "TST"
        assert agent.category == "ingestion"
        assert agent.trigger_pattern == "Ingest/Clippings/*.md"
        assert agent.trigger_event == "created"
        assert agent.trigger_exclude_pattern == "*.draft.md"
        assert agent.input_path == ["Ingest/Clippings"]
        assert agent.output_path == "AI/Tasks"
        assert agent.executor == "claude_code"
        assert agent.max_parallel == 2
        assert agent.timeout_minutes == 15
        assert "This is the prompt body for testing." in agent.prompt_body

    def test_load_multiple_agents(self, temp_vault):
        """Test loading multiple agent definitions."""
        vault_path, agents_dir = temp_vault

        # Create two agent files
        agent1 = """---
title: "Agent One"
abbreviation: "AG1"
category: "ingestion"
trigger_pattern: "*.md"
trigger_event: "created"
---
Prompt 1
"""

        agent2 = """---
title: "Agent Two"
abbreviation: "AG2"
category: "publish"
trigger_pattern: "*.txt"
trigger_event: "modified"
---
Prompt 2
"""

        (agents_dir / "agent1.md").write_text(agent1, encoding='utf-8')
        (agents_dir / "agent2.md").write_text(agent2, encoding='utf-8')

        registry = AgentRegistry(agents_dir, vault_path)

        assert len(registry.agents) == 2
        assert "AG1" in registry.agents
        assert "AG2" in registry.agents
        assert registry.agents["AG1"].name == "Agent One"
        assert registry.agents["AG2"].name == "Agent Two"

    def test_invalid_agent_missing_required_field(self, temp_vault):
        """Test that agents with missing required fields are skipped."""
        vault_path, agents_dir = temp_vault

        # Missing 'trigger_event' field
        invalid_agent = """---
title: "Invalid Agent"
abbreviation: "INV"
category: "ingestion"
trigger_pattern: "*.md"
---
Prompt
"""

        (agents_dir / "invalid.md").write_text(invalid_agent, encoding='utf-8')

        registry = AgentRegistry(agents_dir, vault_path)

        # Should be skipped
        assert len(registry.agents) == 0

    def test_find_matching_agents_basic(self, sample_agent_file):
        """Test finding agents that match an event."""
        vault_path, agents_dir, _ = sample_agent_file

        registry = AgentRegistry(agents_dir, vault_path)

        # Matching event
        event_data = {
            'path': 'Ingest/Clippings/test.md',
            'event_type': 'created'
        }

        matches = registry.find_matching_agents(event_data)

        assert len(matches) == 1
        assert matches[0].abbreviation == "TST"

    def test_find_matching_agents_wrong_event_type(self, sample_agent_file):
        """Test that wrong event type doesn't match."""
        vault_path, agents_dir, _ = sample_agent_file

        registry = AgentRegistry(agents_dir, vault_path)

        # Wrong event type (modified instead of created)
        event_data = {
            'path': 'Ingest/Clippings/test.md',
            'event_type': 'modified'
        }

        matches = registry.find_matching_agents(event_data)

        assert len(matches) == 0

    def test_find_matching_agents_wrong_pattern(self, sample_agent_file):
        """Test that wrong path pattern doesn't match."""
        vault_path, agents_dir, _ = sample_agent_file

        registry = AgentRegistry(agents_dir, vault_path)

        # Wrong path (not in Ingest/Clippings/)
        event_data = {
            'path': 'AI/Tasks/test.md',
            'event_type': 'created'
        }

        matches = registry.find_matching_agents(event_data)

        assert len(matches) == 0

    def test_find_matching_agents_excluded_pattern(self, sample_agent_file):
        """Test that excluded patterns are not matched."""
        vault_path, agents_dir, _ = sample_agent_file

        registry = AgentRegistry(agents_dir, vault_path)

        # Matches pattern but excluded
        event_data = {
            'path': 'Ingest/Clippings/test.draft.md',
            'event_type': 'created'
        }

        matches = registry.find_matching_agents(event_data)

        assert len(matches) == 0

    def test_export_config_snapshot(self, sample_agent_file):
        """Test exporting agent configuration to JSON."""
        vault_path, agents_dir, _ = sample_agent_file

        registry = AgentRegistry(agents_dir, vault_path)

        output_path = vault_path / "config.json"
        registry.export_config_snapshot(output_path)

        assert output_path.exists()

        with open(output_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        assert "TST" in config
        assert config["TST"]["name"] == "Test Agent"
        assert config["TST"]["category"] == "ingestion"
        assert config["TST"]["trigger_pattern"] == "Ingest/Clippings/*.md"

    def test_handle_string_to_list_conversion(self, temp_vault):
        """Test that string values are converted to lists where needed."""
        vault_path, agents_dir = temp_vault

        # Agent with string instead of list for input_path
        agent_content = """---
title: "String Test"
abbreviation: "STR"
category: "ingestion"
trigger_pattern: "*.md"
trigger_event: "created"
input_path: "single/path"
skills: "skill1"
mcp_servers: "server1"
---
Prompt
"""

        (agents_dir / "string_test.md").write_text(agent_content, encoding='utf-8')

        registry = AgentRegistry(agents_dir, vault_path)

        agent = registry.agents["STR"]
        assert agent.input_path == ["single/path"]
        assert agent.skills == ["skill1"]
        assert agent.mcp_servers == ["server1"]

    def test_empty_agents_directory(self, temp_vault):
        """Test registry with no agent files."""
        vault_path, agents_dir = temp_vault

        registry = AgentRegistry(agents_dir, vault_path)

        assert len(registry.agents) == 0

    def test_nonexistent_agents_directory(self, temp_vault):
        """Test registry with nonexistent directory."""
        vault_path, _ = temp_vault

        # Use a directory that doesn't exist
        fake_dir = vault_path / "nonexistent"

        registry = AgentRegistry(fake_dir, vault_path)

        assert len(registry.agents) == 0
