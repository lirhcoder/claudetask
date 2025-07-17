#!/bin/bash
echo "========================================"
echo "Claude Task Executor"
echo "Task ID: 4640ab1e-a2df-440c-a4d6-76a299094be0"
echo "Created: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
echo

cd "/mnt/c/development/claudetask/backend/projects/test-local"
echo "Working Directory: $(pwd)"
echo

echo "Executing Claude Code..."
echo "----------------------------------------"
claude "Please create a simple test file named 'hello.txt' with the content 'Hello from local execution!'"

echo
echo "----------------------------------------"
echo "Task completed. Press Enter to close..."
read
