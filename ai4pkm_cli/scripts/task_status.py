#!/usr/bin/env python3
"""Task Status Manager - Scans and manages knowledge task files."""

import os
import sys
import json
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class TaskStatusManager:
    """Manages task status tracking and queue generation."""
    
    def __init__(self, workspace_path: str = None):
        """Initialize the task manager.
        
        Args:
            workspace_path: Path to the workspace root (defaults to current directory)
        """
        self.workspace_path = workspace_path or os.getcwd()
        self.tasks_dir = os.path.join(self.workspace_path, "AI", "Tasks")
        
    def scan_tasks(self) -> List[Dict[str, Any]]:
        """Scan all task files and extract metadata.
        
        Returns:
            List of task dictionaries with metadata
        """
        tasks = []
        
        if not os.path.exists(self.tasks_dir):
            return tasks
            
        # Find all markdown files in AI/Tasks (excluding Requests subdirectory)
        for file_path in Path(self.tasks_dir).glob("*.md"):
            if file_path.name == "Tasks.md":
                continue
                
            try:
                task_data = self._parse_task_file(str(file_path))
                if task_data:
                    tasks.append(task_data)
            except Exception as e:
                print(f"Warning: Error parsing {file_path.name}: {e}", file=sys.stderr)
                
        return tasks
    
    def _parse_task_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse a task file and extract frontmatter.
        
        Args:
            file_path: Path to the task file
            
        Returns:
            Dictionary with task metadata or None if invalid
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract frontmatter
        frontmatter = self._extract_frontmatter(content)
        if not frontmatter:
            return None
            
        # Extract filename and creation date
        filename = os.path.basename(file_path)
        created_date = self._extract_date_from_filename(filename)
        
        # Extract instructions from content
        instructions = self._extract_instructions(content)
        
        return {
            'file': filename,
            'path': file_path,
            'created': frontmatter.get('created', created_date),
            'status': frontmatter.get('status', 'TBD'),
            'priority': frontmatter.get('priority', 'P2'),
            'task_type': frontmatter.get('task_type', 'Unknown'),
            'worker': frontmatter.get('worker', ''),
            'output': frontmatter.get('output', ''),
            'archived': frontmatter.get('archived', False),
            'budget': frontmatter.get('budget', ''),
            'instructions': instructions
        }
    
    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown content.
        
        Args:
            content: Markdown file content
            
        Returns:
            Dictionary of frontmatter properties
        """
        # Match YAML frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return {}
            
        yaml_content = match.group(1)
        frontmatter = {}
        
        # Simple YAML parser for our needs
        for line in yaml_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Match key: value pairs
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                    
                # Convert boolean strings
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value == '':
                    value = ''
                    
                frontmatter[key] = value
                
        return frontmatter
    
    def _extract_date_from_filename(self, filename: str) -> str:
        """Extract date from filename (YYYY-MM-DD format).
        
        Args:
            filename: Task filename
            
        Returns:
            Date string or empty string
        """
        match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
        return match.group(1) if match else ''
    
    def _extract_instructions(self, content: str) -> str:
        """Extract instructions section from task content.
        
        Args:
            content: Full markdown content
            
        Returns:
            Instructions text (first 200 chars)
        """
        # Find ## Instructions section
        match = re.search(r'## Instructions\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if match:
            instructions = match.group(1).strip()
            # Return first 200 chars
            return instructions[:200] + '...' if len(instructions) > 200 else instructions
        return ''
    
    def filter_tasks(self, tasks: List[Dict[str, Any]], 
                    status: str = None, 
                    priority: str = None,
                    archived: bool = False) -> List[Dict[str, Any]]:
        """Filter tasks by status, priority, and archived state.
        
        Args:
            tasks: List of task dictionaries
            status: Filter by status (TBD, IN_PROGRESS, UNDER_REVIEW, COMPLETED)
            priority: Filter by priority (P0, P1, P2, P3)
            archived: Include archived tasks (default: False)
            
        Returns:
            Filtered list of tasks
        """
        filtered = tasks
        
        # Filter out archived tasks unless explicitly requested
        if not archived:
            filtered = [t for t in filtered if not t['archived']]
            
        if status:
            filtered = [t for t in filtered if t['status'] == status]
            
        if priority:
            filtered = [t for t in filtered if t['priority'] == priority]
            
        return filtered
    
    def sort_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort tasks by priority (P0 > P1 > P2 > P3) then by creation date.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Sorted list of tasks
        """
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        
        def sort_key(task):
            priority_val = priority_order.get(task['priority'], 99)
            created = task['created'] or '9999-99-99'
            return (priority_val, created)
            
        return sorted(tasks, key=sort_key)
    
    def generate_statistics(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about tasks.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Statistics dictionary
        """
        stats = {
            'total': len(tasks),
            'active': 0,
            'by_status': {},
            'by_priority': {}
        }
        
        for task in tasks:
            status = task['status']
            priority = task['priority']
            
            # Count by status
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # Count by priority
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
            
            # Count active tasks (not COMPLETED, not archived)
            if status not in ['COMPLETED', 'CANCELLED'] and not task['archived']:
                stats['active'] += 1
                
        return stats
    
    def generate_execution_queue(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prioritized execution queue.

        Args:
            tasks: List of task dictionaries (should already be filtered)

        Returns:
            Ordered list of tasks ready for execution
        """
        # Sort by priority (tasks should already be filtered by caller)
        sorted_tasks = self.sort_tasks(tasks)

        # Add order numbers
        queue = []
        for idx, task in enumerate(sorted_tasks, 1):
            queue_item = {
                'order': idx,
                'file': task['file'],
                'priority': task['priority'],
                'status': task['status'],
                'task_type': task['task_type'],
                'instructions': task['instructions']
            }
            queue.append(queue_item)

        return queue
    
    def group_by_priority(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group tasks by priority level.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Dictionary mapping priority to list of tasks
        """
        grouped = {'P0': [], 'P1': [], 'P2': [], 'P3': []}
        
        for task in tasks:
            priority = task['priority']
            if priority in grouped:
                grouped[priority].append(task)
                
        return grouped
    
    def update_task_status(self, filename: str, new_status: str, worker: str = None) -> bool:
        """Update task status in file.
        
        Args:
            filename: Task filename
            new_status: New status value
            worker: Worker/agent name (optional)
            
        Returns:
            True if successful, False otherwise
        """
        file_path = os.path.join(self.tasks_dir, filename)
        if not os.path.exists(file_path):
            print(f"Error: Task file not found: {filename}", file=sys.stderr)
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Update status in frontmatter
            content = self._update_frontmatter_field(content, 'status', new_status)
            
            if worker:
                content = self._update_frontmatter_field(content, 'worker', worker)
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ Updated {filename}: status={new_status}" + (f", worker={worker}" if worker else ""))
            return True
            
        except Exception as e:
            print(f"Error updating task: {e}", file=sys.stderr)
            return False
    
    def complete_task(self, filename: str, output_link: str = None) -> bool:
        """Mark task as completed.
        
        Args:
            filename: Task filename
            output_link: Output wiki link (optional)
            
        Returns:
            True if successful, False otherwise
        """
        file_path = os.path.join(self.tasks_dir, filename)
        if not os.path.exists(file_path):
            print(f"Error: Task file not found: {filename}", file=sys.stderr)
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Update status
            content = self._update_frontmatter_field(content, 'status', 'COMPLETED')
            
            # Update output if provided
            if output_link:
                content = self._update_frontmatter_field(content, 'output', output_link)
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ Completed {filename}" + (f" with output: {output_link}" if output_link else ""))
            return True
            
        except Exception as e:
            print(f"Error completing task: {e}", file=sys.stderr)
            return False
    
    def _update_frontmatter_field(self, content: str, field: str, value: str) -> str:
        """Update a field in YAML frontmatter.
        
        Args:
            content: Full markdown content
            field: Field name to update
            value: New value
            
        Returns:
            Updated content
        """
        # Match frontmatter
        match = re.match(r'^(---\s*\n)(.*?)(\n---\s*\n)', content, re.DOTALL)
        if not match:
            return content
            
        prefix = match.group(1)
        yaml_content = match.group(2)
        suffix = match.group(3)
        rest = content[match.end():]
        
        # Check if field exists
        field_pattern = rf'^{field}:\s*.*$'
        if re.search(field_pattern, yaml_content, re.MULTILINE):
            # Update existing field
            yaml_content = re.sub(field_pattern, f'{field}: "{value}"', yaml_content, flags=re.MULTILINE)
        else:
            # Add new field
            yaml_content += f'\n{field}: "{value}"'
            
        return prefix + yaml_content + suffix + rest


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(description='Task Status Manager for AI4PKM')
    
    parser.add_argument('--stats-only', action='store_true',
                       help='Display statistics only (no queue generation)')
    parser.add_argument('--output', type=str,
                       help='Output JSON file for task queue')
    parser.add_argument('--status', type=str, choices=['TBD', 'IN_PROGRESS', 'PROCESSED', 'UNDER_REVIEW', 'COMPLETED'],
                       help='Filter by status')
    parser.add_argument('--priority', type=str, choices=['P0', 'P1', 'P2', 'P3'],
                       help='Filter by priority')
    parser.add_argument('--update', type=str,
                       help='Update status of specific task (provide filename)')
    parser.add_argument('--status-new', type=str,
                       help='New status value (use with --update)')
    parser.add_argument('--worker', type=str,
                       help='Worker/agent name (use with --update)')
    parser.add_argument('--complete', type=str,
                       help='Mark task as completed (provide filename)')
    parser.add_argument('--output-link', type=str,
                       help='Output wiki link (use with --complete)')
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = TaskStatusManager()
    
    # Handle update command
    if args.update:
        if not args.status_new:
            print("Error: --status-new required with --update", file=sys.stderr)
            sys.exit(1)
        success = manager.update_task_status(args.update, args.status_new, args.worker)
        sys.exit(0 if success else 1)
        
    # Handle complete command
    if args.complete:
        success = manager.complete_task(args.complete, args.output_link)
        sys.exit(0 if success else 1)
    
    # Scan tasks
    print("Scanning tasks...", file=sys.stderr)
    tasks = manager.scan_tasks()
    
    # Filter if requested
    filtered_tasks = manager.filter_tasks(tasks, status=args.status, priority=args.priority)
    
    # Generate statistics
    stats = manager.generate_statistics(filtered_tasks)
    
    print(f"\n📊 Task Statistics:", file=sys.stderr)
    print(f"Total: {stats['total']}", file=sys.stderr)
    print(f"Active: {stats['active']}", file=sys.stderr)
    print(f"By Status: {stats['by_status']}", file=sys.stderr)
    print(f"By Priority: {stats['by_priority']}\n", file=sys.stderr)
    
    # If stats only, exit
    if args.stats_only:
        sys.exit(0)
    
    # Generate execution queue
    queue = manager.generate_execution_queue(filtered_tasks)
    grouped = manager.group_by_priority(filtered_tasks)
    
    # Prepare output
    output_data = {
        'generated': datetime.now().isoformat(),
        'statistics': stats,
        'execution_queue': queue,
        'grouped': {k: [t['file'] for t in v] for k, v in grouped.items()}
    }
    
    # Write to file or stdout
    if args.output:
        # Ensure directory exists
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        print(f"✅ Queue written to: {args.output}", file=sys.stderr)
    else:
        print(json.dumps(output_data, indent=2))
    
    sys.exit(0)


if __name__ == '__main__':
    main()


