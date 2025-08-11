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
    "numpy>=1.26.0",
    "scipy>=1.11.0",
    "pandas>=2.1.0",
    "PyPDF2>=3.0.1",
    "pdfplumber>=0.10.0",
    "pymupdf>=1.23.26",
    "pdfminer.six>=20231228",
    "pytesseract>=0.3.10",
    "Pillow>=10.0.0",
    "opencv-python>=4.8.0",
    "transformers>=4.36.0",
    "sentence-transformers>=2.2.2",
    "scikit-learn>=1.3.0",
    "hdbscan>=0.8.33",
    "umap-learn>=0.5.5",
    "openai>=1.6.0",
    "anthropic>=0.8.0",
    "ollama>=0.1.7",
    "pydantic>=2.5.0",
    "tqdm>=4.66.0",
    "click>=8.1.0",
    "rich>=13.7.0",
    "loguru>=0.7.0",
    "pyyaml>=6.0.1",
    "joblib>=1.3.0",
    "requests>=2.31.0",
    "httpx>=0.25.0",
    "typing-extensions>=4.8.0",
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
        "torch>=2.1.0",
        "torchvision>=0.16.0",
    ],
    "performance": [
        "numba>=0.59.1",
        "llvmlite>=0.42.0",
        "faiss-cpu>=1.7.4",
    ],
    "visualization": [
        "matplotlib>=3.8.0",
        "seaborn>=0.13.0",
        "plotly>=5.17.0",
    ],
    "web": [
        "streamlit>=1.29.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
    ],
    "database": [
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.9",
    ],
    "cloud": [
        "boto3>=1.34.0",
        "azure-storage-blob>=12.19.0",
        "google-cloud-storage>=2.10.0",
    ],
    "dev": [
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "pytest-asyncio>=0.21.0",
        "black>=23.11.0",
        "flake8>=6.1.0",
        "mypy>=1.7.0",
        "isort>=5.12.0",
    ],
    "docs": [
        "sphinx>=7.2.0",
        "sphinx-rtd-theme>=1.3.0",
    ],
}

# All optional dependencies (manually curated to avoid conflicts)
optional_requirements["all"] = [
    "zeyrek>=0.1.2",
    "turkish-stemmer>=1.0.0",
    "layoutparser>=0.3.4",
    "detectron2>=0.6; python_version<'3.11'",
    "torch>=2.1.0",
    "torchvision>=0.16.0",
    "numba>=0.59.1",
    "llvmlite>=0.42.0",
    "faiss-cpu>=1.7.4",
    "matplotlib>=3.8.0",
    "seaborn>=0.13.0",
    "plotly>=5.17.0",
    "streamlit>=1.29.0",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "sqlalchemy>=2.0.0",
    "psycopg2-binary>=2.9.9",
    "boto3>=1.34.0",
    "azure-storage-blob>=12.19.0",
    "google-cloud-storage>=2.10.0",
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.11.0",
    "flake8>=6.1.0",
    "mypy>=1.7.0",
    "isort>=5.12.0",
    "sphinx>=7.2.0",
    "sphinx-rtd-theme>=1.3.0",
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