#!/usr/bin/env python3
"""
Setup script for DoorDash MCP Server
"""

from setuptools import setup, find_packages

import os

# Read README if it exists
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "DoorDash MCP Server - An MCP server for DoorDash food ordering"

setup(
    name="doordash-mcp-server",
    version="1.0.0",
    author="DoorDash Automation",
    author_email="support@example.com",
    description="An MCP server for DoorDash food ordering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/doordash-automation/doordash-mcp",
    py_modules=["doordash_mcp_server"],
    install_requires=[
        "mcp>=1.2.0",
        "doordash-rest-client>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "doordash-mcp-server=doordash_mcp_server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    keywords=["mcp", "doordash", "food", "delivery", "ordering", "model-context-protocol"],
)