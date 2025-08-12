#!/usr/bin/env python
"""
Setup script for Enhanced Automatic Shifted Log Transformer
"""

import sys
from pathlib import Path
from setuptools import setup, find_packages

# Ensure minimum Python version
if sys.version_info < (3, 7):
    sys.exit(f"Python 3.7 or higher is required. You are using {sys.version_info.major}.{sys.version_info.minor}")

# Read long description from README
here = Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

# Read version from __init__.py
def get_version():
    version_file = here / "src" / "enhanced_aslt" / "__init__.py"
    if version_file.exists():
        with open(version_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="enhanced-automatic-shifted-log",
    version=get_version(),
    description="Enhanced Automatic Shifted Log Transformer with Monte Carlo optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Muhammad Akmal Husain",
    author_email="akmalhusain2003@gmail.com",
    license="MIT",
    url="https://github.com/AkmalHusain2003/enhanced-automatic-shifted-log",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "scipy>=1.7.0",
        "numba>=0.50.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "pytest-xdist>=2.2",
            "black>=21.0",
            "flake8>=3.9",
            "isort>=5.9",
            "mypy>=0.910",
            "pre-commit>=2.15",
            "jupyter>=1.0.0",
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0"
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "pytest-xdist>=2.2",
            "hypothesis>=6.0"
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "numpydoc>=1.1",
            "myst-parser>=0.15"
        ],
        "examples": [
            "jupyter>=1.0.0",
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0",
            "plotly>=5.0.0"
        ],
        "performance": [
            "numba>=0.56.0",
            "llvmlite>=0.39.0"
        ],
        "all": [
            "pytest>=6.0", "pytest-cov>=2.10", "pytest-xdist>=2.2", "black>=21.0",
            "flake8>=3.9", "isort>=5.9", "mypy>=0.910", "pre-commit>=2.15",
            "jupyter>=1.0.0", "matplotlib>=3.3.0", "seaborn>=0.11.0", "hypothesis>=6.0",
            "sphinx>=4.0", "sphinx-rtd-theme>=1.0", "numpydoc>=1.1", "myst-parser>=0.15",
            "plotly>=5.0.0", "numba>=0.56.0", "llvmlite>=0.39.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "aslt-benchmark=enhanced_aslt.cli:benchmark_command",
            "aslt-validate=enhanced_aslt.cli:validate_command",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
)
