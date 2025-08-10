#!/usr/bin/env python3
"""
ReqNinja Development Setup Script

This script helps set up the development environment and validates the installation.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report the result."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {cmd}")
        print(f"   Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("   ReqNinja requires Python 3.8 or higher")
        return False


def setup_development_environment():
    """Set up the development environment."""
    print("🚀 Setting up ReqNinja development environment")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install in development mode
    if not run_command("pip install -e .", "Installing ReqNinja in development mode"):
        return False
    
    # Install development dependencies
    if not run_command("pip install -e \".[dev,test]\"", "Installing development dependencies"):
        return False
    
    # Install pre-commit hooks
    if not run_command("pre-commit install", "Setting up pre-commit hooks"):
        print("⚠️  Pre-commit installation failed (optional)")
    
    return True


def run_tests():
    """Run the test suite."""
    print("\n🧪 Running tests...")
    return run_command("pytest -v", "Running test suite")


def run_linting():
    """Run linting checks."""
    print("\n🔍 Running linting checks...")
    
    checks = [
        ("black --check .", "Code formatting check (Black)"),
        ("isort --check-only .", "Import sorting check (isort)"),
        ("flake8 .", "Linting check (flake8)"),
    ]
    
    all_passed = True
    for cmd, desc in checks:
        if not run_command(cmd, desc):
            all_passed = False
    
    return all_passed


def validate_cli():
    """Validate CLI functionality."""
    print("\n🖥️  Validating CLI...")
    
    # Test basic CLI functionality
    tests = [
        ("reqninja --version", "Version check"),
        ("reqninja --help", "Help command"),
        ("reqninja http --help", "HTTP command help"),
    ]
    
    for cmd, desc in tests:
        if not run_command(cmd, desc):
            return False
    
    return True


def create_example_config():
    """Create an example configuration file."""
    print("\n📝 Creating example configuration...")
    
    config_dir = Path.home() / '.reqninja'
    config_file = config_dir / 'config.yml'
    
    if config_file.exists():
        print(f"✅ Configuration already exists at {config_file}")
        return True
    
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy example config
        example_config = Path(__file__).parent / 'config.example.yml'
        if example_config.exists():
            import shutil
            shutil.copy(example_config, config_file)
            print(f"✅ Example configuration created at {config_file}")
            print(f"   Edit this file to customize your profiles and settings")
        else:
            print("⚠️  Example config file not found")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create configuration: {e}")
        return False


def run_example_request():
    """Run an example request to test functionality."""
    print("\n🌐 Testing with example request...")
    
    cmd = "reqninja http GET https://httpbin.org/json"
    return run_command(cmd, "Example GET request")


def main():
    """Main setup function."""
    print("ReqNinja Development Setup")
    print("=" * 50)
    
    # Setup development environment
    if not setup_development_environment():
        print("\n❌ Development environment setup failed")
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("\n⚠️  Some tests failed")
    
    # Run linting (optional)
    if not run_linting():
        print("\n⚠️  Linting checks failed (run 'make format' to fix)")
    
    # Validate CLI
    if not validate_cli():
        print("\n❌ CLI validation failed")
        sys.exit(1)
    
    # Create example config
    create_example_config()
    
    # Test with example request
    if not run_example_request():
        print("\n⚠️  Example request failed (check internet connection)")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("  • Edit ~/.reqninja/config.yml to add your profiles")
    print("  • Run 'reqninja --help' to see all available commands")
    print("  • Check out examples/ directory for usage examples")
    print("  • Run 'make test' to run the full test suite")
    print("  • Run 'make format' to format code")
    print("  • Visit https://github.com/vishal-ravi/reqninja for updates")


if __name__ == "__main__":
    main()
