#!/usr/bin/env python3
"""
System Monitor MCP Server 安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="system-monitor-mcp",
    version="1.0.0",
    author="undoom",
    author_email="kaikaihuhu666@163.com",
    description="System monitoring and performance analysis MCP server based on PyQt5 monitoring program",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/undoom/system-monitor-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "gpu": ["GPUtil>=1.4.0"],
        "dev": ["pytest>=6.0", "pytest-asyncio>=0.18.0"],
    },
    entry_points={
        "console_scripts": [
            "system-monitor-mcp=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt"],
    },
)
