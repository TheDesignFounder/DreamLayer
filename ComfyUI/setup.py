#!/usr/bin/env python3
"""
Setup script for ComfyUI
"""

from setuptools import setup, find_packages

setup(
    name="comfyui",
    version="0.1.0",
    author="ComfyUI",
    description="ComfyUI - A powerful and modular stable diffusion GUI",
    packages=find_packages(),
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
)
