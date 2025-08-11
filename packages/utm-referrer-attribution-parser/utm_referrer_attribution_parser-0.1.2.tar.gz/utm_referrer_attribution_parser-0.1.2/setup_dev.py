#!/usr/bin/env python3
"""
Development setup script for utm-referrer-attribution-parser.
"""

import os
import subprocess
import sys


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def main():
    """Set up development environment."""
    print("🚀 Setting up utm-referrer-attribution-parser development environment")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not os.path.exists('pyproject.toml'):
        print("❌ pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)
    
    success = True
    
    # Install package in development mode
    success &= run_command(
        "pip install -e .[dev]",
        "Installing package in development mode"
    )
    
    # Run tests
    if success:
        success &= run_command(
            "python -m pytest tests/ -v",
            "Running tests"
        )
    
    # Run basic functionality test
    if success:
        success &= run_command(
            "python examples/basic_usage.py > /dev/null",
            "Testing basic functionality"
        )
    
    # Check code formatting
    if success:
        print("🔄 Checking code style...")
        try:
            subprocess.run("black --check .", shell=True, check=True, capture_output=True)
            print("✅ Code style check passed")
        except subprocess.CalledProcessError:
            print("⚠️  Code style issues found. Run 'black .' to fix.")
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 Development environment setup completed successfully!")
        print("\n📋 Next steps:")
        print("   • Run tests: pytest")
        print("   • Format code: black .")
        print("   • Type check: mypy utm_referrer_parser")
        print("   • View examples: python examples/basic_usage.py")
    else:
        print("❌ Setup encountered issues. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()