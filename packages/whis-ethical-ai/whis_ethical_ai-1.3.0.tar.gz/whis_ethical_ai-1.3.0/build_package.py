#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build script for Ethical AI Validator package.

This script helps build and test the pip package locally.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print("{}...".format(description))
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ {}".format(description))
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("❌ {} failed: {}".format(description, e.stderr))
        return None

def clean_build():
    """Clean previous build artifacts."""
    print("🧹 Cleaning build artifacts...")
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print("   Removed {}".format(dir_name))
    print("✅ Build artifacts cleaned")

def build_package():
    """Build the package."""
    print("🔨 Building Ethical AI Validator package...")
    
    # Clean previous builds
    clean_build()
    
    # Build the package
    result = run_command("python setup.py sdist bdist_wheel", "Building package")
    if result is None:
        return False
    
    print("✅ Package built successfully!")
    return True

def test_installation():
    """Test installing the package locally."""
    print("🧪 Testing package installation...")
    
    # Install in development mode
    result = run_command("pip install -e .", "Installing package in development mode")
    if result is None:
        return False
    
    # Test import
    try:
        import ethical_ai_validator
        print("✅ Package imports successfully!")
        print("   Version: {}".format(ethical_ai_validator.__version__))
        return True
    except ImportError as e:
        print("❌ Package import failed: {}".format(e))
        return False

def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    result = run_command("python -m pytest tests/ -v", "Running test suite")
    if result is None:
        return False
    
    print("✅ Tests completed!")
    return True

def create_distribution():
    """Create distribution files."""
    print("📦 Creating distribution...")
    
    # Build source distribution
    result = run_command("python setup.py sdist", "Creating source distribution")
    if result is None:
        return False
    
    # Build wheel
    result = run_command("python setup.py bdist_wheel", "Creating wheel distribution")
    if result is None:
        return False
    
    print("✅ Distribution files created!")
    return True

def main():
    """Main build process."""
    print("🚀 Ethical AI Validator Package Builder")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info[0] != 2:
        print("⚠️  Warning: This package is designed for Python 2.x")
        print("   Current Python version: {}".format(sys.version))
    
    # Build steps
    steps = [
        ("Clean build artifacts", clean_build),
        ("Build package", build_package),
        ("Test installation", test_installation),
        ("Run tests", run_tests),
        ("Create distribution", create_distribution),
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print("\n" + "=" * 50)
        print("Step: {}".format(step_name))
        print("=" * 50)
        
        if step_func():
            success_count += 1
        else:
            print("❌ Step '{}' failed!".format(step_name))
            break
    
    print("\n" + "=" * 50)
    print("Build Summary")
    print("=" * 50)
    print("✅ Successful steps: {}/{}".format(success_count, len(steps)))
    
    if success_count == len(steps):
        print("🎉 Package build completed successfully!")
        print("\nNext steps:")
        print("1. Test the package: pip install -e .")
        print("2. Run example: python examples/basic_usage.py")
        print("3. Upload to PyPI: python -m twine upload dist/*")
    else:
        print("❌ Build failed at step {}".format(success_count + 1))

if __name__ == "__main__":
    main() 