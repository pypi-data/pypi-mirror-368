#!/usr/bin/env python3
"""
Setup script for building DisjointForest Python bindings
"""

from setuptools import setup, Extension, find_packages
import pybind11
from pybind11 import get_cmake_dir
import pybind11.commands
import sys
import os

# Read the README for long description
with open("../README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="disjoint-forest",
    version="1.0.0",
    author="DisjointForest Contributors",
    author_email="",
    description="A high-performance C++ implementation of disjoint-set data structure with Python bindings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/disjoint-forest",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/disjoint-forest/issues",
        "Source Code": "https://github.com/yourusername/disjoint-forest",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: C++",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: Utilities",
    ],
    package_dir={"": "."},
    packages=find_packages(where="."),
    python_requires=">=3.8",
    ext_modules=[
        Extension(
            "disjoint_forest.disjoint_forest",
            ["disjoint_forest_bindings.cc"],
            include_dirs=[
                pybind11.get_include(),
                "..",
            ],
            language="c++",
            extra_compile_args=["-std=c++17"],
        ),
    ],
    zip_safe=False,

    keywords="disjoint-set, union-find, data-structure, algorithm, graph, optimization",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
) 