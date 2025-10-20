"""Integration test for KTG/KTP/KTE workflow - EIC scenario.

This test simulates the complete end-to-end workflow:
1. Starts ai4pkm watchdog in test mode
2. Creates test clipping file
3. Monitors: File Watchdog → Task Request → KTG → KTP → KTE
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


class KTGKTPIntegrationTest:
    """Integration test for KTG/KTP/KTE EIC workflow."""

    def __init__(self):
        """Initialize test environment."""
        self.logger = Logger(console_output=True)

        # IMPORTANT: Use the AI4PKM repo as test workspace, NOT production vault!
        # The repo has the same folder structure (AI/, Ingest/, etc.) for testing
        self.repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.workspace_path = self.repo_root

        # Config must be loaded from workspace
        self.config = Config(config_file=os.path.join(self.workspace_path, 'ai4pkm_cli.json'))

        # Validate workspace has required folders
        required_folders = ['AI/Tasks', 'Ingest/Clippings', '_Settings_/Prompts']
        for folder in required_folders:
            full_path = os.path.join(self.workspace_path, folder)
            if not os.path.exists(full_path):
                raise ValueError(f"Invalid test workspace: {full_path} does not exist")

        self.logger.info(f"Using test workspace: {self.workspace_path}")

        # Test file paths
        self.test_timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        self.test_clipping_name = f"2025-10-17 Test Integration Article {self.test_timestamp}.md"
        self.test_clipping_path = os.path.join(
            self.workspace_path,
            "Ingest",
            "Clippings",
            self.test_clipping_name
        )

        # Paths to monitor
        self.requests_dir = os.path.join(self.workspace_path, "AI", "Tasks", "Requests", "Clipping")  # Note: singular!
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
            watchdog_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'watchdog_output.log')
            watchdog_log_file = open(watchdog_log, 'w')

            self.logger.info(f"  Starting watchdog in: {self.workspace_path}")
            self.watchdog_process = subprocess.Popen(
                ['ai4pkm', '-t'],
                stdout=watchdog_log_file,
                stderr=subprocess.STDOUT,
                cwd=self.workspace_path,  # CRITICAL: Run from workspace, not code repo!
                text=True
            )

            # Store log file handle for cleanup
            self.watchdog_log_file = watchdog_log_file
            self.watchdog_log_path = watchdog_log

            # Give watchdog time to initialize and start monitoring
            self.logger.info("  Waiting for watchdog to initialize...")
            time.sleep(10)  # Increased wait time for full initialization

            # Check if process is still running
            if self.watchdog_process.poll() is not None:
                watchdog_log_file.close()
                with open(watchdog_log, 'r') as f:
                    output = f.read()
                self.logger.error(f"✗ Watchdog failed to start")
                self.logger.error(f"Output:\n{output}")
                self.test_results['issues'].append("Watchdog failed to start")
                return False

            self.logger.info(f"✓ Watchdog started (PID: {self.watchdog_process.pid})")
            self.logger.info(f"  Log file: {watchdog_log}")

            # Show first few lines of watchdog output
            time.sleep(1)
            watchdog_log_file.flush()
            try:
                with open(watchdog_log, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        self.logger.info("  Watchdog output (first 10 lines):")
                        for line in lines[:10]:
                            self.logger.info(f"    {line.rstrip()}")
            except Exception as e:
                self.logger.warning(f"  Could not read watchdog output: {e}")

            self.test_results['stages']['watchdog_started'] = {
                'success': True,
                'timestamp': datetime.now(),
                'pid': self.watchdog_process.pid,
                'log_file': watchdog_log
            }
            return True

        except Exception as e:
            self.logger.error(f"✗ Failed to start watchdog: {e}")
            self.test_results['issues'].append(f"Watchdog start failed: {e}")
            return False

    def stop_watchdog(self):
        """Stop the ai4pkm watchdog."""
        if self.watchdog_process:
            self.logger.info("\nStopping watchdog...")
            try:
                # Send SIGTERM for graceful shutdown
                self.watchdog_process.send_signal(signal.SIGTERM)

                # Wait up to 5 seconds for graceful shutdown
                try:
                    self.watchdog_process.wait(timeout=5)
                    self.logger.info("✓ Watchdog stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't stop
                    self.logger.warning("Watchdog didn't stop gracefully, forcing...")
                    self.watchdog_process.kill()
                    self.watchdog_process.wait()
                    self.logger.info("✓ Watchdog force-stopped")

                # Close log file
                if hasattr(self, 'watchdog_log_file'):
                    self.watchdog_log_file.close()

            except Exception as e:
                self.logger.error(f"Error stopping watchdog: {e}")

    def create_test_clipping(self):
        """Create a test clipping file to trigger the workflow."""
        self.logger.info("=" * 80)
        self.logger.info("STAGE 1: Creating test clipping file")
        self.logger.info("=" * 80)

        # Read template from fixtures folder
        template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'fixtures',
            'test_clipping_template.md'
        )

        try:
            # Read template content
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            self.logger.error(f"✗ Template file not found: {template_path}")
            self.test_results['issues'].append(f"Template file not found: {template_path}")
            return False

        try:
            os.makedirs(os.path.dirname(self.test_clipping_path), exist_ok=True)

            with open(self.test_clipping_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Ensure file is flushed to disk
            os.sync() if hasattr(os, 'sync') else None

            self.created_files.append(self.test_clipping_path)

            self.logger.info(f"✓ Created test clipping: {self.test_clipping_path}")
            self.logger.info(f"  File size: {os.path.getsize(self.test_clipping_path)} bytes")

            # Give watchdog a moment to detect the file
            time.sleep(2)
            self.test_results['stages']['clipping_created'] = {
                'success': True,
                'timestamp': datetime.now(),
                'file': self.test_clipping_path
            }
            return True

        except Exception as e:
            self.logger.error(f"✗ Failed to create test clipping: {e}")
            self.test_results['issues'].append(f"Clipping creation failed: {e}")
            return False

    def wait_for_task_request(self, timeout=60):
        """Wait for task request file to be created by ClippingFileHandler.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            Path to task request file if found, None otherwise
        """
        self.logger.info("\n" + "=" * 80)
        self.logger.info("STAGE 2: Waiting for task request creation")
        self.logger.info("=" * 80)

        start_time = time.time()
        request_file = None

        while time.time() - start_time < timeout:
            if os.path.exists(self.requests_dir):
                # Look for JSON files created after test start
                for filename in os.listdir(self.requests_dir):
                    if not filename.endswith('.json'):
                        continue

                    filepath = os.path.join(self.requests_dir, filename)

                    # Check if file was created after test started
                    file_mtime = os.path.getmtime(filepath)
                    if file_mtime > self.test_results['start_time'].timestamp():
                        # Verify it's for our test file
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if self.test_clipping_name in data.get('target_file', ''):
                                    request_file = filepath
                                    self.created_files.append(filepath)
                                    break
                        except Exception as e:
                            self.logger.warning(f"Could not read request file {filepath}: {e}")

            if request_file:
                break

            time.sleep(1)

        if request_file:
            self.logger.info(f"✓ Task request created: {request_file}")
            self.logger.info(f"  Time elapsed: {time.time() - start_time:.1f}s")

            # Read and log content
            try:
                with open(request_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logger.info(f"  Task type: {data.get('task_type')}")
                    self.logger.info(f"  Handler: {data.get('handler')}")
                    self.logger.info(f"  Target: {data.get('target_file')}")
            except Exception as e:
                self.logger.warning(f"Could not parse request file: {e}")

            self.test_results['stages']['task_request_created'] = {
                'success': True,
                'timestamp': datetime.now(),
                'file': request_file,
                'elapsed_seconds': time.time() - start_time
            }
        else:
            self.logger.error(f"✗ Task request not created within {timeout}s")
            self.test_results['issues'].append(f"Task request not created within {timeout}s")
            self.test_results['stages']['task_request_created'] = {
                'success': False,
                'timestamp': datetime.now()
            }

        return request_file

    def wait_for_task_file(self, timeout=90):
        """Wait for KTG to create the task file.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            Path to task file if found, None otherwise
        """
        self.logger.info("\n" + "=" * 80)
        self.logger.info("STAGE 3: Waiting for KTG task file creation")
        self.logger.info("=" * 80)

        start_time = time.time()
        task_file = None

        # Pattern to match: AI/Tasks/2025-10-17 [anything].md
        date_prefix = "2025-10-17"

        while time.time() - start_time < timeout:
            if os.path.exists(self.tasks_dir):
                for filename in os.listdir(self.tasks_dir):
                    if not filename.endswith('.md'):
                        continue
                    if not filename.startswith(date_prefix):
                        continue
                    if 'Test Integration' not in filename and 'test integration' not in filename.lower():
                        continue

                    filepath = os.path.join(self.tasks_dir, filename)

                    # Check if file was created after test started
                    file_mtime = os.path.getmtime(filepath)
                    if file_mtime > self.test_results['start_time'].timestamp():
                        task_file = filepath
                        self.created_files.append(filepath)
                        break

            if task_file:
                break

            time.sleep(2)

        if task_file:
            self.logger.info(f"✓ Task file created: {os.path.basename(task_file)}")
            self.logger.info(f"  Time elapsed: {time.time() - start_time:.1f}s")

            # Read and validate frontmatter
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Check for required properties
                    required_props = ['priority', 'status', 'task_type', 'source']
                    missing_props = [prop for prop in required_props if prop not in content.lower()]

                    if missing_props:
                        self.logger.warning(f"  Missing properties: {', '.join(missing_props)}")
                        self.test_results['issues'].append(f"Task missing properties: {missing_props}")
                    else:
                        self.logger.info(f"  ✓ All required properties present")
            except Exception as e:
                self.logger.warning(f"Could not validate task file: {e}")

            self.test_results['stages']['task_created'] = {
                'success': True,
                'timestamp': datetime.now(),
                'file': task_file,
                'elapsed_seconds': time.time() - start_time
            }
        else:
            self.logger.error(f"✗ Task file not created within {timeout}s")
            self.test_results['issues'].append(f"Task file not created within {timeout}s")
            self.test_results['stages']['task_created'] = {
                'success': False,
                'timestamp': datetime.now()
            }

        return task_file

    def monitor_task_processing(self, task_file, timeout=300):
        """Monitor task file for status changes through KTP workflow.

        Args:
            task_file: Path to task file
            timeout: Maximum seconds to wait for completion

        Returns:
            True if task completed successfully, False otherwise
        """
        self.logger.info("\n" + "=" * 80)
        self.logger.info("STAGE 4: Monitoring KTP task processing")
        self.logger.info("=" * 80)

        start_time = time.time()
        last_status = None
        status_history = []

        while time.time() - start_time < timeout:
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Extract status (simple regex)
                    import re
                    status_match = re.search(r'status:\s*["\']?(\w+)["\']?', content, re.IGNORECASE)

                    if status_match:
                        current_status = status_match.group(1)

                        if current_status != last_status:
                            self.logger.info(f"  Status changed: {last_status or 'None'} → {current_status}")
                            status_history.append({
                                'status': current_status,
                                'timestamp': datetime.now(),
                                'elapsed': time.time() - start_time
                            })
                            last_status = current_status

                        # Check for completion
                        if current_status in ['COMPLETED', 'FAILED', 'NEEDS_INPUT']:
                            self.logger.info(f"✓ Task reached terminal status: {current_status}")

                            # Validate output if COMPLETED
                            if current_status == 'COMPLETED':
                                output_match = re.search(r'output:\s*["\']?\[\[([^\]]+)\]\]["\']?', content, re.IGNORECASE)
                                if output_match:
                                    self.logger.info(f"  ✓ Output file specified: {output_match.group(1)}")
                                else:
                                    self.logger.warning(f"  ⚠ No output file specified")
                                    self.test_results['issues'].append("No output file specified in completed task")

                            self.test_results['stages']['task_processing'] = {
                                'success': current_status == 'COMPLETED',
                                'timestamp': datetime.now(),
                                'final_status': current_status,
                                'status_history': status_history,
                                'total_seconds': time.time() - start_time
                            }

                            return current_status == 'COMPLETED'

            except Exception as e:
                self.logger.warning(f"Error reading task file: {e}")

            time.sleep(5)

        self.logger.error(f"✗ Task did not complete within {timeout}s")
        self.logger.error(f"  Last status: {last_status}")
        self.test_results['issues'].append(f"Task timeout after {timeout}s, status: {last_status}")
        self.test_results['stages']['task_processing'] = {
            'success': False,
            'timestamp': datetime.now(),
            'final_status': last_status,
            'status_history': status_history
        }

        return False

    def check_for_duplicates(self):
        """Check if any duplicate tasks were created."""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("VALIDATION: Checking for duplicate tasks")
        self.logger.info("=" * 80)

        # Look for tasks with similar names created during test
        test_tasks = []
        date_prefix = "2025-10-17"

        if os.path.exists(self.tasks_dir):
            for filename in os.listdir(self.tasks_dir):
                if not filename.endswith('.md'):
                    continue
                if not filename.startswith(date_prefix):
                    continue
                if 'Test Integration' not in filename and 'test integration' not in filename.lower():
                    continue

                filepath = os.path.join(self.tasks_dir, filename)
                file_mtime = os.path.getmtime(filepath)

                if file_mtime > self.test_results['start_time'].timestamp():
                    test_tasks.append(filename)

        if len(test_tasks) == 0:
            self.logger.warning("⚠ No test tasks found")
            return False
        elif len(test_tasks) == 1:
            self.logger.info(f"✓ Exactly one task created (no duplicates)")
            return True
        else:
            self.logger.error(f"✗ Multiple tasks created: {len(test_tasks)}")
            for task in test_tasks:
                self.logger.error(f"  - {task}")
            self.test_results['issues'].append(f"Duplicate tasks created: {test_tasks}")
            return False

    def cleanup(self):
        """Clean up all test artifacts and stop watchdog."""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("CLEANUP: Stopping watchdog and removing test artifacts")
        self.logger.info("=" * 80)

        # Stop watchdog first
        self.stop_watchdog()

        cleaned = 0
        failed = 0

        for filepath in reversed(self.created_files):  # Reverse to delete files before dirs
            try:
                if os.path.exists(filepath):
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                        self.logger.info(f"✓ Deleted: {filepath}")
                        cleaned += 1
                    elif os.path.isdir(filepath):
                        shutil.rmtree(filepath)
                        self.logger.info(f"✓ Deleted directory: {filepath}")
                        cleaned += 1
            except Exception as e:
                self.logger.error(f"✗ Failed to delete {filepath}: {e}")
                failed += 1

        self.logger.info(f"\nCleanup summary: {cleaned} deleted, {failed} failed")

        self.test_results['cleanup'] = {
            'files_deleted': cleaned,
            'files_failed': failed
        }

    def generate_report(self):
        """Generate test results report."""
        self.test_results['end_time'] = datetime.now()
        self.test_results['total_duration'] = (
            self.test_results['end_time'] - self.test_results['start_time']
        ).total_seconds()

        # Determine overall success
        self.test_results['success'] = (
            len(self.test_results['issues']) == 0 and
            all(stage.get('success', False) for stage in self.test_results['stages'].values())
        )

        report = f"""
{'=' * 80}
KTG/KTP/KTE INTEGRATION TEST RESULTS
{'=' * 80}

