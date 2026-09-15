#!/usr/bin/env python3
"""
setup.py for OmniAudit-GEO.
Supports editable installation via: pip install -e .
Provides console commands: `omniaudit` and `omni`
"""

from pathlib import Path

from setuptools import setup

REPO_ROOT = Path(__file__).resolve().parent
long_description = (REPO_ROOT / "README.md").read_text(encoding="utf-8") if (REPO_ROOT / "README.md").exists() else ""

setup(
    name="omniaudit-geo",
    version="1.0.0",
    description="Enterprise Brand AI-Readiness, GEO/AEO Audit Marketplace & Anthropic MCP Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Shaswat Raj & Prithvi",
    author_email="shaswatraj3@gmail.com",
    url="https://github.com/SH20RAJ/omniaudit",
    py_modules=["cli", "app"],
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "web": [
            "fastapi>=0.115.0",
            "uvicorn>=0.30.0",
            "streamlit>=1.38.0",
            "httpx>=0.27.0",
            "pydantic>=2.7.0",
        ],
        "dev": [
            "fastapi>=0.115.0",
            "uvicorn>=0.30.0",
            "streamlit>=1.38.0",
            "httpx>=0.27.0",
            "pydantic>=2.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "omniaudit=cli:main",
            "omni=cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
