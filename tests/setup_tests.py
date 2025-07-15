#!/usr/bin/env python3
"""
Setup script for NASA MCP Server testing environment.

This script installs the required dependencies and prepares the testing environment.
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies for testing."""
    print("Installing test dependencies...")
    try:
        # Go to parent directory to find requirements.txt
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        requirements_path = os.path.join(parent_dir, "requirements.txt")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        return False

def setup_environment():
    """Set up the testing environment."""
    print("Setting up testing environment...")
    
    # Go to parent directory for proper paths
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create __init__.py in tests directory if it doesn't exist
    tests_init = os.path.join(parent_dir, "tests", "__init__.py")
    if not os.path.exists(tests_init):
        with open(tests_init, "w") as f:
            f.write("# Test package initialization\n")
        print("✓ Created tests/__init__.py")
    
    # Create __init__.py in src directory if it doesn't exist
    src_init = os.path.join(parent_dir, "src", "__init__.py")
    if not os.path.exists(src_init):
        with open(src_init, "w") as f:
            f.write("# Source package initialization\n")
        print("✓ Created src/__init__.py")
    
    return True

def main():
    """Main setup function."""
    print("NASA MCP Server - Test Environment Setup")
    print("=" * 50)
    
    if not install_dependencies():
        sys.exit(1)
    
    if not setup_environment():
        sys.exit(1)
    
    print("\nSetup completed successfully!")
    print("\nTo run tests:")
    print("  python -m pytest tests/")
    print("  python tests/run_tests.py")
    print("\nTo run specific test:")
    print("  python -m pytest tests/test_server.py::TestAPODTool::test_get_apod_default")

if __name__ == "__main__":
    main()
