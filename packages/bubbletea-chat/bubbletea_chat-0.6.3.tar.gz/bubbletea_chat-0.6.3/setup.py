"""
Setup script for BubbleTea Python SDK (Minimal Version)
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bubbletea",
    version="0.1.0",
    author="BubbleTea Team",
    author_email="team@bubbletea.dev",
    description="A Python package for building AI chatbots for BubbleTea platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bubbletea/bubbletea-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "pydantic>=2.0.0",
    ],
)