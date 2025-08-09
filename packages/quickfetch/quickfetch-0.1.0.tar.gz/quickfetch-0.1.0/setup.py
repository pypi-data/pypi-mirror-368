#!/usr/bin/env python3
"""
Setup script for qfetch package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="quickfetch",
    version="0.1.0",
    author="quickfetch",
    author_email="quickfetch@example.com",
    description="Fast, simple, and beautifully minimal web scraping",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/quickfetch/quickfetch",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "selectolax>=0.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    keywords="web scraping, http, html, json, requests, beautifulsoup, lxml",
    project_urls={
        "Bug Reports": "https://github.com/quickfetch/quickfetch/issues",
        "Source": "https://github.com/quickfetch/quickfetch",
        "Documentation": "https://github.com/quickfetch/quickfetch#readme",
    },
)
