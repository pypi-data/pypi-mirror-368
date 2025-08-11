#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for Ethical AI Validator package.

This package provides comprehensive ethical AI validation and auditing capabilities
for bias detection, fairness assessment, and compliance reporting.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    """Read README.md file for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback to ASCII if UTF-8 fails
            with open(readme_path, 'r', encoding='ascii', errors='ignore') as f:
                return f.read()
    return "Ethical AI Validator - Comprehensive AI bias detection and fairness assessment"

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt file."""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except UnicodeDecodeError:
            # Fallback to ASCII if UTF-8 fails
            with open(requirements_path, 'r', encoding='ascii', errors='ignore') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="whis-ethical-ai",
    version="1.3.0",
    author="Ethical AI Team",
    author_email="muhammadabdullahinbox@gmail.com",
    description="Comprehensive ethical AI validation and auditing package",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/whis-19/ethical-ai",
    project_urls={
        "Bug Tracker": "https://github.com/whis-19/ethical-ai/issues",
        "Documentation": "https://whis-19.github.io/ethical-ai/",
        "Source Code": "https://github.com/whis-19/ethical-ai",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=2.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=4.0.0",
            "pytest-cov>=2.0.0",
            "pytest-mock>=2.0.0",
            "black>=19.0.0",
            "flake8>=3.0.0",
            "mypy>=0.700",
            "pre-commit>=1.0.0",
        ],
        "docs": [
            "sphinx>=2.0.0",
            "sphinx-rtd-theme>=0.4.0",
        ],
        "full": [
            "matplotlib>=2.0.0",
            "seaborn>=0.9.0",
            "jupyter>=1.0.0",
            "notebook>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "whis-ethical-ai=ethical_ai_validator.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "ethical-ai",
        "bias-detection",
        "fairness",
        "ai-auditing",
        "gdpr-compliance",
        "ai-act-compliance",
        "machine-learning",
        "artificial-intelligence",
    ],
    platforms=["any"],
    license="MIT",
    license_files=["LICENSE"],
) 