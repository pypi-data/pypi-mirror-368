"""
Setup configuration for opensearch-demos-utils package.

This package provides utilities for OpenSearch demonstrations and educational content,
specifically optimized for Google Colab environments.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    """Read README.md file for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "OpenSearch demonstration utilities for educational and development purposes."

# Read version from __init__.py
def get_version():
    """Extract version from package __init__.py."""
    init_path = os.path.join('opensearch_demos_utils', '__init__.py')
    with open(init_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return "1.0.0"

setup(
    name="opensearch-demos-utils",
    version=get_version(),
    author="OpenSearch Demos Team",
    author_email="support@example.com",
    description="Utilities for OpenSearch demonstrations and educational content",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/opensearch-project/opensearch-demos",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Indexing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opensearch-py>=2.4.0,<3.0.0",
        "pandas>=1.3.0,<3.0.0",
        "matplotlib>=3.5.0,<4.0.0",
        "seaborn>=0.11.0,<1.0.0",
        "numpy>=1.21.0,<2.0.0",
        "requests>=2.25.0,<3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "black>=22.0.0,<24.0.0",
            "flake8>=4.0.0,<7.0.0",
            "mypy>=0.950,<2.0.0",
            "build>=0.8.0,<1.0.0",
            "twine>=4.0.0,<5.0.0",
            "wheel>=0.37.0,<1.0.0",
        ],
        "notebook": [
            "jupyter>=1.0.0,<2.0.0",
            "ipywidgets>=7.6.0,<9.0.0",
            "nbformat>=5.4.0,<6.0.0",
            "nbconvert>=6.5.0,<8.0.0",
        ],
        "colab": [
            # Minimal dependencies for Google Colab environment
            "ipywidgets>=7.6.0,<9.0.0",
        ]
    },
    keywords=[
        "opensearch",
        "elasticsearch", 
        "search",
        "analytics",
        "demos",
        "education",
        "colab",
        "jupyter",
        "astra",
        "datastax"
    ],
    project_urls={
        "Bug Reports": "https://github.com/opensearch-project/opensearch-demos/issues",
        "Source": "https://github.com/opensearch-project/opensearch-demos",
        "Documentation": "https://github.com/opensearch-project/opensearch-demos/blob/main/README.md",
    },
    include_package_data=True,
    zip_safe=False,
)