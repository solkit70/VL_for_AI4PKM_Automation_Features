"""Integration test for UNDER_REVIEW task recovery.

Tests the smart cleanup logic that validates output and either:
- Marks tasks COMPLETED if output is valid
- Resets tasks to PROCESSED if output is invalid/missing

This test verifies the fix for stuck UNDER_REVIEW tasks from old code bugs.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai4pkm_cli.logger import Logger
from ai4pkm_cli.cli import PKMApp
from ai4pkm_cli.config import Config


def create_test_task(tasks_dir: Path, task_name: str, status: str,
                     output_link: str = "", add_evaluated_flag: bool = False) -> Path:
    """Create test task with specified status and optional output.

    Args:
        tasks_dir: Path to tasks directory
        task_name: Task filename
        status: Task status
        output_link: Wiki link for output property
        add_evaluated_flag: Whether to add evaluated="1" flag (old code artifact)

    Returns:
        Path to created task file
    """
    task_path = tasks_dir / task_name

    evaluated_line = 'evaluated: "1"' if add_evaluated_flag else ''
    output_line = f'output: "{output_link}"' if output_link else ''

    content = f"""---
created: {datetime.now().isoformat()}
status: "{status}"
task_type: EIC
worker: "test"
priority: P1
{output_line}
{evaluated_line}
---
# Test UNDER_REVIEW Recovery

## Input
Test content for UNDER_REVIEW recovery testing.

## Instructions
- Validate output exists and is complete
- Mark COMPLETED if output valid
- Reset to PROCESSED if output invalid

