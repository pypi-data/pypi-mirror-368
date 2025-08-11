#!/usr/bin/env python3
"""
Setup script for LegalVector MCP Server
"""

from setuptools import setup, find_packages
import os

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="legalvector-mcp",
    version="1.0.2",
    author="DocketLabs",
    author_email="contact@docketlabs.com",
    description="Legal technology intelligence MCP server for Claude Desktop - transforms legal tech discovery into strategic AI adoption consulting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/docketlabs/LegalVector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "legalvector-mcp=legalvector_mcp.server:main",
        ],
    },
    keywords="legal-tech ai law-firms mcp-server claude-desktop legal-intelligence business-intelligence",
    project_urls={
        "Bug Reports": "https://github.com/docketlabs/LegalVector/issues",
        "Source": "https://github.com/docketlabs/LegalVector",
        "Documentation": "https://github.com/docketlabs/LegalVector/blob/main/README.md",
    },
    include_package_data=True,
    zip_safe=False,
)