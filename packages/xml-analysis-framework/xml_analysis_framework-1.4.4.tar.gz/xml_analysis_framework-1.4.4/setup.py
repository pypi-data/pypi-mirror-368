#!/usr/bin/env python3
"""
Setup script for XML Analysis Framework
"""

from setuptools import setup
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="xml-analysis-framework",
    version="1.4.4",
    author="Wes Jackson",
    author_email="wjackson@redhat.com",
    description="XML document analysis and preprocessing framework designed for AI/ML data pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/redhat-ai-americas/xml-analysis-framework",
    project_urls={
        "Bug Reports": "https://github.com/redhat-ai-americas/xml-analysis-framework/issues",
        "Source": "https://github.com/redhat-ai-americas/xml-analysis-framework",
        "Documentation": "https://github.com/redhat-ai-americas/xml-analysis-framework/blob/main/README.md",
    },
    packages=[
        "xml_analysis_framework",
        "xml_analysis_framework.core", 
        "xml_analysis_framework.handlers",
        "xml_analysis_framework.utils"
    ],
    package_dir={"xml_analysis_framework": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: XML",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "defusedxml>=0.7.1",  # For secure XML parsing
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=3.0",
            "sphinx_rtd_theme>=0.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "xml-analyze=src.examples.basic_analysis:main",
            "xml-analyze-enhanced=src.examples.enhanced_analysis:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)