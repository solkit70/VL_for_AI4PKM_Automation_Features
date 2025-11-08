"""Unit tests for main/orchestrator.py"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from ai4pkm_cli.main.orchestrator import run_orchestrator_daemon, show_orchestrator_status


class TestOrchestratorFunctions:
    """Test orchestrator CLI functions."""

    @pytest.fixture
    def temp_vault(self):
        """Create temporary vault."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            (vault_path / "_Settings_" / "Prompts").mkdir(parents=True)
            yield vault_path

    @patch('ai4pkm_cli.main.orchestrator.Orchestrator')
    @patch('ai4pkm_cli.main.orchestrator.Config')
    @patch('ai4pkm_cli.main.orchestrator.signal.signal')
    def test_run_orchestrator_daemon(self, mock_signal, mock_config_class, mock_orchestrator_class, temp_vault):
        """Test run_orchestrator_daemon function."""
        # Setup mocks
        mock_config = Mock()
        mock_config.get_orchestrator_max_concurrent.return_value = 3
        mock_config_class.return_value = mock_config
        
        mock_orchestrator = Mock()
        mock_orchestrator.get_status.return_value = {
            'agents_loaded': 2,
            'agent_list': [
                {'abbreviation': 'EIC', 'name': 'Enrich Ingested Content', 'category': 'ingestion'},
                {'abbreviation': 'CTP', 'name': 'Create Thread Postings', 'category': 'publish'}
            ]
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Call function (will hang on run_forever, so we'll mock it)
        mock_orchestrator.run_forever = Mock()
        
        # This will call run_forever which we've mocked, so it won't hang
        run_orchestrator_daemon(vault_path=temp_vault, debug=False)
        
        # Verify orchestrator was created
        mock_orchestrator_class.assert_called_once()
        call_kwargs = mock_orchestrator_class.call_args[1]
        assert call_kwargs['vault_path'] == temp_vault
        assert call_kwargs['max_concurrent'] == 3
        assert call_kwargs['debug'] is False
        
        # Verify signal handlers were set
        assert mock_signal.call_count == 2
        
        # Verify status was retrieved
        mock_orchestrator.get_status.assert_called_once()
        
        # Verify run_forever was called
        mock_orchestrator.run_forever.assert_called_once()

    @patch('ai4pkm_cli.main.orchestrator.Orchestrator')
    @patch('ai4pkm_cli.main.orchestrator.Config')
    def test_run_orchestrator_daemon_with_debug(self, mock_config_class, mock_orchestrator_class, temp_vault):
        """Test run_orchestrator_daemon with debug enabled."""
        mock_config = Mock()
        mock_config.get_orchestrator_max_concurrent.return_value = 5
        mock_config_class.return_value = mock_config
        
        mock_orchestrator = Mock()
        mock_orchestrator.get_status.return_value = {'agents_loaded': 0, 'agent_list': []}
        mock_orchestrator.run_forever = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        run_orchestrator_daemon(vault_path=temp_vault, debug=True)
        
        call_kwargs = mock_orchestrator_class.call_args[1]
        assert call_kwargs['debug'] is True

    @patch('ai4pkm_cli.main.orchestrator.Orchestrator')
    @patch('ai4pkm_cli.main.orchestrator.Config')
    def test_show_orchestrator_status(self, mock_config_class, mock_orchestrator_class, temp_vault):
        """Test show_orchestrator_status function."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config
        
        mock_orchestrator = Mock()
        mock_orchestrator.get_status.return_value = {
            'vault_path': str(temp_vault),
            'agents_loaded': 3,
            'max_concurrent': 3,
            'agent_list': [
                {'abbreviation': 'EIC', 'name': 'Enrich Ingested Content', 'category': 'ingestion'},
                {'abbreviation': 'CTP', 'name': 'Create Thread Postings', 'category': 'publish'},
                {'abbreviation': 'GDR', 'name': 'Generate Daily Roundup', 'category': 'workflow'}
            ]
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        show_orchestrator_status(vault_path=temp_vault)
        
        # Verify orchestrator was created
        mock_orchestrator_class.assert_called_once()
        call_kwargs = mock_orchestrator_class.call_args[1]
        assert call_kwargs['vault_path'] == temp_vault
        
        # Verify status was retrieved
        mock_orchestrator.get_status.assert_called_once()

    @patch('ai4pkm_cli.main.orchestrator.Orchestrator')
    @patch('ai4pkm_cli.main.orchestrator.Config')
    def test_show_orchestrator_status_no_agents(self, mock_config_class, mock_orchestrator_class, temp_vault):
        """Test show_orchestrator_status with no agents."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config
        
        mock_orchestrator = Mock()
        mock_orchestrator.get_status.return_value = {
            'vault_path': str(temp_vault),
            'agents_loaded': 0,
            'max_concurrent': 3,
            'agent_list': []
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Should not raise exception
        show_orchestrator_status(vault_path=temp_vault)
        
        mock_orchestrator.get_status.assert_called_once()

    @patch('ai4pkm_cli.main.orchestrator.Path.cwd')
    def test_run_orchestrator_daemon_defaults_to_cwd(self, mock_cwd, temp_vault):
        """Test that run_orchestrator_daemon defaults to CWD."""
        mock_cwd.return_value = temp_vault
        
        with patch('ai4pkm_cli.main.orchestrator.Config') as mock_config_class, \
             patch('ai4pkm_cli.main.orchestrator.Orchestrator') as mock_orchestrator_class:
            
            mock_config = Mock()
            mock_config.get_orchestrator_max_concurrent.return_value = 3
            mock_config_class.return_value = mock_config
            
            mock_orchestrator = Mock()
            mock_orchestrator.get_status.return_value = {'agents_loaded': 0, 'agent_list': []}
            mock_orchestrator.run_forever = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator
            
            run_orchestrator_daemon(vault_path=None, debug=False)
            
            # Should use CWD
            mock_cwd.assert_called_once()
            call_kwargs = mock_orchestrator_class.call_args[1]
            assert call_kwargs['vault_path'] == temp_vault

