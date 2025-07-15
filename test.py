#!/usr/bin/env python3
"""
Simple test runner for NASA MCP Server.
This script allows running tests from the project root.
"""

import subprocess
import sys
import os

def main():
    """Run tests from the project root."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Check if we're in the project root
    if not os.path.exists(os.path.join(project_root, "tests")):
        print("Error: tests directory not found. Please run from the project root.")
        sys.exit(1)
    
    # Run the actual test runner
    test_runner = os.path.join(project_root, "tests", "run_tests.py")
    
    # Pass all arguments to the test runner
    cmd = [sys.executable, test_runner] + sys.argv[1:]
    
    print("Running NASA MCP Server tests...")
    print("=" * 50)
    
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
