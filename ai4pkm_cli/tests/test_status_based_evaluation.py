"""Test status-based evaluation (no 'evaluated' flag).

This test verifies that evaluation logic uses status as the single source
of truth, and properly handles various status states without relying on
the 'evaluated' flag.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai4pkm_cli.logger import Logger
from ai4pkm_cli.commands.ktp_runner import KTPRunner
from ai4pkm_cli.config import Config


def create_test_task(tasks_dir: Path, task_name: str, status: str, add_evaluated_flag: bool = False) -> Path:
    """Create a test task file with specified status.

    Args:
        tasks_dir: Path to AI/Tasks directory
        task_name: Task filename
        status: Task status (PROCESSED, COMPLETED, etc.)
        add_evaluated_flag: Whether to add old 'evaluated: "1"' flag

    Returns:
        Path to created task file
    """
    task_path = tasks_dir / task_name

    evaluated_line = 'evaluated: "1"' if add_evaluated_flag else ''

    content = f"""---
created: 2025-10-18T00:00:00
status: "{status}"
task_type: EIC
worker: "test"
output: "[[AI/Articles/2025-10-18 Test Output]]"
{evaluated_line}
---

# Test Task: {task_name}

## Context
Testing status-based evaluation logic.

## Requirements
This task is for testing:
- Status: {status}
- Has evaluated flag: {add_evaluated_flag}

## Expected Behavior
- PROCESSED → Should evaluate (will complete to COMPLETED/NEEDS_INPUT/FAILED)
- UNDER_REVIEW → Should skip (already evaluating)
- COMPLETED → Should skip (already done)
- NEEDS_INPUT → Should skip (already done)
- FAILED → Should skip (already done)

