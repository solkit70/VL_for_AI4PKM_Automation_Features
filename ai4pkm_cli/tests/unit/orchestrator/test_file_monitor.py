"""Unit tests for file monitor."""
import pytest
import time
from pathlib import Path
from ai4pkm_cli.orchestrator.file_monitor import FileSystemMonitor


def test_file_monitor_initialization(tmp_path):
    """Test FileSystemMonitor initialization."""
    monitor = FileSystemMonitor(tmp_path)
    
    assert monitor.vault_path == tmp_path
    assert monitor.event_queue.empty()
    assert monitor.is_running is False


def test_file_monitor_start_stop(tmp_path):
    """Test FileSystemMonitor start and stop."""
    monitor = FileSystemMonitor(tmp_path)
    
    monitor.start()
    assert monitor.is_running is True
    
    monitor.stop()
    time.sleep(0.1)
    assert monitor.is_running is False


def test_file_monitor_detects_new_file(tmp_path):
    """Test that FileSystemMonitor detects new file creation."""
    monitor = FileSystemMonitor(tmp_path)
    monitor.start()

    try:
        test_file = tmp_path / "test.md"
        test_file.write_text("---\ntitle: Test\n---\n# Content")

        time.sleep(0.5)

        assert not monitor.event_queue.empty()

        event = monitor.event_queue.get(timeout=1.0)
        # FileEvent is now an object, not a dict
        assert event.event_type == 'created'
        assert 'test.md' in event.path

    finally:
        monitor.stop()


def test_file_monitor_ignores_non_markdown(tmp_path):
    """Test that FileSystemMonitor ignores non-markdown files."""
    monitor = FileSystemMonitor(tmp_path)
    monitor.start()
    
    try:
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test")
        
        time.sleep(0.5)
        
        assert monitor.event_queue.empty()
        
    finally:
        monitor.stop()


def test_file_monitor_parses_frontmatter(tmp_path):
    """Test that FileSystemMonitor parses frontmatter from files."""
    monitor = FileSystemMonitor(tmp_path)
    monitor.start()

    try:
        test_file = tmp_path / "test.md"
        test_file.write_text("---\ntitle: Test Document\nstatus: pending\n---\n# Content")

        time.sleep(0.5)

        event = monitor.event_queue.get(timeout=1.0)

        # FileEvent is now an object with frontmatter attribute
        assert event.frontmatter is not None
        assert event.frontmatter['title'] == 'Test Document'
        assert event.frontmatter['status'] == 'pending'

    finally:
        monitor.stop()


def test_file_monitor_queues_multiple_events(tmp_path):
    """Test that FileSystemMonitor queues multiple file events."""
    monitor = FileSystemMonitor(tmp_path)
    monitor.start()
    
    try:
        # Create multiple files
        (tmp_path / "test1.md").write_text("# Test 1")
        (tmp_path / "test2.md").write_text("# Test 2")
        (tmp_path / "test3.md").write_text("# Test 3")
        
        time.sleep(0.5)
        
        # Should have at least 3 events
        event_count = 0
        while not monitor.event_queue.empty():
            monitor.event_queue.get_nowait()
            event_count += 1
        
        assert event_count >= 3
        
    finally:
        monitor.stop()
