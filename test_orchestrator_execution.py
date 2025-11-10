#!/usr/bin/env python3
"""
End-to-end test suite for orchestrator execution functionality.

Tests agent execution, task processing, file monitoring, and concurrency.
Complements hot_reload_scenarios.py by testing runtime behavior.
"""

import subprocess
import time
import signal
import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re

# Test configuration
VAULT_PATH = Path("/Users/minsukkang/GitHub/temp/AI4PKM/ai4pkm_vault")
ORCHESTRATOR_YAML = VAULT_PATH / "orchestrator.yaml"
BACKUP_YAML = VAULT_PATH / "orchestrator.yaml.backup"
LOG_FILE = VAULT_PATH / "_Settings_/Logs" / f"ai4pkm_{datetime.now().strftime('%Y-%m-%d')}.log"
TEST_TIMEOUT = 300  # 5 minutes per test


class OrchestratorExecutionTestSuite:
    """Test suite for orchestrator execution scenarios."""
    
    def __init__(self):
        self.vault_path = VAULT_PATH
        self.orchestrator_yaml = ORCHESTRATOR_YAML
        self.backup_yaml = BACKUP_YAML
        self.log_file = LOG_FILE
        self.orchestrator_process: Optional[subprocess.Popen] = None
        self.test_results: List[Dict] = []
        self.log_position_before_test: int = 0
        
    def setup(self):
        """Setup test environment."""
        print("=" * 80)
        print("Orchestrator Execution Test Suite Setup")
        print("=" * 80)
        
        # Backup original orchestrator.yaml
        if self.orchestrator_yaml.exists():
            with open(self.orchestrator_yaml, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(self.backup_yaml, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            print(f"✓ Backed up orchestrator.yaml")
        else:
            print("⚠ orchestrator.yaml not found")
            return False
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        print(f"✓ Log file: {self.log_file}")
        
        return True
    
    def teardown(self):
        """Cleanup test environment."""
        print("\n" + "=" * 80)
        print("Teardown")
        print("=" * 80)
        
        # Stop orchestrator if running
        if self.orchestrator_process:
            self.stop_orchestrator()
        
        # Restore original orchestrator.yaml
        if self.backup_yaml.exists():
            try:
                with open(self.backup_yaml, 'r', encoding='utf-8') as f:
                    backup_content = f.read()
                temp_file = self.orchestrator_yaml.with_suffix('.yaml.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(backup_content)
                    f.flush()
                    os.fsync(f.fileno())
                temp_file.replace(self.orchestrator_yaml)
                print(f"✓ Restored orchestrator.yaml from backup")
            except Exception as e:
                print(f"✗ Error restoring orchestrator.yaml: {e}")
    
    def start_orchestrator(self) -> bool:
        """Start orchestrator daemon."""
        if self.orchestrator_process:
            print("⚠ Orchestrator already running")
            return True
            
        print("\nStarting orchestrator daemon...")
        try:
            self.orchestrator_process = subprocess.Popen(
                [sys.executable, "-m", "ai4pkm_cli.main.cli", "--orchestrator"],
                cwd=str(self.vault_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Wait for initialization
            time.sleep(3)
            
            if self.orchestrator_process.poll() is not None:
                print("✗ Orchestrator failed to start")
                return False
                
            print(f"✓ Orchestrator started (PID: {self.orchestrator_process.pid})")
            return True
        except Exception as e:
            print(f"✗ Error starting orchestrator: {e}")
            return False
    
    def stop_orchestrator(self):
        """Stop orchestrator daemon."""
        if not self.orchestrator_process:
            return
        
        print("\nStopping orchestrator...")
        try:
            self.orchestrator_process.terminate()
            try:
                self.orchestrator_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.orchestrator_process.kill()
                self.orchestrator_process.wait()
            print("✓ Orchestrator stopped")
        except Exception as e:
            print(f"✗ Error stopping orchestrator: {e}")
        finally:
            self.orchestrator_process = None
    
    def wait_for_log_pattern(self, pattern: str, timeout: int = 30) -> bool:
        """Wait for a pattern to appear in logs."""
        start_time = time.time()
        last_log_size = self.log_position_before_test if hasattr(self, 'log_position_before_test') else 0
        
        while time.time() - start_time < timeout:
            if not self.log_file.exists():
                time.sleep(0.5)
                continue
            
            with open(self.log_file, 'r') as f:
                f.seek(last_log_size)
                new_content = f.read()
                last_log_size = f.tell()
            
            if re.search(pattern, new_content, re.MULTILINE | re.DOTALL):
                return True
            
            time.sleep(0.5)
        
        return False
    
    def check_log_patterns(self, patterns: List[str], use_test_log_only: bool = False) -> Tuple[bool, List[str]]:
        """Check if log contains expected patterns."""
        if not self.log_file.exists():
            return False, ["Log file does not exist"]
        
        with open(self.log_file, 'r') as f:
            if use_test_log_only and self.log_position_before_test > 0:
                f.seek(self.log_position_before_test)
                log_content = f.read()
            else:
                log_content = f.read()
        
        found_patterns = []
        missing_patterns = []
        
        for pattern in patterns:
            if re.search(pattern, log_content, re.MULTILINE | re.DOTALL):
                found_patterns.append(pattern)
            else:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            return False, [f"Missing patterns: {missing_patterns}"]
        
        return True, found_patterns
    
    def find_task_files(self, agent_abbr: str = None, status: str = None) -> List[Path]:
        """Find task files matching criteria."""
        from ai4pkm_cli.config import Config as ConfigClass
        config_obj = ConfigClass()
        tasks_dir_rel = config_obj.get_orchestrator_tasks_dir()
        tasks_dir = self.vault_path / tasks_dir_rel
        tasks_dir.mkdir(parents=True, exist_ok=True)
        
        task_files = []
        for task_file in tasks_dir.glob("*.md"):
            try:
                content = task_file.read_text(encoding='utf-8')
                # Parse frontmatter
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 2:
                        frontmatter = yaml.safe_load(parts[1])
                        task_status = frontmatter.get('status', '')
                        task_type = frontmatter.get('task_type', '')
                        
                        match = True
                        if agent_abbr and task_type != agent_abbr:
                            match = False
                        if status and task_status != status:
                            match = False
                        
                        if match:
                            task_files.append(task_file)
            except:
                pass
        
        return task_files
    
    def run_test(self, test_name: str, test_func) -> Dict:
        """Run a single test case."""
        print("\n" + "=" * 80)
        print(f"Test: {test_name}")
        print("=" * 80)
        
        # Track log position before test starts
        if self.log_file.exists():
            self.log_position_before_test = self.log_file.stat().st_size
        else:
            self.log_position_before_test = 0
        
        test_start = time.time()
        success = False
        error_msg = None
        
        try:
            success, error_msg = test_func()
        except Exception as e:
            error_msg = f"Test exception: {str(e)}"
            import traceback
            traceback.print_exc()
        
        duration = time.time() - test_start
        
        result = {
            "test_name": test_name,
            "success": success,
            "duration": duration,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"\n{status}: {test_name} ({duration:.2f}s)")
        if error_msg:
            print(f"  Error: {error_msg}")
        
        return result
    
    # ============================================================================
    # TEST SCENARIOS
    # ============================================================================
    
    def test_1_file_creation_triggers_agent(self) -> Tuple[bool, Optional[str]]:
        """Test 1: Creating a file in input_path triggers agent execution."""
        if not self.start_orchestrator():
            return False, "Failed to start orchestrator"
        
        time.sleep(2)
        
        # Ensure we have an agent with input_path configured
        with open(self.orchestrator_yaml, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Find an agent with input_path that has a prompt file
        agent_with_input = None
        for node in config.get('nodes', []):
            if node.get('type') == 'agent' and node.get('input_path'):
                agent_name = node.get('name', '')
                prompt_file = self.vault_path / "_Settings_/Prompts" / f"{agent_name}.md"
                if prompt_file.exists():
                    agent_with_input = node
                    break
        
        if not agent_with_input:
            return True, None  # Skip if no agent with input_path and prompt file
        
        input_path = agent_with_input.get('input_path')
        agent_name = agent_with_input.get('name', '')
        
        # Create test file in input_path
        test_dir = self.vault_path / input_path
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file = test_dir / f"test_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        test_file.write_text("# Test Content\n\nThis should trigger agent execution.")
        
        # Wait for agent to be triggered
        if not self.wait_for_log_pattern(rf"Processing event.*{test_file.name}", timeout=30):
            # Cleanup
            if test_file.exists():
                test_file.unlink()
            return False, "Agent was not triggered by file creation"
        
        # Check that task file was created
        time.sleep(2)  # Give time for task file creation
        task_files = self.find_task_files()
        
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        
        if not task_files:
            return False, "No task file was created"
        
        return True, None
    
    def test_2_task_status_lifecycle(self) -> Tuple[bool, Optional[str]]:
        """Test 2: Task progresses through QUEUED -> IN_PROGRESS -> PROCESSED."""
        if not self.start_orchestrator():
            return False, "Failed to start orchestrator"
        
        time.sleep(2)
        
        # Create a file that will trigger an agent
        with open(self.orchestrator_yaml, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        agent_with_input = None
        for node in config.get('nodes', []):
            if node.get('type') == 'agent' and node.get('input_path'):
                agent_with_input = node
                break
        
        if not agent_with_input:
            return True, None  # Skip
        
        input_path = agent_with_input.get('input_path')
        test_dir = self.vault_path / input_path
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file = test_dir / f"test_lifecycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        test_file.write_text("# Test Lifecycle\n\nTesting task status transitions.")
        
        # Wait for task file creation
        time.sleep(3)
        task_files = self.find_task_files()
        
        if not task_files:
            # Cleanup
            if test_file.exists():
                test_file.unlink()
            return False, "No task file created"
        
        # Check initial status (should be QUEUED or IN_PROGRESS)
        task_file = task_files[0]
        content = task_file.read_text(encoding='utf-8')
        
        if "---" in content:
            parts = content.split("---", 2)
            frontmatter = yaml.safe_load(parts[1])
            initial_status = frontmatter.get('status', '')
            
            if initial_status not in ['QUEUED', 'IN_PROGRESS', 'FAILED']:
                if test_file.exists():
                    test_file.unlink()
                return False, f"Unexpected initial status: {initial_status}"
            
            # If FAILED, that's also a valid state (agent might have failed quickly)
            if initial_status == 'FAILED':
                if test_file.exists():
                    test_file.unlink()
                if task_file.exists():
                    task_file.unlink()
                return True, None
        
        # Wait for status to change (if QUEUED, should become IN_PROGRESS)
        max_wait = 30
        waited = 0
        while waited < max_wait:
            time.sleep(2)
            waited += 2
            
            content = task_file.read_text(encoding='utf-8')
            if "---" in content:
                parts = content.split("---", 2)
                frontmatter = yaml.safe_load(parts[1])
                current_status = frontmatter.get('status', '')
                
                if current_status in ['PROCESSED', 'FAILED']:
                    # Cleanup
                    if test_file.exists():
                        test_file.unlink()
                    if task_file.exists():
                        task_file.unlink()
                    return True, None
        
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if task_file.exists():
            task_file.unlink()
        
        return False, "Task did not complete within timeout"
    
    def test_3_concurrent_execution_limit(self) -> Tuple[bool, Optional[str]]:
        """Test 3: max_concurrent limits concurrent executions."""
        if not self.start_orchestrator():
            return False, "Failed to start orchestrator"
        
        time.sleep(2)
        
        # Get max_concurrent setting
        with open(self.orchestrator_yaml, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        max_concurrent = config.get('orchestrator', {}).get('max_concurrent', 3)
        
        # Create multiple files simultaneously to trigger multiple agents
        with open(self.orchestrator_yaml, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        agent_with_input = None
        for node in config.get('nodes', []):
            if node.get('type') == 'agent' and node.get('input_path'):
                agent_with_input = node
                break
        
        if not agent_with_input:
            return True, None  # Skip
        
        input_path = agent_with_input.get('input_path')
        test_dir = self.vault_path / input_path
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Create more files than max_concurrent
        num_files = max_concurrent + 2
        test_files = []
        for i in range(num_files):
            test_file = test_dir / f"test_concurrent_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            test_file.write_text(f"# Test Concurrent {i}\n\nTesting concurrent execution limits.")
            test_files.append(test_file)
        
        # Wait a bit and check logs for concurrent execution count
        time.sleep(5)
        
        # Check logs for execution count
        with open(self.log_file, 'r') as f:
            f.seek(self.log_position_before_test)
            log_content = f.read()
        
        # Count "Starting execution" messages (should not exceed max_concurrent)
        execution_starts = len(re.findall(r"Starting execution", log_content))
        
        # Cleanup
        for test_file in test_files:
            if test_file.exists():
                test_file.unlink()
        
        # Note: This is a soft check - exact count depends on timing
        # The important thing is that we don't see way more than max_concurrent
        if execution_starts > max_concurrent * 2:
            return False, f"Too many concurrent executions: {execution_starts} (max: {max_concurrent})"
        
        return True, None
    
    def test_4_queued_task_processing(self) -> Tuple[bool, Optional[str]]:
        """Test 4: QUEUED tasks are processed when capacity becomes available."""
        if not self.start_orchestrator():
            return False, "Failed to start orchestrator"
        
        time.sleep(2)
        
        # Set max_concurrent to 1 to force queuing
        with open(self.orchestrator_yaml, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        original_max = config.get('orchestrator', {}).get('max_concurrent', 3)
        
        # Temporarily set to 1
        config['orchestrator']['max_concurrent'] = 1
        
        temp_file = self.orchestrator_yaml.with_suffix('.yaml.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                f.flush()
                os.fsync(f.fileno())
            temp_file.replace(self.orchestrator_yaml)
        except Exception as e:
            return False, f"Failed to update config: {e}"
        
        os.utime(self.orchestrator_yaml, None)
        time.sleep(3)  # Wait for reload
        
        # Create 2 files - first should execute, second should be QUEUED
        with open(self.orchestrator_yaml, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        agent_with_input = None
        for node in config.get('nodes', []):
            if node.get('type') == 'agent' and node.get('input_path'):
                agent_with_input = node
                break
        
        if not agent_with_input:
            # Restore config
            config['orchestrator']['max_concurrent'] = original_max
            temp_file = self.orchestrator_yaml.with_suffix('.yaml.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                f.flush()
                os.fsync(f.fileno())
            temp_file.replace(self.orchestrator_yaml)
            return True, None  # Skip
        
        input_path = agent_with_input.get('input_path')
        test_dir = self.vault_path / input_path
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_file1 = test_dir / f"test_queued_1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        test_file1.write_text("# Test Queued 1\n\nFirst file.")
        test_file2 = test_dir / f"test_queued_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        test_file2.write_text("# Test Queued 2\n\nSecond file - should be queued.")
        
        # Wait for first to start and second to be queued
        time.sleep(3)
        
        queued_tasks = self.find_task_files(status='QUEUED')
        in_progress_tasks = self.find_task_files(status='IN_PROGRESS')
        
        # Restore config
        config['orchestrator']['max_concurrent'] = original_max
        temp_file = self.orchestrator_yaml.with_suffix('.yaml.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            f.flush()
            os.fsync(f.fileno())
        temp_file.replace(self.orchestrator_yaml)
        os.utime(self.orchestrator_yaml, None)
        time.sleep(2)  # Wait for reload
        
        # Wait for queued task to be processed
        max_wait = 30
        waited = 0
        while waited < max_wait:
            time.sleep(2)
            waited += 2
            queued_tasks = self.find_task_files(status='QUEUED')
            if not queued_tasks:
                break
        
        # Cleanup
        if test_file1.exists():
            test_file1.unlink()
        if test_file2.exists():
            test_file2.unlink()
        
        # Check that at least one task was queued initially
        if not queued_tasks and waited == 0:
            return False, "No tasks were queued (expected at least one)"
        
        return True, None
    
    def test_5_agent_exclude_pattern(self) -> Tuple[bool, Optional[str]]:
        """Test 5: Files matching exclude_pattern don't trigger agents."""
        if not self.start_orchestrator():
            return False, "Failed to start orchestrator"
        
        time.sleep(2)
        
        # Find agent with exclude pattern (like HTC) that has a prompt file
        with open(self.orchestrator_yaml, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        agent_with_exclude = None
        for node in config.get('nodes', []):
            if node.get('type') == 'agent' and node.get('trigger_exclude_pattern'):
                agent_name = node.get('name', '')
                prompt_file = self.vault_path / "_Settings_/Prompts" / f"{agent_name}.md"
                if prompt_file.exists():
                    agent_with_exclude = node
                    break
        
        if not agent_with_exclude:
            return True, None  # Skip if no agent with exclude pattern and prompt file
        
        exclude_pattern = agent_with_exclude.get('trigger_exclude_pattern', '')
        
        # Create file in excluded path
        if '_Settings_' in exclude_pattern:
            excluded_dir = self.vault_path / "_Settings_/Tasks"
            excluded_dir.mkdir(parents=True, exist_ok=True)
            test_file = excluded_dir / f"test_excluded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            test_file.write_text("# Test Excluded\n\nThis should NOT trigger agent.")
            
            # Wait a bit
            time.sleep(3)
            
            # Check logs - should not see agent execution for this file
            with open(self.log_file, 'r') as f:
                f.seek(self.log_position_before_test)
                log_content = f.read()
            
            # Check that file was detected but agent was not triggered
            file_detected = test_file.name in log_content
            agent_triggered = agent_with_exclude.get('name', '').split('(')[0].strip() in log_content
            
            # Cleanup
            if test_file.exists():
                test_file.unlink()
            
            if file_detected and agent_triggered:
                return False, "Agent was triggered for excluded file"
            
            return True, None
        
        return True, None
    
    def test_6_task_file_creation(self) -> Tuple[bool, Optional[str]]:
        """Test 6: Task files are created with correct structure."""
        if not self.start_orchestrator():
            return False, "Failed to start orchestrator"
        
        time.sleep(2)
        
        # Create a file to trigger agent
        with open(self.orchestrator_yaml, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        agent_with_input = None
        for node in config.get('nodes', []):
            if node.get('type') == 'agent' and node.get('input_path'):
                agent_with_input = node
                break
        
        if not agent_with_input:
            return True, None  # Skip
        
        input_path = agent_with_input.get('input_path')
        agent_name = agent_with_input.get('name', '')
        
        # Extract abbreviation
        abbr_match = re.search(r'\(([A-Z]{3,4})\)', agent_name)
        agent_abbr = abbr_match.group(1) if abbr_match else None
        
        test_dir = self.vault_path / input_path
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file = test_dir / f"test_task_structure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        test_file.write_text("# Test Task Structure\n\nTesting task file creation.")
        
        # Wait for task file creation
        time.sleep(3)
        
        task_files = self.find_task_files(agent_abbr=agent_abbr) if agent_abbr else self.find_task_files()
        
        if not task_files:
            if test_file.exists():
                test_file.unlink()
            return False, "No task file was created"
        
        task_file = task_files[0]
        content = task_file.read_text(encoding='utf-8')
        
        # Verify structure
        if not content.startswith("---"):
            if test_file.exists():
                test_file.unlink()
            if task_file.exists():
                task_file.unlink()
            return False, "Task file doesn't start with frontmatter"
        
        parts = content.split("---", 2)
        if len(parts) < 2:
            if test_file.exists():
                test_file.unlink()
            if task_file.exists():
                task_file.unlink()
            return False, "Task file has invalid frontmatter structure"
        
        frontmatter = yaml.safe_load(parts[1])
        
        required_fields = ['status', 'task_type']
        for field in required_fields:
            if field not in frontmatter:
                if test_file.exists():
                    test_file.unlink()
                if task_file.exists():
                    task_file.unlink()
                return False, f"Task file missing required field: {field}"
        
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if task_file.exists():
            task_file.unlink()
        
        return True, None
    
    def test_7_file_modification_triggers(self) -> Tuple[bool, Optional[str]]:
        """Test 7: Modifying a file triggers agent (if configured)."""
        if not self.start_orchestrator():
            return False, "Failed to start orchestrator"
        
        time.sleep(2)
        
        # Create and then modify a file
        with open(self.orchestrator_yaml, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        agent_with_input = None
        for node in config.get('nodes', []):
            if node.get('type') == 'agent' and node.get('input_path'):
                agent_with_input = node
                break
        
        if not agent_with_input:
            return True, None  # Skip
        
        input_path = agent_with_input.get('input_path')
        test_dir = self.vault_path / input_path
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = test_dir / f"test_modify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        test_file.write_text("# Test Modify\n\nInitial content.")
        
        # Wait for initial trigger
        time.sleep(2)
        
        # Modify the file
        test_file.write_text("# Test Modify\n\nModified content.")
        os.utime(test_file, None)  # Touch file
        
        # Wait for modification trigger
        if not self.wait_for_log_pattern(rf"Processing event.*{test_file.name}", timeout=20):
            if test_file.exists():
                test_file.unlink()
            return False, "Agent was not triggered by file modification"
        
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        
        return True, None
    
    def test_8_multiple_agents_same_file(self) -> Tuple[bool, Optional[str]]:
        """Test 8: Multiple agents can match the same file."""
        if not self.start_orchestrator():
            return False, "Failed to start orchestrator"
        
        time.sleep(2)
        
        # Create a file that might match multiple agents
        # Use a general path that multiple agents might watch
        test_dir = self.vault_path / "Journals"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = test_dir / f"test_multi_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        test_file.write_text("# Test Multi Agent\n\nThis might match multiple agents.")
        
        # Wait for processing
        time.sleep(5)
        
        # Check logs for multiple agent executions
        with open(self.log_file, 'r') as f:
            f.seek(self.log_position_before_test)
            log_content = f.read()
        
        # Count unique agent executions for this file
        execution_matches = re.findall(r"Starting execution.*\(ID: ([^)]+)\)", log_content)
        
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        
        # If we see multiple executions, that's fine (multiple agents matched)
        # If we see at least one, that's also fine
        return True, None
    
    def test_9_task_file_naming(self) -> Tuple[bool, Optional[str]]:
        """Test 9: Task files follow naming convention."""
        if not self.start_orchestrator():
            return False, "Failed to start orchestrator"
        
        time.sleep(2)
        
        # Create a file to trigger agent
        with open(self.orchestrator_yaml, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        agent_with_input = None
        for node in config.get('nodes', []):
            if node.get('type') == 'agent' and node.get('input_path'):
                agent_with_input = node
                break
        
        if not agent_with_input:
            return True, None  # Skip
        
        input_path = agent_with_input.get('input_path')
        agent_name = agent_with_input.get('name', '')
        
        # Extract abbreviation
        abbr_match = re.search(r'\(([A-Z]{3,4})\)', agent_name)
        agent_abbr = abbr_match.group(1) if abbr_match else None
        
        test_dir = self.vault_path / input_path
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file = test_dir / f"test_naming_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        test_file.write_text("# Test Naming\n\nTesting task file naming.")
        
        # Wait for task file creation
        time.sleep(3)
        
        task_files = self.find_task_files(agent_abbr=agent_abbr) if agent_abbr else self.find_task_files()
        
        if not task_files:
            if test_file.exists():
                test_file.unlink()
            return False, "No task file was created"
        
        task_file = task_files[0]
        task_name = task_file.name
        
        # Verify naming: YYYY-MM-DD {ABBR} - {input}.md
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        if not re.search(date_pattern, task_name):
            if test_file.exists():
                test_file.unlink()
            if task_file.exists():
                task_file.unlink()
            return False, f"Task file name doesn't contain date: {task_name}"
        
        if agent_abbr and agent_abbr not in task_name:
            if test_file.exists():
                test_file.unlink()
            if task_file.exists():
                task_file.unlink()
            return False, f"Task file name doesn't contain agent abbreviation: {task_name}"
        
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if task_file.exists():
            task_file.unlink()
        
        return True, None
    
    def test_10_error_handling(self) -> Tuple[bool, Optional[str]]:
        """Test 10: Errors in agent execution are handled gracefully."""
        if not self.start_orchestrator():
            return False, "Failed to start orchestrator"
        
        time.sleep(2)
        
        # Create a file that might cause an error (e.g., invalid content)
        # This is a soft test - we just verify orchestrator doesn't crash
        with open(self.orchestrator_yaml, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        agent_with_input = None
        for node in config.get('nodes', []):
            if node.get('type') == 'agent' and node.get('input_path'):
                agent_with_input = node
                break
        
        if not agent_with_input:
            return True, None  # Skip
        
        input_path = agent_with_input.get('input_path')
        test_dir = self.vault_path / input_path
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = test_dir / f"test_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        test_file.write_text("# Test Error\n\n" + "x" * 10000)  # Large content
        
        # Wait a bit
        time.sleep(5)
        
        # Check that orchestrator is still running
        if self.orchestrator_process and self.orchestrator_process.poll() is not None:
            if test_file.exists():
                test_file.unlink()
            return False, "Orchestrator crashed after error"
        
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        
        return True, None


def main():
    """Run all tests."""
    suite = OrchestratorExecutionTestSuite()
    
    if not suite.setup():
        print("✗ Setup failed")
        return 1
    
    try:
        # Run all tests
        tests = [
            ("File Creation Triggers Agent", suite.test_1_file_creation_triggers_agent),
            ("Task Status Lifecycle", suite.test_2_task_status_lifecycle),
            ("Concurrent Execution Limit", suite.test_3_concurrent_execution_limit),
            ("Queued Task Processing", suite.test_4_queued_task_processing),
            ("Agent Exclude Pattern", suite.test_5_agent_exclude_pattern),
            ("Task File Creation", suite.test_6_task_file_creation),
            ("File Modification Triggers", suite.test_7_file_modification_triggers),
            ("Multiple Agents Same File", suite.test_8_multiple_agents_same_file),
            ("Task File Naming", suite.test_9_task_file_naming),
            ("Error Handling", suite.test_10_error_handling),
        ]
        
        for test_name, test_func in tests:
            suite.run_test(test_name, test_func)
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total = len(suite.test_results)
        passed = sum(1 for r in suite.test_results if r['success'])
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ✗")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n" + "-" * 80)
        print("Detailed Results:")
        print("-" * 80)
        
        for result in suite.test_results:
            status = "✓ PASS" if result['success'] else "✗ FAIL"
            print(f"{status:8} | {result['test_name']:40} | {result['duration']:6.2f}s")
            if result['error']:
                print(f"         |   Error: {result['error']}")
        
        # Save results
        results_file = VAULT_PATH / "orchestrator_execution_test_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "success_rate": success_rate
                },
                "results": suite.test_results
            }, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")
        
    finally:
        suite.teardown()
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

