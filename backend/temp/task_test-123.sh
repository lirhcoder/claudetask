#!/bin/bash
echo "========================================"
echo "Claude Task Executor"
echo "Task ID: test-123"
echo "Created: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
echo

cd "/tmp/test"
echo "Working Directory: $(pwd)"
echo

echo "Executing Claude Code..."
echo "----------------------------------------"
claude "测试提示词"

echo
echo "----------------------------------------"
echo "Task completed. Press Enter to close..."
read
