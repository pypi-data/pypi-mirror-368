#!/usr/bin/env python3
"""
Setup script for the imagenet-classes package.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt if it exists
def read_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return requirements

setup(
    name="imagenet-classes",
    author="Illia Volkov, Nikita Kisel",
    author_email="kiselnik@fel.cvut.cz",  # Primary contact
    description="A Python package for managing and retrieving ImageNet-1k mappings among integer class IDs, string class IDs, and human-readable class names.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/gonikisgo/imagenet-classes",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19.0",
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
    include_package_data=True,
    package_data={
        "class_mapping": [
            "*.npy",
        ],
    },
    zip_safe=False,
    keywords="imagenet, computer-vision, machine-learning, deep-learning, classification",
    project_urls={
        "Bug Reports": "https://github.com/gonikisgo/imagenet-classes/issues",
        "Source": "https://github.com/gonikisgo/imagenet-classes",
        "Documentation": "https://github.com/gonikisgo/imagenet-classes#readme",
    },
)
