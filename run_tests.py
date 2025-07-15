#!/usr/bin/env python3
"""
Test runner script for NASA MCP Server tests.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py -v           # Run with verbose output
    python run_tests.py --help       # Show help
"""

import subprocess
import sys
import os

def main():
    """Run the test suite."""
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Build the pytest command
    cmd = [sys.executable, "-m", "pytest", "tests/"]
    
    # Add any command line arguments passed to this script
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    # Add default arguments for better output
    if "-v" not in cmd and "--verbose" not in cmd:
        cmd.append("-v")
    
    # Add coverage if available
    try:
        import coverage
        cmd.extend(["--cov=src/nasa_mcp", "--cov-report=term-missing"])
    except ImportError:
        pass
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 60)
    
    # Run the tests
    result = subprocess.run(cmd)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
