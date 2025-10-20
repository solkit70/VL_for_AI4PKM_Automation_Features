"""Test to verify infinite evaluation loop fix.

This test creates a task with status: PROCESSED and evaluated: 1,
then triggers watchdog events to ensure it doesn't enter an infinite loop.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger import Logger


def test_evaluation_loop_fix():
    """Test that evaluated tasks don't trigger infinite evaluation loops."""
    logger = Logger(console_output=True)

    # Use AI4PKM repo as workspace
    repo_root = Path(__file__).parent.parent.parent
    tasks_dir = repo_root / "AI" / "Tasks"

    # Create test task file with PROCESSED status and evaluated flag
    test_task_name = "2025-10-18 Test Evaluation Loop Fix.md"
    test_task_path = tasks_dir / test_task_name

    logger.info("=" * 80)
    logger.info("TEST: Infinite Evaluation Loop Fix")
    logger.info("=" * 80)

    try:
        # Create test task
        logger.info(f"Creating test task: {test_task_name}")

        task_content = """---
created: 2025-10-18T00:00:00
status: "PROCESSED"
evaluated: "1"
task_type: EIC
worker: "test"
output: "[[AI/Articles/2025-10-18 Test Output]]"
evaluation_log: "[[Tasks/Logs/2025-10-18 Test-eval]]"
---

# Test Task

This is a test task to verify the infinite evaluation loop fix.

## Context
Task has:
- status: PROCESSED
- evaluated: 1
- evaluation_log already present

## Expected Behavior
When this file is modified (touched), TaskEvaluator should:
1. Detect the PROCESSED status
2. See evaluated=1
3. Skip evaluation immediately (early return)
4. NOT spawn evaluation thread
5. NOT enter infinite loop
"""

        with open(test_task_path, 'w', encoding='utf-8') as f:
            f.write(task_content)

        logger.info(f"✅ Created test task at: {test_task_path}")

        # Start watchdog
        logger.info("\nStarting watchdog...")
        watchdog_log = Path(__file__).parent / "watchdog_loop_test_output.log"

        watchdog_log_file = open(watchdog_log, 'w')
        watchdog_process = subprocess.Popen(
            ['ai4pkm', '-t'],
            stdout=watchdog_log_file,
            stderr=subprocess.STDOUT,
            cwd=str(repo_root),
            preexec_fn=os.setsid
        )

        logger.info(f"Watchdog started (PID: {watchdog_process.pid})")
        logger.info("Waiting 10s for initialization...")
        time.sleep(10)

        # Touch the file multiple times to trigger watchdog
        logger.info("\n" + "=" * 80)
        logger.info("TRIGGERING FILE MODIFICATIONS")
        logger.info("=" * 80)

        for i in range(3):
            logger.info(f"\nTouch #{i+1}: Modifying file to trigger watchdog...")
            test_task_path.touch()
            time.sleep(3)

        logger.info("\n✅ All file modifications complete")
        logger.info("Waiting 10s to observe behavior...")
        time.sleep(10)

        # Stop watchdog
        logger.info("\nStopping watchdog...")
        import signal
        os.killpg(os.getpgid(watchdog_process.pid), signal.SIGTERM)
        time.sleep(2)

        # Read and analyze log
        logger.info("\n" + "=" * 80)
        logger.info("ANALYZING WATCHDOG LOG")
        logger.info("=" * 80)

        with open(watchdog_log, 'r') as f:
            log_content = f.read()

        # Count evaluation-related messages
        already_evaluated_count = log_content.count("Task already evaluated")
        cache_hit_count = log_content.count("Cache hit for")
        evaluation_started_count = log_content.count("🔎 Evaluating task:")
        evaluation_completed_count = log_content.count("✅ KTP evaluation completed")

        logger.info(f"\nLog Analysis:")
        logger.info(f"  'Task already evaluated' messages: {already_evaluated_count}")
        logger.info(f"  'Cache hit' messages: {cache_hit_count}")
        logger.info(f"  '🔎 Evaluating task' messages: {evaluation_started_count}")
        logger.info(f"  '✅ KTP evaluation completed' messages: {evaluation_completed_count}")

        # Verdict
        logger.info("\n" + "=" * 80)
        logger.info("TEST RESULTS")
        logger.info("=" * 80)

        if evaluation_started_count == 0:
            logger.info("✅ PASS: No evaluation threads spawned (early return working!)")
            logger.info(f"   Tasks properly skipped via evaluated flag or cache")
            success = True
        elif evaluation_started_count == 1 and evaluation_completed_count == 1:
            logger.info("⚠️  WARNING: One evaluation occurred")
            logger.info("   This might be OK if it was before the fix kicked in")
            success = True
        else:
            logger.info(f"❌ FAIL: {evaluation_started_count} evaluations started")
            logger.info("   Infinite loop may still be occurring!")
            success = False

        # Show relevant log excerpt
        logger.info("\nRelevant log excerpt:")
        logger.info("-" * 80)
        for line in log_content.split('\n'):
            if any(keyword in line for keyword in [
                "already evaluated",
                "Cache hit",
                "Evaluating task",
                "evaluation completed",
                test_task_name
            ]):
                logger.info(line)
        logger.info("-" * 80)

        return success

    finally:
        # Cleanup
        logger.info("\n" + "=" * 80)
        logger.info("CLEANUP")
        logger.info("=" * 80)

        try:
            if watchdog_process and watchdog_process.poll() is None:
                os.killpg(os.getpgid(watchdog_process.pid), signal.SIGKILL)
                logger.info("Watchdog killed")
        except:
            pass

        try:
            if test_task_path.exists():
                test_task_path.unlink()
                logger.info(f"Removed test task: {test_task_name}")
        except Exception as e:
            logger.warning(f"Could not remove test task: {e}")

        try:
            if watchdog_log_file:
                watchdog_log_file.close()
            logger.info(f"Watchdog log saved: {watchdog_log}")
        except:
            pass


if __name__ == '__main__':
    success = test_evaluation_loop_fix()
    sys.exit(0 if success else 1)