Test Start: {self.test_results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}
Test End:   {self.test_results['end_time'].strftime('%Y-%m-%d %H:%M:%S')}
Duration:   {self.test_results['total_duration']:.1f}s

Overall Result: {'✓ PASSED' if self.test_results['success'] else '✗ FAILED'}

{'=' * 80}
STAGE RESULTS
{'=' * 80}
"""

        for stage_name, stage_data in self.test_results['stages'].items():
            status = '✓ PASSED' if stage_data.get('success') else '✗ FAILED'
            report += f"\n{stage_name.upper()}: {status}\n"

            if 'elapsed_seconds' in stage_data:
                report += f"  Time: {stage_data['elapsed_seconds']:.1f}s\n"

            if 'file' in stage_data:
                report += f"  File: {stage_data['file']}\n"

            if 'status_history' in stage_data:
                report += f"  Status transitions:\n"
                for status in stage_data['status_history']:
                    report += f"    - {status['status']} at {status['elapsed']:.1f}s\n"

        if self.test_results['issues']:
            report += f"\n{'=' * 80}\n"
            report += f"ISSUES FOUND ({len(self.test_results['issues'])})\n"
            report += f"{'=' * 80}\n"
            for i, issue in enumerate(self.test_results['issues'], 1):
                report += f"{i}. {issue}\n"

        report += f"\n{'=' * 80}\n"

        return report

    def run(self):
        """Run the complete integration test."""
        self.logger.info("\n\n")
        self.logger.info("*" * 80)
        self.logger.info("*" + " " * 78 + "*")
        self.logger.info("*" + " " * 20 + "KTG/KTP/KTE INTEGRATION TEST" + " " * 30 + "*")
        self.logger.info("*" + " " * 78 + "*")
        self.logger.info("*" * 80)
        self.logger.info("\n")

        try:
            # Stage 0: Start watchdog
            if not self.start_watchdog():
                return False

            # Stage 1: Create test clipping
            if not self.create_test_clipping():
                return False

            # Stage 2: Wait for task request
            request_file = self.wait_for_task_request(timeout=30)
            if not request_file:
                return False

            # Stage 3: Wait for task file
            task_file = self.wait_for_task_file(timeout=60)
            if not task_file:
                return False

            # Stage 4: Monitor task processing
            success = self.monitor_task_processing(task_file, timeout=300)

            # Validation: Check for duplicates
            no_duplicates = self.check_for_duplicates()

            if not no_duplicates:
                self.test_results['success'] = False

            return success

        finally:
            # Stop watchdog but DON'T clean up files yet for debugging
            self.stop_watchdog()

            # Generate and print report BEFORE cleanup so we can inspect files
            report = self.generate_report()
            self.logger.info(report)

            # Save report to file
            test_dir = os.path.dirname(os.path.abspath(__file__))
            report_path = os.path.join(test_dir, 'KTG_KTP_Integration_Test_Results.md')
            log_path = os.path.join(test_dir, 'integration_test.log')

            try:
                # Save markdown report
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(f"# KTG/KTP/KTE Integration Test Results\n\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(report)

                self.logger.info(f"\n✓ Test report saved to: {report_path}")

                # Also save full test log
                if os.path.exists('/tmp/integration_test.log'):
                    shutil.copy('/tmp/integration_test.log', log_path)
                    self.logger.info(f"✓ Test log saved to: {log_path}")

            except Exception as e:
                self.logger.error(f"✗ Failed to save report/log: {e}")

            # Note: Files left for inspection - manually clean up with:
            # rm AI/Tasks/2025-10-17*.md Ingest/Clippings/2025-10-17*.md
            self.logger.info("\n⚠️  Test artifacts left for debugging - clean up manually")


if __name__ == '__main__':
    test = KTGKTPIntegrationTest()
    success = test.run()
    sys.exit(0 if success else 1)