Note: Evaluation is a synchronous operation that runs to completion,
so PROCESSED tasks will end up in final status (COMPLETED/NEEDS_INPUT/FAILED)
rather than staying in UNDER_REVIEW intermediate state.
"""

    with open(task_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return task_path


def test_status_based_evaluation():
    """Test that evaluation uses status, not 'evaluated' flag."""
    logger = Logger(console_output=True)

    # Use AI4PKM repo as workspace
    repo_root = Path(__file__).parent.parent.parent
    tasks_dir = repo_root / "AI" / "Tasks"

    logger.info("=" * 80)
    logger.info("TEST: Status-Based Evaluation (No 'evaluated' Flag)")
    logger.info("=" * 80)

    # Create config and runner
    config = Config()
    runner = KTPRunner(logger, config)

    test_results = []
    created_tasks = []

    try:
        # Test 1: PROCESSED task should evaluate
        logger.info("\n" + "=" * 80)
        logger.info("TEST 1: PROCESSED task should evaluate")
        logger.info("=" * 80)

        task1 = create_test_task(tasks_dir, "2025-10-18 Test Status PROCESSED.md", "PROCESSED")
        created_tasks.append(task1)

        logger.info(f"Created task with status: PROCESSED")
        logger.info(f"Calling evaluate_task()...")

        # This should proceed with evaluation (PROCESSED → COMPLETED/NEEDS_INPUT/FAILED)
        runner.evaluate_task(task1.name)

        # Read status after evaluation completes
        with open(task1, 'r') as f:
            content = f.read()

        # Check if status changed from PROCESSED (evaluation ran)
        # Agent may mark as COMPLETED or NEEDS_INPUT depending on output validation
        final_statuses = ['COMPLETED', 'NEEDS_INPUT', 'FAILED']
        if any(f'status: "{s}"' in content or f"status: '{s}'" in content for s in final_statuses):
            logger.info("✅ TEST 1 PASSED: Task was evaluated and reached final status")
            test_results.append(('TEST 1', True, 'PROCESSED task properly evaluated'))
        else:
            logger.error("❌ TEST 1 FAILED: Status still PROCESSED (evaluation didn't run)")
            test_results.append(('TEST 1', False, 'Evaluation did not run'))

        # Test 2: COMPLETED task should skip
        logger.info("\n" + "=" * 80)
        logger.info("TEST 2: COMPLETED task should skip")
        logger.info("=" * 80)

        task2 = create_test_task(tasks_dir, "2025-10-18 Test Status COMPLETED.md", "COMPLETED")
        created_tasks.append(task2)

        logger.info(f"Created task with status: COMPLETED")
        logger.info(f"Calling evaluate_task()...")

        # This should skip (already completed)
        runner.evaluate_task(task2.name)

        # Status should stay COMPLETED
        with open(task2, 'r') as f:
            content = f.read()

        if 'status: "COMPLETED"' in content or "status: 'COMPLETED'" in content:
            logger.info("✅ TEST 2 PASSED: Status stayed COMPLETED (skipped)")
            test_results.append(('TEST 2', True, 'COMPLETED task properly skipped'))
        else:
            logger.error("❌ TEST 2 FAILED: Status changed unexpectedly")
            test_results.append(('TEST 2', False, 'Status changed'))

        # Test 3: UNDER_REVIEW task should skip
        logger.info("\n" + "=" * 80)
        logger.info("TEST 3: UNDER_REVIEW task should skip")
        logger.info("=" * 80)

        task3 = create_test_task(tasks_dir, "2025-10-18 Test Status UNDER_REVIEW.md", "UNDER_REVIEW")
        created_tasks.append(task3)

        logger.info(f"Created task with status: UNDER_REVIEW")
        logger.info(f"Calling evaluate_task()...")

        # This should skip (already in review)
        runner.evaluate_task(task3.name)

        # Status should stay UNDER_REVIEW
        with open(task3, 'r') as f:
            content = f.read()

        if 'status: "UNDER_REVIEW"' in content or "status: 'UNDER_REVIEW'" in content:
            logger.info("✅ TEST 3 PASSED: Status stayed UNDER_REVIEW (skipped)")
            test_results.append(('TEST 3', True, 'UNDER_REVIEW task properly skipped'))
        else:
            logger.error("❌ TEST 3 FAILED: Status changed unexpectedly")
            test_results.append(('TEST 3', False, 'Status changed'))

        # Test 4: PROCESSED + evaluated="1" (stuck task) should evaluate
        logger.info("\n" + "=" * 80)
        logger.info("TEST 4: PROCESSED + evaluated='1' (stuck task) should evaluate")
        logger.info("=" * 80)

        task4 = create_test_task(tasks_dir, "2025-10-18 Test Stuck Task.md", "PROCESSED", add_evaluated_flag=True)
        created_tasks.append(task4)

        logger.info(f"Created task with status: PROCESSED, evaluated: '1'")
        logger.info(f"This simulates a stuck task from old code")
        logger.info(f"Calling evaluate_task()...")

        # This should evaluate anyway (ignores old evaluated flag)
        runner.evaluate_task(task4.name)

        # Read status after evaluation completes
        with open(task4, 'r') as f:
            content = f.read()

        # Check if status changed from PROCESSED (evaluation ran despite old evaluated flag)
        final_statuses = ['COMPLETED', 'NEEDS_INPUT', 'FAILED']
        if any(f'status: "{s}"' in content or f"status: '{s}'" in content for s in final_statuses):
            logger.info("✅ TEST 4 PASSED: Stuck task re-evaluated and reached final status")
            logger.info("   Old 'evaluated' flag was properly ignored!")
            test_results.append(('TEST 4', True, 'Stuck task properly re-evaluated'))
        else:
            logger.error("❌ TEST 4 FAILED: Stuck task still at PROCESSED status")
            test_results.append(('TEST 4', False, 'Stuck task still stuck'))

        # Test 5: NEEDS_INPUT should skip
        logger.info("\n" + "=" * 80)
        logger.info("TEST 5: NEEDS_INPUT task should skip")
        logger.info("=" * 80)

        task5 = create_test_task(tasks_dir, "2025-10-18 Test Status NEEDS_INPUT.md", "NEEDS_INPUT")
        created_tasks.append(task5)

        logger.info(f"Created task with status: NEEDS_INPUT")
        logger.info(f"Calling evaluate_task()...")

        # This should skip (already evaluated, needs human input)
        runner.evaluate_task(task5.name)

        # Status should stay NEEDS_INPUT
        with open(task5, 'r') as f:
            content = f.read()

        if 'status: "NEEDS_INPUT"' in content or "status: 'NEEDS_INPUT'" in content:
            logger.info("✅ TEST 5 PASSED: Status stayed NEEDS_INPUT (skipped)")
            test_results.append(('TEST 5', True, 'NEEDS_INPUT task properly skipped'))
        else:
            logger.error("❌ TEST 5 FAILED: Status changed unexpectedly")
            test_results.append(('TEST 5', False, 'Status changed'))

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)

        passed = sum(1 for _, result, _ in test_results if result)
        total = len(test_results)

        for test_name, result, message in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} - {test_name}: {message}")

        logger.info("")
        logger.info(f"Total: {passed}/{total} tests passed")

        # Also print to stdout for visibility
        print(f"\n{'='*80}")
        print(f"TEST RESULTS: {passed}/{total} tests passed")
        print(f"{'='*80}")

        if passed == total:
            logger.info("\n🎉 ALL TESTS PASSED!")
            logger.info("\nStatus-based evaluation is working correctly:")
            logger.info("  ✅ PROCESSED tasks are evaluated and reach final status")
            logger.info("  ✅ COMPLETED/UNDER_REVIEW/NEEDS_INPUT/FAILED tasks are skipped")
            logger.info("  ✅ Stuck tasks (PROCESSED + evaluated='1') are properly re-evaluated")
            logger.info("  ✅ No dependency on 'evaluated' flag - status is single source of truth")

            print("\n🎉 ALL TESTS PASSED!")
            print("\nStatus-based evaluation is working correctly:")
            print("  ✅ PROCESSED tasks are evaluated and reach final status")
            print("  ✅ COMPLETED/UNDER_REVIEW/NEEDS_INPUT/FAILED tasks are skipped")
            print("  ✅ Stuck tasks (PROCESSED + evaluated='1') are properly re-evaluated")
            print("  ✅ No dependency on 'evaluated' flag - status is single source of truth\n")
            return True
        else:
            logger.error(f"\n❌ {total - passed} TEST(S) FAILED")
            print(f"\n❌ {total - passed} TEST(S) FAILED\n")
            for test_name, result, message in test_results:
                if not result:
                    print(f"  FAILED: {test_name} - {message}")
            return False

    finally:
        # Cleanup
        logger.info("\n" + "=" * 80)
        logger.info("CLEANUP")
        logger.info("=" * 80)

        for task_path in created_tasks:
            try:
                if task_path.exists():
                    task_path.unlink()
                    logger.info(f"✅ Removed: {task_path.name}")
            except Exception as e:
                logger.warning(f"⚠️  Could not remove {task_path.name}: {e}")


if __name__ == '__main__':
    success = test_status_based_evaluation()
    sys.exit(0 if success else 1)
