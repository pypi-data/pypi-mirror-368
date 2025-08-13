#!/usr/bin/env python3
"""
Test Suite for SequentialTaskExecutor

This module contains unit tests for the SequentialTaskExecutor class.
"""

import os
import json
import tempfile
from sokrates.sequential_task_executor import SequentialTaskExecutor
from sokrates.file_helper import FileHelper

def create_test_task_file():
    """Create a test JSON file with sample tasks"""
    tasks = {
        "task": "Test task execution",
        "subtasks": [
            {
                "id": 1,
                "description": "Write a story about a cat named Minzi that lives on the streets of Saarbrücken.",
                "complexity": 8
            },
            {
                "id": 2,
                "description": "Make a plan for publishing a book with stories about a cat named Minzi that lives on the streets of Saarbrücken.",
                "complexity": 6
            }
        ],
        "count": 2
    }

    # Create temporary file
    fd, path = tempfile.mkstemp(suffix='.json')
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(tasks, f, indent=2)
        return path
    except Exception as e:
        os.close(fd)
        raise e

def test_sequential_task_executor():
    """Test the SequentialTaskExecutor class"""
    # Create test task file
    task_file = create_test_task_file()

    try:
        # Initialize executor with minimal configuration for testing
        executor = SequentialTaskExecutor(
            api_endpoint="http://localhost:1234/v1",
            api_key="notrequired",
            model="qwen/qwen3-8b",
            output_dir="../tmp/test_results",
            verbose=False
        )

        # Execute tasks
        result = executor.execute_tasks_from_file(task_file)

        # Verify results
        assert "total_tasks" in result
        assert "successful_tasks" in result
        assert "failed_tasks" in result
        assert "details" in result

        print("✓ SequentialTaskExecutor test passed")

    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        raise
    finally:
        # Clean up
        if os.path.exists(task_file):
            os.remove(task_file)
        if os.path.exists("./test_results"):
            import shutil
            shutil.rmtree("./test_results")

if __name__ == "__main__":
    test_sequential_task_executor()