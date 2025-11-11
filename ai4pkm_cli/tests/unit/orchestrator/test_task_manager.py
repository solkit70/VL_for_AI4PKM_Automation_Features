"""Unit tests for task_manager.py"""

import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch
import pytest

from ai4pkm_cli.orchestrator.task_manager import TaskFileManager
from ai4pkm_cli.orchestrator.models import AgentDefinition, ExecutionContext


class TestTaskFileManager:
    """Test TaskFileManager functionality."""

    @pytest.fixture
    def temp_vault(self):
        """Create temporary vault structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            (vault_path / "_Settings_" / "Tasks").mkdir(parents=True)
            yield vault_path

    @pytest.fixture
    def mock_config(self):
        """Create mock config."""
        config = Mock()
        config.get_orchestrator_tasks_dir.return_value = "_Settings_/Tasks"
        return config

    @pytest.fixture
    def sample_agent(self):
        """Create sample agent definition."""
        return AgentDefinition(
            title="Test Agent",
            abbreviation="TST",
            category="test",
            executor="claude_code",
            task_create=True,
            task_priority="medium"
        )

    @pytest.fixture
    def execution_context(self, temp_vault):
        """Create execution context."""
        ctx = ExecutionContext(
            trigger_data={"path": "Test/input.md"},
            agent_abbreviation="TST",
            timestamp=datetime.now()
        )
        ctx.log_file = temp_vault / "_Settings_" / "Logs" / "test.log"
        ctx.log_file.parent.mkdir(parents=True, exist_ok=True)
        return ctx

    def test_init_with_config(self, temp_vault, mock_config):
        """Test initialization with config."""
        manager = TaskFileManager(temp_vault, config=mock_config)
        assert manager.vault_path == temp_vault
        assert manager.tasks_dir == temp_vault / "_Settings_" / "Tasks"
        assert manager.tasks_dir.exists()

    def test_init_with_orchestrator_settings(self, temp_vault):
        """Test initialization with orchestrator settings override."""
        settings = {"tasks_dir": "Custom/Tasks"}
        manager = TaskFileManager(temp_vault, orchestrator_settings=settings)
        assert manager.tasks_dir == temp_vault / "Custom" / "Tasks"
        assert manager.tasks_dir.exists()

    def test_create_task_file(self, temp_vault, mock_config, sample_agent, execution_context):
        """Test task file creation."""
        manager = TaskFileManager(temp_vault, config=mock_config)
        
        task_path = manager.create_task_file(execution_context, sample_agent)
        
        assert task_path is not None
        assert task_path.exists()
        assert task_path.name.startswith("202")
        assert "TST" in task_path.name
        
        # Check content
        content = task_path.read_text(encoding='utf-8')
        assert "---" in content
        assert "status: \"IN_PROGRESS\"" in content
        assert "agent: \"TST\"" in content
        assert "Test/input.md" in content

    def test_create_task_file_disabled(self, temp_vault, mock_config, execution_context):
        """Test that task file is not created when disabled."""
        agent = AgentDefinition(
            title="Test Agent",
            abbreviation="TST",
            category="test",
            executor="claude_code",
            task_create=False  # Disabled
        )
        
        manager = TaskFileManager(temp_vault, config=mock_config)
        task_path = manager.create_task_file(execution_context, agent)
        
        assert task_path is None

    def test_update_task_status(self, temp_vault, mock_config, sample_agent, execution_context):
        """Test updating task status."""
        manager = TaskFileManager(temp_vault, config=mock_config)
        
        # Create task file
        task_path = manager.create_task_file(execution_context, sample_agent)
        assert task_path is not None
        
        # Update status
        manager.update_task_status(task_path, "PROCESSED")
        
        # Verify update
        content = task_path.read_text(encoding='utf-8')
        assert "status: \"PROCESSED\"" in content
        assert "status: \"IN_PROGRESS\"" not in content

    def test_update_task_status_with_output(self, temp_vault, mock_config, sample_agent, execution_context):
        """Test updating task status with output link."""
        manager = TaskFileManager(temp_vault, config=mock_config)
        
        task_path = manager.create_task_file(execution_context, sample_agent)
        assert task_path is not None
        
        # Update with output
        manager.update_task_status(task_path, "COMPLETED", output_link="[[AI/Articles/Output.md]]")
        
        content = task_path.read_text(encoding='utf-8')
        assert "status: \"COMPLETED\"" in content
        assert "output: \"[[AI/Articles/Output.md]]\"" in content

    def test_task_filename_generation(self, temp_vault, mock_config, sample_agent, execution_context):
        """Test task filename generation."""
        manager = TaskFileManager(temp_vault, config=mock_config)
        
        task_path = manager.create_task_file(execution_context, sample_agent)
        
        # Check filename format: YYYY-MM-DD {ABBR} - {input}.md
        filename = task_path.name
        assert filename.startswith(datetime.now().strftime("%Y-%m-%d"))
        assert "TST" in filename
        assert "input" in filename
        assert filename.endswith(".md")

    def test_task_filename_truncation(self, temp_vault, mock_config, sample_agent):
        """Test that long filenames are truncated."""
        # Create context with very long input filename
        long_name = "a" * 300 + ".md"
        ctx = ExecutionContext(
            trigger_data={"path": f"Test/{long_name}"},
            agent_abbreviation="TST",
            timestamp=datetime.now()
        )
        ctx.log_file = temp_vault / "_Settings_" / "Logs" / "test.log"
        
        manager = TaskFileManager(temp_vault, config=mock_config)
        task_path = manager.create_task_file(ctx, sample_agent)
        
        # Filename should be truncated (macOS limit is 255 bytes)
        assert len(task_path.name.encode('utf-8')) <= 255

