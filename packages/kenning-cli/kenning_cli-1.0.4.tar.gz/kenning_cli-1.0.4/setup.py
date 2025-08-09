#!/usr/bin/env python3
"""
Setup configuration for Kenning CLI.
"""

from setuptools import setup, find_packages

import os

base_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base_dir, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(os.path.join(base_dir, "requirements.txt"), "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="kenning-cli",
    version="1.0.4",
    author="Kenning Project",
    author_email="info@kenningproject.com",
    description="AI-powered contextual risk analysis tool for AWS infrastructure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kenningproject/kenning-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "kenning=cli.main:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
