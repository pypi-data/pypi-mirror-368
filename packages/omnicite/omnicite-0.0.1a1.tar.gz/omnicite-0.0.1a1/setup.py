#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="omnicite",
    version="0.0.1a1",
    author="OmniCite Team",
    author_email="team@omnicite.org",
    description="Universal citation management and academic reference toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/omnicite/omnicite",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Documentation",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "omnicite=omnicite.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
