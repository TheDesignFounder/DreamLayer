#!/usr/bin/env python3
"""
Setup script for DreamLayer CLI
"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dreamlayer-cli",
    version="0.1.0",
    author="DreamLayer AI",
    author_email="",
    description="DreamLayer AI CLI - LoRA merging and utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dreamlayer-ai/DreamLayer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "dreamlayer=dream_layer_backend.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)