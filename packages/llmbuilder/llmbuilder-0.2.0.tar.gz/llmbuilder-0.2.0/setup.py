"""
Setup configuration for LLMBuilder package.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as fh:
            return fh.read()
    return "A comprehensive toolkit for building, training, and deploying language models."

# Read version from the package
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "llmbuilder", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="llmbuilder",
    version=get_version(),
    author="Qubase",
    author_email="contact@qubase.in",
    description="A comprehensive toolkit for building, training, and deploying language models",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/qubasehq/llmbuilder-package",
    packages=find_packages(),
    package_data={
        'llmbuilder': [
            'config/defaults/*.json',
            'templates/*',
        ],
    },
    install_requires=[
        # Core ML dependencies
        "torch>=2.0.0,<3.0.0",
        "transformers>=4.30.0,<5.0.0", 
        "tokenizers>=0.13.0,<1.0.0",
        "sentencepiece>=0.1.99,<1.0.0",
        
        # Data processing
        "pandas>=2.0.0,<3.0.0",
        "numpy>=1.24.0,<2.0.0",
        "PyMuPDF>=1.23.0,<2.0.0",  # fitz for PDF processing
        "docx2txt>=0.8,<1.0.0",
        "python-pptx>=0.6.21,<1.0.0",
        "markdown>=3.4.0,<4.0.0",
        "beautifulsoup4>=4.12.0,<5.0.0",
        
        # Utilities
        "tqdm>=4.65.0,<5.0.0",
        "PyYAML>=6.0,<7.0.0",
        "loguru>=0.7.0,<1.0.0",
        
        # CLI support
        "click>=8.0.0,<9.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "gpu": [
            # GPU-specific dependencies can be installed separately
            # Users can install with: pip install llmbuilder[gpu]
        ],
        "export": [
            # Additional dependencies for model export
            "onnx>=1.14.0",
            "onnxruntime>=1.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llmbuilder=llmbuilder.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    keywords="llm, language model, transformer, training, fine-tuning, nlp, ai, machine learning",
    project_urls={
        "Bug Reports": "https://github.com/qubasehq/llmbuilder-package/issues",
        "Source": "https://github.com/qubasehq/llmbuilder-package",
        "Documentation": "https://github.com/qubasehq/llmbuilder-package/wiki",
    },
)