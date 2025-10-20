#!/usr/bin/env python3
"""Test script for TaskStatusManager."""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add parent directory to path to import task_status
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from task_status import TaskStatusManager


def create_test_task(tasks_dir: str, filename: str, status: str = "TBD", priority: str = "P2") -> str:
    """Create a test task file.
    
    Args:
        tasks_dir: Directory to create task in
        filename: Task filename
        status: Initial status
        priority: Priority level
        
    Returns:
        Full path to created file
    """
    content = f"""---
created: 2025-10-16
status: {status}
priority: {priority}
task_type: Test
worker: ""
output: ""
archived: false
---

# Test Task

## Instructions

This is a test task for verifying TaskStatusManager functionality.
"""
    
    file_path = os.path.join(tasks_dir, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path


def test_scan_tasks(manager: TaskStatusManager):
    """Test scanning tasks."""
    print("\n📋 Test 1: Scanning tasks...")
    tasks = manager.scan_tasks()
    
    if len(tasks) > 0:
        print(f"✅ Found {len(tasks)} task(s)")
        for task in tasks:
            print(f"   - {task['file']}: status={task['status']}, priority={task['priority']}")
        return True
    else:
        print("⚠️  No tasks found")
        return False


def test_read_status(manager: TaskStatusManager, filename: str, expected_status: str):
    """Test reading task status.
    
    Args:
        manager: TaskStatusManager instance
        filename: Task filename to check
        expected_status: Expected status value
        
    Returns:
        True if test passed
    """
    print(f"\n📖 Test 2: Reading status from {filename}...")
    tasks = manager.scan_tasks()
    
    task = next((t for t in tasks if t['file'] == filename), None)
    
    if task:
        actual_status = task['status']
        if actual_status == expected_status:
            print(f"✅ Status correct: {actual_status}")
            return True
        else:
            print(f"❌ Status mismatch: expected={expected_status}, actual={actual_status}")
            return False
    else:
        print(f"❌ Task not found: {filename}")
        return False


def test_update_status(manager: TaskStatusManager, filename: str, new_status: str, worker: str = None):
    """Test updating task status.
    
    Args:
        manager: TaskStatusManager instance
        filename: Task filename to update
        new_status: New status value
        worker: Worker name (optional)
        
    Returns:
        True if test passed
    """
    print(f"\n✏️  Test 3: Updating status to {new_status}...")
    success = manager.update_task_status(filename, new_status, worker)
    
    if success:
        print(f"✅ Update successful")
        return True
    else:
        print(f"❌ Update failed")
        return False


def test_verify_update(manager: TaskStatusManager, filename: str, expected_status: str, expected_worker: str = None):
    """Test verifying status was updated correctly.
    
    Args:
        manager: TaskStatusManager instance
        filename: Task filename to verify
        expected_status: Expected status after update
        expected_worker: Expected worker after update (optional)
        
    Returns:
        True if test passed
    """
    print(f"\n🔍 Test 4: Verifying update...")
    tasks = manager.scan_tasks()
    
    task = next((t for t in tasks if t['file'] == filename), None)
    
    if not task:
        print(f"❌ Task not found: {filename}")
        return False
    
    status_ok = task['status'] == expected_status
    worker_ok = True
    
    if expected_worker:
        worker_ok = task['worker'] == expected_worker
        
    if status_ok and worker_ok:
        print(f"✅ Verification successful: status={task['status']}" + 
              (f", worker={task['worker']}" if expected_worker else ""))
        return True
    else:
        print(f"❌ Verification failed:")
        if not status_ok:
            print(f"   Status: expected={expected_status}, actual={task['status']}")
        if not worker_ok:
            print(f"   Worker: expected={expected_worker}, actual={task['worker']}")
        return False


def test_filter_and_sort(manager: TaskStatusManager):
    """Test filtering and sorting tasks."""
    print(f"\n🔄 Test 5: Filter and sort...")
    
    tasks = manager.scan_tasks()
    
    # Test filtering by status
    tbd_tasks = manager.filter_tasks(tasks, status='TBD')
    print(f"   TBD tasks: {len(tbd_tasks)}")
    
    # Test sorting
    sorted_tasks = manager.sort_tasks(tbd_tasks)
    if sorted_tasks:
        print(f"   Sorted order:")
        for task in sorted_tasks:
            print(f"      - {task['file']}: {task['priority']}")
    
    print(f"✅ Filter and sort working")
    return True


def test_statistics(manager: TaskStatusManager):
    """Test statistics generation."""
    print(f"\n📊 Test 6: Statistics...")
    
    tasks = manager.scan_tasks()
    stats = manager.generate_statistics(tasks)
    
    print(f"   Total: {stats['total']}")
    print(f"   Active: {stats['active']}")
    print(f"   By Status: {stats['by_status']}")
    print(f"   By Priority: {stats['by_priority']}")
    
    print(f"✅ Statistics generated")
    return True


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("TaskStatusManager Test Suite")
    print("=" * 60)
    
    # Create temporary test workspace
    test_workspace = tempfile.mkdtemp(prefix="task_status_test_")
    tasks_dir = os.path.join(test_workspace, "AI", "Tasks")
    os.makedirs(tasks_dir, exist_ok=True)
    
    print(f"\n🔧 Test workspace: {test_workspace}")
    
    try:
        # Initialize manager
        manager = TaskStatusManager(workspace_path=test_workspace)
        
        # Create test tasks
        print("\n📝 Creating test tasks...")
        test_file_1 = "2025-10-16-test-task-1.md"
        test_file_2 = "2025-10-16-test-task-2.md"
        
        create_test_task(tasks_dir, test_file_1, status="TBD", priority="P1")
        create_test_task(tasks_dir, test_file_2, status="TBD", priority="P2")
        print(f"✅ Created: {test_file_1}, {test_file_2}")
        
        # Run tests
        results = []
        
        results.append(("Scan tasks", test_scan_tasks(manager)))
        results.append(("Read status", test_read_status(manager, test_file_1, "TBD")))
        results.append(("Update status", test_update_status(manager, test_file_1, "IN_PROGRESS", "TestAgent")))
        results.append(("Verify update", test_verify_update(manager, test_file_1, "IN_PROGRESS", "TestAgent")))
        results.append(("Filter and sort", test_filter_and_sort(manager)))
        results.append(("Statistics", test_statistics(manager)))
        
        # Summary
        print("\n" + "=" * 60)
        print("Test Results Summary")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
            return 1
            
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up test workspace...")
        shutil.rmtree(test_workspace)
        print("✅ Cleanup complete")


if __name__ == '__main__':
    sys.exit(run_tests())

