"""
Setup configuration for pipecat-tools library.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="spacestep-tools",
    version="0.1.5",
    author="Your Name",
    author_email="your.email@example.com",
    description="A flexible toolkit for managing Pipecat function tools with OpenAI-style metadata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="",  # No repository URL
    packages=find_packages(),
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.991",
        ],
    },
    package_data={
        "pipecat_tools": ["*.yaml", "*.yml"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "spacestep-tools=pipecat_tools.cli:main",
        ],
    },
) 