from setuptools import setup, find_packages

setup(
    name="hanzo",
    version="0.3.3",
    description="Hanzo AI - Complete AI Infrastructure Platform with CLI, Router, MCP, and Agent Runtime",
    long_description="""
# Hanzo AI Platform

Complete AI infrastructure platform providing:

- **CLI**: Unified command-line interface for all Hanzo services
- **Router**: Intelligent LLM request routing and load balancing  
- **MCP**: Model Context Protocol server integration
- **Agent Runtime**: Multi-agent orchestration and execution
- **Network**: Distributed AI compute with hanzo-net

## Installation

```bash
pip install hanzo
```

## Quick Start

```bash
# Start Hanzo Network
hanzo net

# Access other Hanzo services
hanzo --help
```

## Features

- Unified CLI for all Hanzo AI services
- Seamless integration with hanzo-net for distributed compute
- Model Context Protocol (MCP) support
- Agent orchestration and management
- LLM routing and optimization

## Documentation

Visit [https://hanzo.ai](https://hanzo.ai) for full documentation.
""",
    long_description_content_type="text/markdown",
    author="Hanzo AI",
    author_email="dev@hanzo.ai",
    url="https://hanzo.ai",
    packages=find_packages(),
    install_requires=[
        "click",
        "hanzo-net>=0.1.15",  # Updated to latest version
        "httpx",
        "prompt-toolkit",
        "pydantic",
        "pyyaml", 
        "rich",
        "typer",
    ],
    entry_points={
        "console_scripts": [
            "hanzo=hanzo.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
)