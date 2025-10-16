#!/usr/bin/env python3
"""Setup script for jax-agents package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text()
else:
    long_description = "Multi-agent system for converting Fortran CTSM to JAX"

setup(
    name="jax-agents",
    version="0.1.0",
    description="Multi-agent system for converting Fortran CTSM to JAX",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CTSM-JAX Team",
    license="BSD-3-Clause",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "anthropic>=0.40.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "pydantic>=2.0.0",
        "rich>=13.0.0",
        "tenacity>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jax-convert=jax_agents.cli:main",
        ],
    },
    keywords=["ctsm", "jax", "fortran", "translation", "llm", "agents"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

