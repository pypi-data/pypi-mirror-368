#!/usr/bin/env python3
"""Setup script for SmartChunkLLM package."""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Ensure we're using Python 3.8+
if sys.version_info < (3, 8):
    raise RuntimeError("SmartChunkLLM requires Python 3.8 or later")

# Get the long description from README
here = Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8") if (here / "README.md").exists() else ""

# Core requirements (always installed)
core_requirements = [
    "numpy>=1.21.0",
    "scipy>=1.7.0",
    "pandas>=1.3.0",
    "PyPDF2>=3.0.0",
    "pdfplumber>=0.7.0",
    "pymupdf>=1.23.0",
    "pdfminer.six>=20220524",
    "pytesseract>=0.3.10",
    "Pillow>=9.0.0",
    "opencv-python>=4.5.0",
    "transformers>=4.20.0",
    "sentence-transformers>=2.2.0",
    "scikit-learn>=1.1.0",
    "hdbscan>=0.8.28",
    "umap-learn>=0.5.3",
    "openai>=1.0.0",
    "anthropic>=0.7.0",
    "ollama>=0.1.7",
    "pydantic>=2.0.0",
    "tqdm>=4.64.0",
    "click>=8.0.0",
    "rich>=12.0.0",
    "loguru>=0.6.0",
    "pyyaml>=6.0",
    "joblib>=1.1.0",
    "requests>=2.28.0",
    "httpx>=0.24.0",
    "typing-extensions>=4.0.0",
]

# Optional dependencies
optional_requirements = {
    "turkish": [
        "zeyrek>=0.1.2",
        "turkish-stemmer>=1.0.0",
    ],
    "layout": [
        "layoutparser>=0.3.4",
        "detectron2>=0.6; python_version<'3.11'",
        "torch>=1.12.0",
        "torchvision>=0.13.0",
    ],
    "performance": [
        "numba>=0.58.0",
        "faiss-cpu>=1.7.0",
    ],
    "visualization": [
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
    ],
    "web": [
        "streamlit>=1.20.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.20.0",
    ],
    "database": [
        "sqlalchemy>=1.4.0",
        "psycopg2-binary>=2.9.0",
    ],
    "cloud": [
        "boto3>=1.26.0",
        "azure-storage-blob>=12.14.0",
        "google-cloud-storage>=2.7.0",
    ],
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-asyncio>=0.20.0",
        "black>=22.0.0",
        "flake8>=5.0.0",
        "mypy>=0.991",
        "isort>=5.10.0",
    ],
    "docs": [
        "sphinx>=5.0.0",
        "sphinx-rtd-theme>=1.0.0",
    ],
}

# All optional dependencies (manually curated to avoid conflicts)
optional_requirements["all"] = [
    "zeyrek>=0.1.2",
    "turkish-stemmer>=1.0.0",
    "layoutparser>=0.3.4",
    "detectron2>=0.6; python_version<'3.11'",
    "torch>=1.12.0",
    "torchvision>=0.13.0",
    "numba>=0.58.0",
    "faiss-cpu>=1.7.0",
    "matplotlib>=3.5.0",
    "seaborn>=0.11.0",
    "plotly>=5.0.0",
    "streamlit>=1.20.0",
    "fastapi>=0.95.0",
    "uvicorn>=0.20.0",
    "sqlalchemy>=1.4.0",
    "psycopg2-binary>=2.9.0",
    "boto3>=1.26.0",
    "azure-storage-blob>=12.14.0",
    "google-cloud-storage>=2.7.0",
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.20.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=0.991",
    "isort>=5.10.0",
    "sphinx>=5.0.0",
    "sphinx-rtd-theme>=1.0.0",
]

# Get version from package
def get_version():
    """Get version from package __init__.py"""
    version_file = here / "smartchunkllm" / "__init__.py"
    if version_file.exists():
        with open(version_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"').strip("'")
    return "1.0.0"

setup(
    name="smartchunkllm",
    version=get_version(),
    description="Advanced Legal Document Semantic Chunking System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="SmartChunkLLM Team",
    author_email="info@smartchunkllm.com",
    url="https://github.com/smartchunkllm/smartchunkllm",
    project_urls={
        "Bug Reports": "https://github.com/smartchunkllm/smartchunkllm/issues",
        "Source": "https://github.com/smartchunkllm/smartchunkllm",
        "Documentation": "https://smartchunkllm.readthedocs.io/",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    python_requires=">=3.8",
    install_requires=core_requirements,
    extras_require=optional_requirements,
    entry_points={
        "console_scripts": [
            "smartchunk=smartchunkllm.cli:main",
            "smartchunkllm=smartchunkllm.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "legal", "documents", "semantic", "chunking", "nlp", 
        "ai", "llm", "pdf", "turkish", "law", "embedding", 
        "clustering", "transformers", "ollama", "openai", "anthropic"
    ],
    include_package_data=True,
    package_data={
        "smartchunkllm": [
            "data/*.json",
            "data/*.yaml",
            "data/*.txt",
            "templates/*.txt",
            "templates/*.json",
            "config/*.yaml",
            "config/*.json",
        ],
    },
    zip_safe=False,
    platforms=["any"],
    license="MIT",
    download_url="https://github.com/smartchunkllm/smartchunkllm/archive/v1.0.0.tar.gz",
    maintainer="SmartChunkLLM Team",
    maintainer_email="info@smartchunkllm.com",
)