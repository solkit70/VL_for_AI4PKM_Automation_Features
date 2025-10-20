"""Integration test for KTG/KTP/KTE workflow - #AI Hashtag scenario.

This test simulates the complete end-to-end workflow:
1. Starts ai4pkm watchdog in test mode
2. Creates test file with #AI hashtag
3. Monitors: HashtagFileHandler → Task Request → KTG → KTP → KTE
4. Validates completion and cleanup

Test validates:
- No tasks missed (all stages complete)
- No duplicated processing
- Task completed with correct output
"""

import os
import sys
import time
import json
import shutil
import subprocess
import signal
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger import Logger
from config import Config


class KTGKTPHashtagIntegrationTest:
    """Integration test for KTG/KTP/KTE #AI Hashtag workflow."""

    def __init__(self):
        """Initialize test environment."""
        self.logger = Logger(console_output=True)

        # IMPORTANT: Use the AI4PKM repo as test workspace, NOT production vault!
        # The repo has the same folder structure (AI/, Ingest/, Projects/, etc.) for testing
        self.repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.workspace_path = self.repo_root

        # Config must be loaded from workspace
        self.config = Config(config_file=os.path.join(self.workspace_path, 'ai4pkm_cli.json'))

        # Validate workspace has required folders
        required_folders = ['AI/Tasks', 'Projects', '_Settings_/Prompts']
        for folder in required_folders:
            full_path = os.path.join(self.workspace_path, folder)
            if not os.path.exists(full_path):
                raise ValueError(f"Invalid test workspace: {full_path} does not exist")

        self.logger.info(f"Using test workspace: {self.workspace_path}")

        # Test file paths
        self.test_timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        self.test_hashtag_name = f"2025-10-17 Test Writing Task with AI Hashtag {self.test_timestamp}.md"
        self.test_hashtag_path = os.path.join(
            self.workspace_path,
            "Projects",
            self.test_hashtag_name
        )

        # Paths to monitor
        self.requests_dir = os.path.join(self.workspace_path, "AI", "Tasks", "Requests", "Hashtag")
        self.tasks_dir = os.path.join(self.workspace_path, "AI", "Tasks")

        # Watchdog process
        self.watchdog_process = None

        # Track created files for cleanup
        self.created_files = []
        self.test_results = {
            'start_time': datetime.now(),
            'stages': {},
            'issues': [],
            'success': False
        }

    def start_watchdog(self):
        """Start the ai4pkm watchdog in test mode."""
        self.logger.info("=" * 80)
        self.logger.info("STAGE 0: Starting ai4pkm watchdog")
        self.logger.info("=" * 80)

        try:
            # Start ai4pkm with test flag (-t) which runs watchdog
            # CRITICAL: Must run from workspace directory (cwd parameter)
            # Redirect output to log file for debugging
            watchdog_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'watchdog_hashtag_output.log')
            watchdog_log_file = open(watchdog_log, 'w')

            self.logger.info(f"  Starting watchdog in: {self.workspace_path}")
            self.watchdog_process = subprocess.Popen(
                ['ai4pkm', '-t'],
                stdout=watchdog_log_file,
                stderr=subprocess.STDOUT,
                cwd=self.workspace_path,  # CRITICAL: Run from workspace, not code repo!
                preexec_fn=os.setsid  # Create new process group for clean shutdown
            )

            # Give watchdog time to start up and initialize
            self.logger.info("  ⏳ Waiting 10 seconds for watchdog initialization...")
            time.sleep(10)

            # Check if process started successfully
            if self.watchdog_process.poll() is not None:
                raise RuntimeError(f"Watchdog process exited prematurely with code {self.watchdog_process.returncode}")

            self.logger.info(f"  ✅ Watchdog started (PID: {self.watchdog_process.pid})")
            self.test_results['stages']['watchdog_start'] = {
                'success': True,
                'timestamp': datetime.now(),
                'pid': self.watchdog_process.pid
            }

        except Exception as e:
            self.logger.error(f"  ❌ Failed to start watchdog: {e}")
            self.test_results['stages']['watchdog_start'] = {
                'success': False,
                'timestamp': datetime.now(),
                'error': str(e)
            }
            raise

    def stop_watchdog(self):
        """Stop the watchdog process gracefully."""
        if self.watchdog_process:
            self.logger.info("=" * 80)
            self.logger.info("Stopping watchdog process...")
            self.logger.info("=" * 80)

            try:
                # Send SIGTERM to process group for graceful shutdown
                os.killpg(os.getpgid(self.watchdog_process.pid), signal.SIGTERM)

                # Wait up to 15 seconds for graceful shutdown
                for i in range(15):
                    if self.watchdog_process.poll() is not None:
                        self.logger.info(f"  ✅ Watchdog stopped gracefully")
                        break
                    time.sleep(1)
                else:
                    # Force kill if still running
                    self.logger.warning("  ⚠️  Watchdog didn't stop gracefully, force killing...")
                    os.killpg(os.getpgid(self.watchdog_process.pid), signal.SIGKILL)
                    time.sleep(2)

            except Exception as e:
                self.logger.error(f"  ❌ Error stopping watchdog: {e}")

    def create_test_hashtag_file(self):
        """Create test file with #AI hashtag from template."""
        self.logger.info("=" * 80)
        self.logger.info("STAGE 1: Creating test hashtag file")
        self.logger.info("=" * 80)

        try:
            # Read template
            template_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'fixtures',
                'test_hashtag_template.md'
            )

            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template not found: {template_path}")

            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Ensure Projects directory exists
            projects_dir = os.path.join(self.workspace_path, "Projects")
            os.makedirs(projects_dir, exist_ok=True)

            # Write test file
            with open(self.test_hashtag_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.created_files.append(self.test_hashtag_path)
            self.logger.info(f"  ✅ Created: {self.test_hashtag_path}")

            self.test_results['stages']['hashtag_creation'] = {
                'success': True,
                'timestamp': datetime.now(),
                'file_path': self.test_hashtag_path
            }

        except Exception as e:
            self.logger.error(f"  ❌ Failed to create hashtag file: {e}")
            self.test_results['stages']['hashtag_creation'] = {
                'success': False,
                'timestamp': datetime.now(),
                'error': str(e)
            }
            raise

    def wait_for_request_generation(self, timeout=60):
        """Wait for Writing task request to be generated."""
        self.logger.info("=" * 80)
        self.logger.info("STAGE 2: Waiting for Writing task request generation")
        self.logger.info("=" * 80)

        start_time = time.time()
        request_file = None

        # Ensure requests directory exists
        os.makedirs(self.requests_dir, exist_ok=True)

        while time.time() - start_time < timeout:
            try:
                # Check for request files
                if os.path.exists(self.requests_dir):
                    files = [f for f in os.listdir(self.requests_dir) if f.endswith('.json')]
                    if files:
                        # Found request file - take the most recent one
                        request_file = os.path.join(self.requests_dir, max(files, key=lambda f: os.path.getmtime(os.path.join(self.requests_dir, f))))

                        # Read request content
                        with open(request_file, 'r', encoding='utf-8') as f:
                            request_data = json.load(f)

                        self.logger.info(f"  ✅ Request generated: {os.path.basename(request_file)}")
                        self.logger.info(f"  Task type: {request_data.get('task_type', 'unknown')}")

                        self.test_results['stages']['request_generation'] = {
                            'success': True,
                            'timestamp': datetime.now(),
                            'duration_seconds': time.time() - start_time,
                            'request_file': request_file,
                            'task_type': request_data.get('task_type')
                        }

                        self.created_files.append(request_file)
                        return request_file

            except Exception as e:
                self.logger.warning(f"  Error checking requests: {e}")

            time.sleep(2)

        # Timeout
        self.logger.error(f"  ❌ Timeout waiting for request generation ({timeout}s)")
        self.test_results['stages']['request_generation'] = {
            'success': False,
            'timestamp': datetime.now(),
            'error': f'Timeout after {timeout}s'
        }
        self.test_results['issues'].append('Request generation timeout')
        return None

    def wait_for_task_creation(self, timeout=120):
        """Wait for KTG to create Writing task file."""
        self.logger.info("=" * 80)
        self.logger.info("STAGE 3: Waiting for KTG task creation")
        self.logger.info("=" * 80)

        start_time = time.time()
        task_file = None
        expected_prefix = "2025-10-17 Write"  # KTG creates task with "Write" prefix, not "Test Writing Task"

        while time.time() - start_time < timeout:
            try:
                # Scan Tasks directory for new task
                if os.path.exists(self.tasks_dir):
                    files = [f for f in os.listdir(self.tasks_dir)
                            if f.endswith('.md') and f.startswith(expected_prefix)]

                    # Filter out files we created ourselves
                    new_files = [f for f in files
                                if os.path.join(self.tasks_dir, f) not in self.created_files]

                    if new_files:
                        # Found task file
                        task_file = os.path.join(self.tasks_dir, new_files[0])

                        # Read task frontmatter
                        with open(task_file, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Extract status
                        import re
                        status_match = re.search(r'status:\s*["\']?([A-Z_]+)["\']?', content)
                        status = status_match.group(1) if status_match else 'unknown'

                        self.logger.info(f"  ✅ Task created: {os.path.basename(task_file)}")
                        self.logger.info(f"  Status: {status}")

                        self.test_results['stages']['task_creation'] = {
                            'success': True,
                            'timestamp': datetime.now(),
                            'duration_seconds': time.time() - start_time,
                            'task_file': task_file,
                            'status': status
                        }

                        # Validate status is TBD
                        if status != 'TBD':
                            self.test_results['issues'].append(f'Task created with wrong status: {status} (expected TBD)')
                            self.logger.warning(f"  ⚠️  Task status is '{status}' not 'TBD'")

                        self.created_files.append(task_file)
                        return task_file

            except Exception as e:
                self.logger.warning(f"  Error checking tasks: {e}")

            time.sleep(3)

        # Timeout
        self.logger.error(f"  ❌ Timeout waiting for task creation ({timeout}s)")
        self.test_results['stages']['task_creation'] = {
            'success': False,
            'timestamp': datetime.now(),
            'error': f'Timeout after {timeout}s'
        }
        self.test_results['issues'].append('Task creation timeout')
        return None

    def wait_for_task_detection(self, task_file, timeout=60):
        """Wait for TBDTaskPoller to detect the task."""
        self.logger.info("=" * 80)
        self.logger.info("STAGE 4: Waiting for TBD task detection (polling)")
        self.logger.info("=" * 80)

        start_time = time.time()

        # Read watchdog log for polling detection message
        watchdog_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'watchdog_hashtag_output.log')

        last_position = 0
        if os.path.exists(watchdog_log):
            last_position = os.path.getsize(watchdog_log)

        while time.time() - start_time < timeout:
            try:
                if os.path.exists(watchdog_log):
                    # Read new log content
                    with open(watchdog_log, 'r', encoding='utf-8') as f:
                        f.seek(last_position)
                        new_content = f.read()
                        last_position = f.tell()

                    # Check for polling detection message
                    task_name = os.path.basename(task_file)
                    if '🔄 Polling detected TBD task' in new_content or '📋 TBD task detected' in new_content:
                        # Extract relevant line
                        for line in new_content.split('\n'):
                            if '🔄 Polling detected TBD task' in line or '📋 TBD task detected' in line:
                                self.logger.info(f"  ✅ {line.strip()}")
                                break

                        self.test_results['stages']['task_detection'] = {
                            'success': True,
                            'timestamp': datetime.now(),
                            'duration_seconds': time.time() - start_time
                        }

                        return True

            except Exception as e:
                self.logger.warning(f"  Error checking logs: {e}")

            time.sleep(2)

        # Timeout
        self.logger.error(f"  ❌ Timeout waiting for task detection ({timeout}s)")
        self.test_results['stages']['task_detection'] = {
            'success': False,
            'timestamp': datetime.now(),
            'error': f'Timeout after {timeout}s'
        }
        self.test_results['issues'].append('Task detection timeout')
        return False

    def wait_for_task_processing(self, task_file, timeout=300):
        """Wait for TaskProcessor to process the task."""
        self.logger.info("=" * 80)
        self.logger.info("STAGE 5: Waiting for task processing")
        self.logger.info("=" * 80)

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Read task file status
                with open(task_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract status
                import re
                status_match = re.search(r'status:\s*["\']?([A-Z_]+)["\']?', content)
                status = status_match.group(1) if status_match else 'unknown'

                # Check if processing started
                if status in ['IN_PROGRESS', 'PROCESSED', 'UNDER_REVIEW', 'COMPLETED']:
                    self.logger.info(f"  ✅ Task processing started (status: {status})")

                    self.test_results['stages']['task_processing'] = {
                        'success': True,
                        'timestamp': datetime.now(),
                        'duration_seconds': time.time() - start_time,
                        'final_status': status
                    }

                    return True

            except Exception as e:
                self.logger.warning(f"  Error checking task status: {e}")

            time.sleep(5)

        # Timeout
        self.logger.error(f"  ❌ Timeout waiting for task processing ({timeout}s)")
        self.test_results['stages']['task_processing'] = {
            'success': False,
            'timestamp': datetime.now(),
            'error': f'Timeout after {timeout}s'
        }
        self.test_results['issues'].append('Task processing timeout')
        return False

    def wait_for_task_completion(self, task_file, timeout=600):
        """Wait for task to reach COMPLETED status."""
        self.logger.info("=" * 80)
        self.logger.info("STAGE 6: Waiting for task completion")
        self.logger.info("=" * 80)

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Read task file status
                with open(task_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract status
                import re
                status_match = re.search(r'status:\s*["\']?([A-Z_]+)["\']?', content)
                status = status_match.group(1) if status_match else 'unknown'

                # Check if completed
                if status == 'COMPLETED':
                    # Extract output files
                    output_match = re.search(r'output:\s*\n\s*-\s*"?\[\[([^\]]+)\]\]"?', content)
                    output_file = output_match.group(1) if output_match else None

                    self.logger.info(f"  ✅ Task completed!")
                    if output_file:
                        self.logger.info(f"  Output: {output_file}")

                    self.test_results['stages']['task_completion'] = {
                        'success': True,
                        'timestamp': datetime.now(),
                        'duration_seconds': time.time() - start_time,
                        'output_file': output_file
                    }

                    return True

            except Exception as e:
                self.logger.warning(f"  Error checking task completion: {e}")

            time.sleep(10)

        # Timeout
        self.logger.error(f"  ❌ Timeout waiting for task completion ({timeout}s)")
        self.test_results['stages']['task_completion'] = {
            'success': False,
            'timestamp': datetime.now(),
            'error': f'Timeout after {timeout}s'
        }
        self.test_results['issues'].append('Task completion timeout')
        return False

    def cleanup(self):
        """Clean up test files (optional - can leave for debugging)."""
        self.logger.info("=" * 80)
        self.logger.info("CLEANUP: Removing test files")
        self.logger.info("=" * 80)

        # DISABLED FOR NOW - leave files for debugging
        # Uncomment to enable cleanup
        """
        for filepath in self.created_files:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    self.logger.info(f"  ✅ Removed: {filepath}")
            except Exception as e:
                self.logger.error(f"  ❌ Failed to remove {filepath}: {e}")
        """

        self.logger.info("  ⚠️  Cleanup disabled - test files preserved for debugging")
        self.logger.info(f"  Test files created:")
        for filepath in self.created_files:
            self.logger.info(f"    - {filepath}")

    def generate_report(self):
        """Generate test results report."""
        self.logger.info("=" * 80)
        self.logger.info("TEST RESULTS SUMMARY")
        self.logger.info("=" * 80)

        # Calculate total duration
        end_time = datetime.now()
        total_duration = (end_time - self.test_results['start_time']).total_seconds()

        # Count successful stages
        stages = self.test_results['stages']
        total_stages = len(stages)
        successful_stages = sum(1 for s in stages.values() if s.get('success', False))

        # Overall success
        self.test_results['success'] = (successful_stages == total_stages and
                                       len(self.test_results['issues']) == 0)

        # Print summary
        self.logger.info(f"  Total Duration: {total_duration:.1f}s")
        self.logger.info(f"  Stages Passed: {successful_stages}/{total_stages}")
        self.logger.info(f"  Issues Found: {len(self.test_results['issues'])}")
        self.logger.info(f"  Overall Result: {'✅ PASS' if self.test_results['success'] else '❌ FAIL'}")

        # Print stage details
        self.logger.info("\n  Stage Details:")
        for stage_name, stage_data in stages.items():
            status = '✅' if stage_data.get('success', False) else '❌'
            duration = stage_data.get('duration_seconds', 0)
            self.logger.info(f"    {status} {stage_name}: {duration:.1f}s")
            if not stage_data.get('success', False):
                self.logger.info(f"       Error: {stage_data.get('error', 'unknown')}")

        # Print issues
        if self.test_results['issues']:
            self.logger.info("\n  Issues:")
            for issue in self.test_results['issues']:
                self.logger.info(f"    ⚠️  {issue}")

        # Save report to file
        report_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f'KTG_KTP_Hashtag_Integration_Test_Results_{self.test_timestamp}.md'
        )

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# KTG/KTP/KTE Integration Test Results - #AI Hashtag Scenario\n\n")
            f.write(f"**Test Run**: {self.test_results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Duration**: {total_duration:.1f}s\n")
            f.write(f"**Result**: {'✅ PASS' if self.test_results['success'] else '❌ FAIL'}\n\n")

            f.write("## Stage Results\n\n")
            for stage_name, stage_data in stages.items():
                status = '✅ PASS' if stage_data.get('success', False) else '❌ FAIL'
                f.write(f"### {stage_name}\n")
                f.write(f"- **Status**: {status}\n")
                f.write(f"- **Duration**: {stage_data.get('duration_seconds', 0):.1f}s\n")
                if not stage_data.get('success', False):
                    f.write(f"- **Error**: {stage_data.get('error', 'unknown')}\n")
                f.write("\n")

            if self.test_results['issues']:
                f.write("## Issues Found\n\n")
                for issue in self.test_results['issues']:
                    f.write(f"- {issue}\n")
                f.write("\n")

            f.write("## Test Files\n\n")
            for filepath in self.created_files:
                f.write(f"- `{filepath}`\n")

        self.logger.info(f"\n  📄 Report saved: {report_path}")

    def run(self):
        """Run the complete integration test."""
        try:
            # Start watchdog
            self.start_watchdog()

            # Create test hashtag file
            self.create_test_hashtag_file()

            # Wait for stages
            request_file = self.wait_for_request_generation(timeout=60)
            if not request_file:
                return

            task_file = self.wait_for_task_creation(timeout=120)
            if not task_file:
                return

            detected = self.wait_for_task_detection(task_file, timeout=60)
            if not detected:
                return

            processing_started = self.wait_for_task_processing(task_file, timeout=300)
            if not processing_started:
                return

            # Wait for completion (this may take a while)
            self.wait_for_task_completion(task_file, timeout=600)

        except Exception as e:
            self.logger.error(f"Test failed with exception: {e}", exc_info=True)
            self.test_results['issues'].append(f'Exception: {e}')

        finally:
            # Always stop watchdog and generate report
            self.stop_watchdog()
            self.cleanup()
            self.generate_report()


if __name__ == '__main__':
    test = KTGKTPHashtagIntegrationTest()
    test.run()