## Context
This task is testing UNDER_REVIEW recovery scenarios:
- Status: {status}
- Has evaluated flag: {add_evaluated_flag}
- Has output: {bool(output_link)}
"""

    with open(task_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return task_path


def create_output_file(output_path: Path, lines: int = 100, valid: bool = True):
    """Create test output file.

    Args:
        output_path: Path to output file
        lines: Number of lines to generate
        valid: Whether to create valid output (with frontmatter)
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if valid:
        content = f"""---
title: "Test Output"
created: {datetime.now().strftime('%Y-%m-%d')}
tags:
  - test
  - output
---

## Summary

This is a test output file with {lines} lines.

"""
        # Add content to reach desired line count
        for i in range(lines - 15):
            content += f"Line {i+1} of test content.\n"
    else:
        # Invalid: too short, no frontmatter
        content = "Invalid output\nOnly a few lines\nNot enough substance\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def test_under_review_recovery():
    """Test UNDER_REVIEW task recovery with various scenarios."""
    logger = Logger(console_output=True)

    # Use AI4PKM repo as workspace
    repo_root = Path(__file__).parent.parent.parent
    tasks_dir = repo_root / "AI" / "Tasks"
    articles_dir = repo_root / "AI" / "Articles"

    print("=" * 80)
    print("TEST: UNDER_REVIEW Task Recovery")
    print("=" * 80)
    print("")

    created_tasks = []
    created_outputs = []

    try:
        # Test 1: UNDER_REVIEW + valid output → COMPLETED
        print("\n" + "=" * 80)
        print("TEST 1: UNDER_REVIEW + valid output → COMPLETED")
        print("=" * 80)

        task1 = create_test_task(
            tasks_dir,
            "2025-10-18 Test UR Valid Output.md",
            "UNDER_REVIEW",
            output_link="[[AI/Articles/2025-10-18 Test UR Valid Output by Test.md]]",
            add_evaluated_flag=True  # Old code artifact - should be ignored
        )
        created_tasks.append(task1)

        output1 = articles_dir / "2025-10-18 Test UR Valid Output by Test.md"
        create_output_file(output1, lines=100, valid=True)
        created_outputs.append(output1)

        print(f"Created task with status: UNDER_REVIEW")
        print(f"Created valid output: {output1.name} (100 lines)")
        print(f"Task has evaluated='1' flag (should be ignored)")
        print(f"Running cleanup...")

        # Create app and run cleanup
        config = Config()
        app = PKMApp(suppress_agent_logging=True)
        app._check_under_review_tasks()

        # Read task status after cleanup
        with open(task1, 'r') as f:
            content = f.read()

        if 'status: "COMPLETED"' in content or "status: 'COMPLETED'" in content:
            print("✅ TEST 1 PASSED: Task marked COMPLETED (output was valid)")
            test1_passed = True
        else:
            print("❌ TEST 1 FAILED: Task not marked COMPLETED")
            print(f"   Current status: {[line for line in content.split('\\n') if 'status:' in line]}")
            test1_passed = False

        # Test 2: UNDER_REVIEW + missing output → PROCESSED
        print("\n" + "=" * 80)
        print("TEST 2: UNDER_REVIEW + missing output → PROCESSED")
        print("=" * 80)

        task2 = create_test_task(
            tasks_dir,
            "2025-10-18 Test UR Missing Output.md",
            "UNDER_REVIEW",
            output_link="[[AI/Articles/2025-10-18 Test UR Missing Output by Test.md]]"
        )
        created_tasks.append(task2)

        print(f"Created task with status: UNDER_REVIEW")
        print(f"Output file NOT created (simulating failed execution)")
        print(f"Running cleanup...")

        app._check_under_review_tasks()

        # Read task status after cleanup
        with open(task2, 'r') as f:
            content = f.read()

        if 'status: "PROCESSED"' in content or "status: 'PROCESSED'" in content:
            print("✅ TEST 2 PASSED: Task reset to PROCESSED (output missing)")
            test2_passed = True
        else:
            print("❌ TEST 2 FAILED: Task not reset to PROCESSED")
            print(f"   Current status: {[line for line in content.split('\\n') if 'status:' in line]}")
            test2_passed = False

        # Test 3: UNDER_REVIEW + invalid output (too short) → PROCESSED
        print("\n" + "=" * 80)
        print("TEST 3: UNDER_REVIEW + invalid output (too short) → PROCESSED")
        print("=" * 80)

        task3 = create_test_task(
            tasks_dir,
            "2025-10-18 Test UR Invalid Output.md",
            "UNDER_REVIEW",
            output_link="[[AI/Articles/2025-10-18 Test UR Invalid Output by Test.md]]"
        )
        created_tasks.append(task3)

        output3 = articles_dir / "2025-10-18 Test UR Invalid Output by Test.md"
        create_output_file(output3, lines=10, valid=False)
        created_outputs.append(output3)

        print(f"Created task with status: UNDER_REVIEW")
        print(f"Created invalid output: {output3.name} (only 3 lines, no frontmatter)")
        print(f"Running cleanup...")

        app._check_under_review_tasks()

        # Read task status after cleanup
        with open(task3, 'r') as f:
            content = f.read()

        if 'status: "PROCESSED"' in content or "status: 'PROCESSED'" in content:
            print("✅ TEST 3 PASSED: Task reset to PROCESSED (output invalid)")
            test3_passed = True
        else:
            print("❌ TEST 3 FAILED: Task not reset to PROCESSED")
            print(f"   Current status: {[line for line in content.split('\\n') if 'status:' in line]}")
            test3_passed = False

        # Test 4: UNDER_REVIEW + no output property → PROCESSED
        print("\n" + "=" * 80)
        print("TEST 4: UNDER_REVIEW + no output property → PROCESSED")
        print("=" * 80)

        task4 = create_test_task(
            tasks_dir,
            "2025-10-18 Test UR No Output Property.md",
            "UNDER_REVIEW",
            output_link=""  # No output property
        )
        created_tasks.append(task4)

        print(f"Created task with status: UNDER_REVIEW")
        print(f"No output property defined")
        print(f"Running cleanup...")

        app._check_under_review_tasks()

        # Read task status after cleanup
        with open(task4, 'r') as f:
            content = f.read()

        if 'status: "PROCESSED"' in content or "status: 'PROCESSED'" in content:
            print("✅ TEST 4 PASSED: Task reset to PROCESSED (no output property)")
            test4_passed = True
        else:
            print("❌ TEST 4 FAILED: Task not reset to PROCESSED")
            print(f"   Current status: {[line for line in content.split('\\n') if 'status:' in line]}")
            test4_passed = False

        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        all_passed = all([test1_passed, test2_passed, test3_passed, test4_passed])

        tests = [
            ("TEST 1: Valid output → COMPLETED", test1_passed),
            ("TEST 2: Missing output → PROCESSED", test2_passed),
            ("TEST 3: Invalid output → PROCESSED", test3_passed),
            ("TEST 4: No output property → PROCESSED", test4_passed),
        ]

        for test_name, passed in tests:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} - {test_name}")

        print("")
        passed_count = sum(1 for _, p in tests if p)
        print(f"Total: {passed_count}/{len(tests)} tests passed")
        print("")

        if all_passed:
            print("🎉 ALL TESTS PASSED!")
            print("")
            print("UNDER_REVIEW recovery is working correctly:")
            print("  ✅ Valid output → marked COMPLETED")
            print("  ✅ Invalid/missing output → reset to PROCESSED")
            print("  ✅ Old 'evaluated' flag ignored (status is single source of truth)")
            print("")
            return True
        else:
            print("❌ SOME TESTS FAILED")
            return False

    finally:
        # Cleanup
        print("\n" + "=" * 80)
        print("CLEANUP")
        print("=" * 80)

        for task in created_tasks:
            if task.exists():
                task.unlink()
                print(f"Deleted test task: {task.name}")

        for output in created_outputs:
            if output.exists():
                output.unlink()
                print(f"Deleted test output: {output.name}")

        print("Cleanup complete")
        print("")


if __name__ == "__main__":
    success = test_under_review_recovery()
    sys.exit(0 if success else 1)
