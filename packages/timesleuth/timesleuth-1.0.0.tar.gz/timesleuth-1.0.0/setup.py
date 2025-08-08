#!/usr/bin/env python3
"""
Setup script for TimeSleuth - Digital Forensics Timestamp Analysis Library
"""

from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "TimeSleuth - Digital forensics timestamp analysis library"

setup(
    name="timesleuth",
    version="1.0.0",
    author="Mohammad Nazmul",
    author_email="mohammadnazmuldev@gmail.com",
    description="Digital forensics timestamp analysis library for detecting suspicious activity",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MohammadNazmulDev/TimeSleuth",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: System :: Filesystems",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[],
    keywords="forensics digital-forensics timestamp security incident-response malware-analysis cybersecurity",
    project_urls={
        "Bug Reports": "https://github.com/MohammadNazmulDev/TimeSleuth/issues",
        "Source Code": "https://github.com/MohammadNazmulDev/TimeSleuth",
        "Documentation": "https://github.com/MohammadNazmulDev/TimeSleuth#readme",
    },
)