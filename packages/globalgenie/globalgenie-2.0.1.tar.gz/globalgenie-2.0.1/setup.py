#!/usr/bin/env python3
"""
GlobalGenie Setup Configuration
Professional PyPI distribution setup for GlobalGenie AI Agent Framework
"""

from setuptools import setup, find_packages
import os
import sys
from pathlib import Path

# Ensure we're in the right directory
if __name__ == "__main__":
    here = Path(__file__).parent.resolve()
    os.chdir(here)

# Read the contents of README file
def read_file(filename):
    """Read file contents safely"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# Get long description from README
long_description = read_file("README.md")
if not long_description:
    # Fallback to main README if local one doesn't exist
    try:
        main_readme = Path("../../README.md")
        if main_readme.exists():
            long_description = main_readme.read_text(encoding="utf-8")
    except:
        long_description = "GlobalGenie: The Complete AI Agent Framework for building intelligent, autonomous agents with memory, reasoning, and multi-modal capabilities."

# Version information
VERSION = "1.0.0"

# Core dependencies with version constraints for stability
CORE_DEPENDENCIES = [
    "docstring-parser>=0.15",
    "gitpython>=3.1.0",
    "httpx>=0.24.0",
    "pydantic>=2.0.0,<3.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "python-multipart>=0.0.6",
    "pyyaml>=6.0",
    "rich>=13.0.0",
    "tomli>=2.0.0;python_version<'3.11'",
    "typer>=0.9.0",
    "typing-extensions>=4.5.0",
]

# Development dependencies
DEV_DEPENDENCIES = [
    "mypy>=1.5.0",
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.0",
    "ruff>=0.0.280",
    "timeout-decorator>=0.5.0",
    "types-pyyaml>=6.0.0",
    "types-aiofiles>=23.0.0",
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
    "arxiv>=1.4.0"
]

# Extended classifiers for better discoverability
CLASSIFIERS = [
    # Development Status
    "Development Status :: 5 - Production/Stable",
    
    # Intended Audience
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Information Technology",
    "Intended Audience :: System Administrators",
    
    # License
    "License :: OSI Approved :: MIT License",
    
    # Programming Language
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3 :: Only",
    
    # Operating System
    "Operating System :: OS Independent",
    "Operating System :: POSIX",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS",
    
    # Topic
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
    "Topic :: Communications :: Chat",
    "Topic :: System :: Distributed Computing",
    "Topic :: Database",
    
    # Environment
    "Environment :: Console",
    "Environment :: Web Environment",
    "Environment :: No Input/Output (Daemon)",
    
    # Framework
    "Framework :: AsyncIO",
    
    # Natural Language
    "Natural Language :: English",
    
    # Typing
    "Typing :: Typed"
]

# Keywords for better discoverability
KEYWORDS = [
    # Core AI/ML terms
    "ai", "artificial-intelligence", "machine-learning", "deep-learning",
    "llm", "large-language-model", "nlp", "natural-language-processing",
    
    # Agent-specific terms
    "ai-agent", "autonomous-agents", "multi-agent-system", "intelligent-agents",
    "agent-framework", "reasoning-agents", "cognitive-agents",
    
    # Capabilities
    "reasoning", "memory", "knowledge-base", "rag", "retrieval-augmented-generation",
    "multi-modal", "tool-integration", "automation", "workflow",
    
    # Technical terms
    "framework", "library", "python", "async", "asyncio",
    "api", "rest-api", "microservices", "distributed-systems",
    
    # Model providers
    "openai", "anthropic", "google", "claude", "gpt", "gemini",
    "bedrock", "azure", "huggingface", "ollama", "groq",
    
    # Use cases
    "chatbot", "conversational-ai", "virtual-assistant", "automation",
    "data-analysis", "research", "content-generation", "code-generation",
    
    # Storage and databases
    "vector-database", "embeddings", "chromadb", "pinecone", "qdrant",
    "postgresql", "sqlite", "redis", "mongodb",
    
    # Integration
    "tools", "plugins", "extensions", "integrations", "apis"
]

# Project URLs for comprehensive linking
PROJECT_URLS = {
    "Homepage": "https://github.com/RahulEdward/global-genie",
    "Documentation": "https://github.com/RahulEdward/global-genie/wiki",
    "Repository": "https://github.com/RahulEdward/global-genie",
    "Bug Reports": "https://github.com/RahulEdward/global-genie/issues",
    "Feature Requests": "https://github.com/RahulEdward/global-genie/discussions",
    "Changelog": "https://github.com/RahulEdward/global-genie/releases",
    "Support": "https://github.com/RahulEdward/global-genie/discussions",
    "Source": "https://github.com/RahulEdward/global-genie",
    "Tracker": "https://github.com/RahulEdward/global-genie/issues"
}

if __name__ == "__main__":
    setup(
        # Basic package information
        name="globalgenie",
        version=VERSION,
        description="GlobalGenie: The Complete AI Agent Framework for building intelligent, autonomous agents with memory, reasoning, and multi-modal capabilities",
        long_description=long_description,
        long_description_content_type="text/markdown",
        
        # Author information
        author="GlobalGenie Team",
        author_email="team@globalgenie.com",
        maintainer="GlobalGenie Team",
        maintainer_email="team@globalgenie.com",
        
        # URLs and links
        url="https://github.com/RahulEdward/global-genie",
        project_urls=PROJECT_URLS,
        
        # Package discovery
        packages=find_packages(include=["globalgenie", "globalgenie.*"]),
        package_data={
            "globalgenie": ["py.typed", "*.json", "*.yaml", "*.yml", "*.toml"],
        },
        include_package_data=True,
        
        # Dependencies
        install_requires=CORE_DEPENDENCIES,
        extras_require={
            "dev": DEV_DEPENDENCIES,
        },
        
        # Python version requirements
        python_requires=">=3.8,<4",
        
        # Classification
        classifiers=CLASSIFIERS,
        keywords=KEYWORDS,
        
        # License
        license="MIT",
        license_files=["LICENSE"],
        
        # Entry points for CLI
        entry_points={
            "console_scripts": [
                "gg=globalgenie.cli.entrypoint:globalgenie_cli",
                "globalgenie=globalgenie.cli.entrypoint:globalgenie_cli",
            ],
        },
        
        # Additional metadata
        zip_safe=False,
        platforms=["any"],
        
        # Version is handled manually
        # use_scm_version=False,  # Removed to avoid warning
        
        # Ensure wheel compatibility
        options={
            "bdist_wheel": {
                "universal": False,
            }
        },
    )